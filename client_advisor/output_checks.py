"""Narrow automatic checks, never a substitute for human semantic review."""

import json
import re
from difflib import SequenceMatcher


def parse_output(raw):
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return None, ["HF-01: output is not valid JSON"]
    if not isinstance(data, dict):
        return None, ["HF-01: output must be an object"]
    if data.get("status") in {"needs_clarification", "blocked"}:
        if set(data) != {"status", "reason"} or not isinstance(data["reason"], str) or not data["reason"].strip():
            return None, ["HF-01: non-success output requires only status and reason"]
        return data, []
    if set(data) != {"status", "messages"} or data.get("status") != "generated":
        return None, ["HF-01: expected status and messages only"]
    messages = data["messages"]
    if not isinstance(messages, list) or len(messages) != 3 or any(not isinstance(t, str) or not t.strip() or not re.search(r"[\u4e00-\u9fff]", t) for t in messages):
        return None, ["HF-01: exactly three nonempty Chinese messages required"]
    normalized = [re.sub(r"\s+", "", t) for t in messages]
    if len(set(normalized)) != 3:
        return None, ["HF-06: duplicate candidate messages"]
    markers = r"(?:消息|文案|回复|信息|版本)[一二三123][：:]|不写具体数字|只写.{0,6}问题|由程序|写作要求|三条问题|第[一二三]问|侧重点|BR-\d\d|HF-\d\d|prompt-v\d|方案[一二三123]|候选[一二三123]|candidate_lenses|writing_constraints|receipt\.confirmed|reply_to_advisor|活动名称[：:]|日期时刻[：:]|以.{0,15}为开头|```|<system>|SYSTEM_PROMPT"
    for text in messages:
        match = re.search(markers, text)
        if match:
            return None, [f"HF-06: internal marker {match.group(0)} in client copy; use natural Chinese without field labels or writing instructions"]
    return data, []


def quality_flags(messages):
    flags = []
    for i, text in enumerate(messages, 1):
        if re.search(r"诚邀|莅临|观览|定于|我们坚持|我们的立场|感谢您.{0,5}(?:理解|异议)|完美契合|理想选择|目录中|无需.{0,5}推测|充分考虑了您的偏好|独特的工艺", text):
            flags.append({"code": "NATURALNESS_REVIEW", "field": f"candidates.{i}", "message": "可能包含正式套话、推理泄漏或无依据评价，请审阅；不自动判定失败。"})
        if not 40 <= len(text) <= 100:
            flags.append({"code": "SOFT_LENGTH", "field": f"candidates.{i}", "message": "长度偏离软目标，请结合语境审阅。"})
        if re.search(r"折扣|赠送|免费|保证|限量|最后一|防水|保值|已.{0,4}预留", text):
            flags.append({"code": "CLAIM_REVIEW", "field": f"candidates.{i}", "message": "包含需核实语境与依据的表述，不代表已确认违规。"})
    for i in range(len(messages)):
        for j in range(i):
            if SequenceMatcher(None, messages[i], messages[j]).ratio() > .9:
                flags.append({"code": "DIVERSITY_REVIEW", "field": "candidates", "message": "候选措辞相近，请人工评估差异。"})
    return flags
