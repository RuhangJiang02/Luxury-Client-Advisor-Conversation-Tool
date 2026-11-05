"""Offline UI preview only. Hand-written templates, not an LLM integration.

This deliberately does not implement the full io-v0.1 business validator.
The UI and any future callers can invoke preview() without importing Streamlit.
"""

from datetime import datetime
from uuid import uuid4

from client_advisor.context import PRODUCTS


def preview(request):
    """Return clearly labelled template output and basic preview-only checks."""
    scenario = request["scenario"]
    now = datetime.now().astimezone().isoformat()
    result = {
        "contract_version": "io-v0.1", "request_id": request["request_id"],
        "case_id": request.get("case_id"), "scenario": scenario,
        "status": "generated", "candidates": [], "notices": [], "clarifications": [],
        "metadata": {
            "run_id": str(uuid4()), "brand_version": "brand-v0.1",
            "catalogue_version": "brand-v0.1", "tool_version": "ui-preview-v0.1",
            "prompt_version": None, "model_id": None,
            "started_at": now, "finished_at": now, "generation_attempts": 0,
            "resolved_product_ids": request["product_ids"],
        },
        "preview_only": True,
    }

    def stop(status, code, field, message):
        result["status"] = status
        result["notices"] = [{"code": code, "field": field, "message": message}]
        if status == "needs_clarification":
            result["clarifications"] = [{"field": field, "question": message}]
        return result

    contact = request["client"]["contact_preferences"]
    if request["interaction"]["mode"] == "proactive":
        if contact["proactive_status"] == "opted_out" or scenario in contact["restricted_scenarios"]:
            return stop("blocked", "CONTACT_RESTRICTED", "client.contact_preferences", "客户限制了此类主动联系，未生成外发文案。")
        if contact["proactive_status"] == "unknown":
            return stop("needs_clarification", "CONTACT_PERMISSION_UNKNOWN", "client.contact_preferences", "请先确认客户是否允许主动联系。")
    ctx = request["scenario_context"]
    address = request["client"].get("preferred_address") or ""
    hello = f"{address}，" if address else ""
    product = PRODUCTS.get(next(iter(request["product_ids"]), ""))
    if scenario in {"product_recommendation", "post_purchase_care", "price_objection"} and product is None:
        return stop("needs_clarification", "PRODUCT_UNRESOLVED", "product_ids", "请选择一款目录内产品。")
    if scenario == "greeting":
        if ctx["occasion_type"] == "festival" and not ctx["occasion_name"]:
            return stop("needs_clarification", "ESSENTIAL_FACT_MISSING", "scenario_context.occasion_name", "请填写节日名称。")
        occasion = "生日" if ctx["occasion_type"] == "birthday" else ctx["occasion_name"]
        texts = [f"{hello}{occasion}快乐。愿您自在从容，日常里常有值得期待的小欢喜。", f"{hello}送上一份{occasion}祝福。愿您忙碌之余，也有属于自己的轻松时光。", f"{hello}祝您{occasion}快乐。愿生活有喜欢的风景，也有从容享受的好心情。"]
    elif scenario == "product_recommendation":
        budget = request["client"].get("budget")
        if budget and product["price"] > budget["max_amount"]:
            return stop("needs_clarification", "NO_PRODUCT_FIT", "product_ids", "所选产品超过已填写的预算，请调整候选产品。")
        texts = [f"{hello}想请您看看{product['name']}，采用{product['detail']}。如果您愿意，我可以再为您介绍细节。", f"{hello}{product['name']}的目录价格是 ¥{product['price']:,}。您更在意携带方式还是收纳需求？我可以据此为您说明。", f"{hello}这里有一款{product['name']}供您参考，目录配色包括{'、'.join(product['colors'])}。您可以慢慢看看，有想了解的细节再告诉我。"]
    elif scenario == "post_purchase_care":
        texts = [f"{hello}想问问您这只{product['name']}用得是否顺手。如果有想了解的养护细节，随时告诉我。", f"{hello}关于{product['name']}的日常养护，可以用干净柔软的干布轻拭，并避免接触水、油和香水。", f"{hello}您的{product['name']}暂时不用时，可以保持干燥，放入随附的防尘袋。若有具体使用问题，我可以协助您进一步了解。"]
    elif scenario == "reactivation":
        texts = [f"{hello}想向您问声好。最近如果有想了解的皮具款式，您方便时可以随时告诉我。", f"{hello}希望您近来一切顺心。如果您对颜色或携带方式有了新的偏好，我很愿意听听。", f"{hello}给您留一句问候。您之后有选包或养护方面的问题，方便时联系我就好。"]
    elif scenario == "event_invitation":
        if ctx["eligibility"] == "ineligible":
            return stop("blocked", "EVENT_INELIGIBLE", "scenario_context.eligibility", "当前客户不符合此活动的参与条件。")
        if ctx["eligibility"] != "eligible" or not all(ctx.get(k) for k in ["title", "venue", "starts_at", "ends_at", "rsvp_method"]):
            return stop("needs_clarification", "ESSENTIAL_FACT_MISSING", "scenario_context", "请确认活动资格、名称、时间、地点及回复方式。")
        start = datetime.fromisoformat(ctx["starts_at"])
        end = datetime.fromisoformat(ctx["ends_at"])
        ref = datetime.fromisoformat(request["reference_time"])
        if end <= start or start <= ref:
            return stop("needs_clarification", "ESSENTIAL_FACT_MISSING", "scenario_context.starts_at", "请提供尚未开始、起止时间有效的活动。")
        deadline = ctx.get("rsvp_deadline")
        if deadline and datetime.fromisoformat(deadline) <= ref:
            return stop("needs_clarification", "ESSENTIAL_FACT_MISSING", "scenario_context.rsvp_deadline", "活动报名已截止，请确认有效的邀请安排。")
        when = start.strftime("%m月%d日 %H:%M")
        detail = f"{ctx['title']}将于{when}在{ctx['venue']}举行"
        texts = [f"{hello}{detail}。如果您有兴趣，回复我即可，我们再沟通参与安排。", f"{hello}想邀请您了解一下{ctx['title']}，时间是{when}，地点在{ctx['venue']}。您方便的话，可以回复我。", f"{hello}{detail}。您可以按自己的时间安排考虑，想了解更多时回复我就好。"]
    elif scenario == "price_objection":
        if not request["conversation_history"]:
            return stop("needs_clarification", "ESSENTIAL_FACT_MISSING", "conversation_history", "请补充客户提出价格异议的消息。")
        texts = [f"{hello}理解您对价格的考虑。{product['name']}的目录价格是 ¥{product['price']:,}，我们不提供议价折扣，您可以再慢慢考虑。", f"{hello}谢谢您直接告诉我您的想法。{product['name']}采用{product['detail']}；如果有您想进一步比较的细节，我可以为您说明。", f"{hello}预算确实需要考虑周全。这款不提供议价折扣，您不必急着决定，有具体想了解的地方再告诉我就好。"]
    else:
        return stop("invalid_input", "INPUT_INVALID", "scenario", "不支持此场景。")
    result["candidates"] = [{"candidate_id": i, "text": text} for i, text in enumerate(texts, 1)]
    return result
