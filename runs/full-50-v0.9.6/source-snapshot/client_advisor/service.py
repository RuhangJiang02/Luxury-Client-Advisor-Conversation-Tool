"""Shared generation service for Streamlit and batch callers."""

import hashlib
import json
import sqlite3
import time
from datetime import datetime
from uuid import uuid4

from . import TOOL_VERSION, PROMPT_VERSION
from .config import Config
from .context import RULES_HASH, CATALOGUE_HASH, resolved_products
from .contracts import validate_request, SCENARIOS
from .llm import OpenAIAdapter, OllamaAdapter, ProviderError
from .output_checks import parse_output, quality_flags
from .prompts import build_messages
from .rules import preflight
from .run_store import RunStore
from .grounding import grounding_context, check_grounding
from .event_composition import compose_event
from .greeting_composition import compose_greeting
from .recommendation_composition import compose_recommendation


def now():
    return datetime.now().astimezone().isoformat()


class GenerationService:
    def __init__(self, config=None, adapter=None, store=None):
        self.config = config or Config.load()
        self.adapter = adapter or (OllamaAdapter(self.config) if self.config.provider == "ollama" else OpenAIAdapter(self.config))
        self.store = store or RunStore()

    def generate(self, request):
        request = json.loads(json.dumps(request))
        request_id = request.get("request_id") if isinstance(request, dict) else None
        case_id = request.get("case_id") if isinstance(request, dict) else None
        scenario = request.get("scenario") if isinstance(request, dict) else None
        if not isinstance(request_id, str) or not request_id.strip():
            request_id = None
        key = request_id or "invalid-" + str(uuid4())
        run_id = str(uuid4())
        response = {"contract_version": "io-v0.1", "request_id": request_id, "case_id": case_id if isinstance(case_id, str) else None, "scenario": scenario if scenario in SCENARIOS else None, "status": "generation_failed", "candidates": [], "notices": [], "clarifications": [], "metadata": {"run_id": run_id, "brand_version": "brand-v0.1", "catalogue_version": "brand-v0.1", "tool_version": TOOL_VERSION, "prompt_version": PROMPT_VERSION, "model_id": None, "started_at": now(), "finished_at": None, "generation_attempts": 0, "resolved_product_ids": []}}
        identity_data = {"request": request, "config": self.config.public(), "tool": TOOL_VERSION, "prompt": PROMPT_VERSION, "rules_hash": RULES_HASH, "catalogue_hash": CATALOGUE_HASH, "execution_kind": "live" if self.adapter.is_live else "test_double"}
        identity = hashlib.sha256(json.dumps(identity_data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        artifact = {**identity_data, "identity": identity, "request_id": request_id, "resolved_products": [], "attempts": [], "response": response}

        def fail(status, code, field, message):
            response["status"] = status
            response["notices"].append({"code": code, "field": field, "message": message})
            if status == "needs_clarification":
                response["clarifications"].append({"field": field or "$", "question": message})

        try:
            state, cached = self.store.reserve(key, identity, run_id)
            if state == "cached":
                return cached
            if state != "new":
                fail("invalid_input" if state == "conflict" else "generation_failed", "REQUEST_ID_CONFLICT" if state == "conflict" else "REQUEST_IN_PROGRESS", "request_id", "请求标识已被其他输入使用，或仍在处理中。请勿重复执行；有意重试请使用新标识。")
                response["metadata"]["finished_at"] = now()
                self.store.event(key, artifact)
                return artifact
        except sqlite3.Error:
            fail("generation_failed", "RUN_STORE_ERROR", None, "无法预留运行记录，未调用模型。")
            response["metadata"]["finished_at"] = now()
            return artifact
        errors = validate_request(request)
        if errors:
            fail("invalid_input", "INPUT_INVALID", errors[0]["field"], errors[0]["message"])
        else:
            decision, derived, notices = preflight(request)
            response["notices"].extend(notices)
            if decision:
                fail(decision["status"], decision["code"], decision["field"], decision["message"])
            else:
                derived["writing_constraints"] = grounding_context(request)
                products = resolved_products(derived["eligible_product_ids"])
                artifact["resolved_products"] = products
                artifact["derived_context"] = derived
                response["metadata"]["resolved_product_ids"] = [p["product_id"] for p in products]
                if not self.adapter.available:
                    fail("generation_failed", "CONFIG_MISSING", None, "请在服务器环境变量或项目 .env 中配置 OPENAI_API_KEY。")
                else:
                    response["metadata"]["model_id"] = self.config.model
                    feedback = None
                    previous_output = None
                    for index in range(self.config.max_attempts):
                        attempt = {"number": index + 1, "started_at": now()}
                        artifact["attempts"].append(attempt)
                        messages = build_messages(request, derived, feedback, local=self.config.provider == "ollama", previous_output=previous_output)
                        attempt["messages"] = messages
                        if self.config.provider == "ollama":
                            from .reference_drafts import references
                            attempt["editorial_reference"] = {"method": "evidence-bound-reference-edit-v0.1", "program_authored_references": references(request, derived), "source_fields": ["request.client", "request.scenario_context", "request.conversation_history", "resolved_products", "derived_context.assessment_eligible"], "references_are_model_authored": False, "provider_failure_fallback": False}
                        response["metadata"]["generation_attempts"] += 1
                        started = time.monotonic()
                        try:
                            provider = self.adapter.complete(messages)
                            attempt.update(provider)
                            parsed, errors = parse_output(provider["content"])
                            if parsed and not errors and self.config.provider == "ollama" and request["scenario"] == "event_invitation":
                                parsed, composition, composition_errors = compose_event(parsed, request)
                                errors.extend(composition_errors)
                                if composition:
                                    attempt["structured_composition"] = composition
                            if parsed and not errors and self.config.provider == "ollama" and request["scenario"] == "greeting":
                                parsed, composition, composition_errors = compose_greeting(parsed, request)
                                errors.extend(composition_errors)
                                if composition:
                                    attempt["structured_composition"] = composition
                            if parsed and not errors and self.config.provider == "ollama" and request["scenario"] == "product_recommendation":
                                parsed, composition, composition_errors = compose_recommendation(parsed, request, derived)
                                errors.extend(composition_errors)
                                if composition:
                                    attempt["structured_composition"] = composition
                            if parsed and not errors:
                                grounding_errors, diversity = check_grounding(parsed, request)
                                errors.extend(grounding_errors)
                                attempt["diversity_checks"] = diversity
                            if provider.get("finish_reason") not in {None, "stop"}:
                                errors.append("HF-01: incomplete or refused model response")
                            attempt["validation_errors"] = errors
                            if not errors:
                                if parsed["status"] == "generated":
                                    response["status"] = "generated"
                                    response["candidates"] = [{"candidate_id": i, "text": t} for i, t in enumerate(parsed["messages"], 1)]
                                    response["notices"].extend(quality_flags(parsed["messages"]))
                                else:
                                    fail(parsed["status"], "MODEL_CLARIFICATION" if parsed["status"] == "needs_clarification" else "MODEL_CONTACT_BLOCK", None, parsed["reason"])
                                break
                            feedback = errors
                            previous_output = provider["content"]
                            if index + 1 == self.config.max_attempts:
                                fail("generation_failed", "OUTPUT_REJECTED", None, "模型输出未通过检查，已停止重试。")
                        except ProviderError as exc:
                            attempt["error_code"] = exc.code
                            if not exc.retryable or index + 1 == self.config.max_attempts:
                                fail("generation_failed", "CONFIG_MISSING" if exc.code == "CONFIG_MISSING" else "MODEL_ERROR", None, f"模型调用失败（{exc.code}），没有使用模板替代。")
                                break
                        finally:
                            attempt["finished_at"] = now()
                            attempt["elapsed_seconds"] = round(time.monotonic() - started, 4)
                        time.sleep(.2)
        response["metadata"]["finished_at"] = now()
        try:
            self.store.finish(key, artifact)
        except sqlite3.Error:
            response["candidates"] = []
            response["clarifications"] = []
            fail("generation_failed", "RUN_STORE_ERROR", None, "模型结果未能可靠保存，请检查本地运行存储。")
        return artifact
