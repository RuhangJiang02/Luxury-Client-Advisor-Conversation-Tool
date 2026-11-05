"""Deterministic business preflight, with conservative semantic limitations."""

import calendar
import re
from datetime import date

from .contracts import local_date, timestamp
from .context import PRODUCTS


def outcome(status, code, field, message):
    return {"status": status, "code": code, "field": field, "message": message}


def preflight(request):
    scenario, ctx = request["scenario"], request["scenario_context"]
    client = request["client"]
    contact = client["contact_preferences"]
    messages = request["conversation_history"]
    reply_id = request["interaction"]["reply_to_message_id"]
    proactive = request["interaction"]["mode"] == "proactive"
    client_messages = [m for m in messages if m["role"] == "client"]
    note = contact.get("restrictions_note") or ""
    restrictive = re.compile(r"(?:不要|别再|别|停止|不想|不希望).{0,8}(?:联系|打扰|发消息|发微信|推送)|请勿联系|退订")
    channel_ban = re.compile(r"(?:不要|别|停止).{0,6}(?:微信联系|发微信|在微信)")
    ambiguous = re.compile(r"(?:少|晚点|暂时不|不太方便).{0,5}(?:联系|发消息|打扰)")
    topic_words = {"event_invitation": "活动", "product_recommendation": "新品|推荐", "greeting": "生日|节日"}

    def applies(text):
        if not restrictive.search(text):
            return False
        mentioned = [s for s, words in topic_words.items() if re.search(words, text)]
        return not mentioned or scenario in mentioned

    if channel_ban.search(note) or any(channel_ban.search(m["text"]) for m in client_messages):
        return outcome("blocked", "CONTACT_RESTRICTED", "conversation_history", "客户明确限制微信联系，请先由顾问确认可用渠道。"), {}, []
    if proactive:
        if contact["proactive_status"] == "opted_out" or scenario in contact["restricted_scenarios"] or applies(note) or any(applies(m["text"]) for m in client_messages):
            return outcome("blocked", "CONTACT_RESTRICTED", "client.contact_preferences", "存在适用的主动联系限制，不生成外发文案。"), {}, []
        if contact["proactive_status"] == "unknown" or ambiguous.search(note) or any(ambiguous.search(m["text"]) for m in client_messages):
            return outcome("needs_clarification", "CONTACT_PERMISSION_UNKNOWN", "client.contact_preferences", "请确认主动联系的许可与范围。"), {}, []
    else:
        reply = next((m for m in client_messages if m["message_id"] == reply_id), None)
        if reply and applies(reply["text"]):
            return outcome("blocked", "CONTACT_RESTRICTED", "interaction.reply_to_message_id", "本条客户消息包含适用的停止联系要求。"), {}, []
        if reply and ambiguous.search(reply["text"]):
            return outcome("needs_clarification", "CONTACT_PERMISSION_UNKNOWN", "interaction.reply_to_message_id", "请确认本次回复是否符合客户联系范围。"), {}, []
    if scenario == "event_invitation" and ctx["eligibility"] == "ineligible":
        return outcome("blocked", "EVENT_INELIGIBLE", "scenario_context.eligibility", "客户不符合此活动参与条件。"), {}, []

    notices = []
    derived = {"assessment_eligible": None, "eligible_product_ids": [], "current_inventory": []}

    def clarify(code, field, message):
        return outcome("needs_clarification", code, field, message), derived, notices

    if any(p not in PRODUCTS for p in request["product_ids"]):
        return clarify("PRODUCT_UNRESOLVED", "product_ids", "所选产品不在当前版本目录内。")
    if scenario in {"product_recommendation", "post_purchase_care", "price_objection"} and not request["product_ids"]:
        return clarify("PRODUCT_UNRESOLVED", "product_ids", "请选择所需的目录产品。")
    if scenario == "greeting":
        if ctx["occasion_type"] == "festival" and not ctx["occasion_name"]:
            return clarify("ESSENTIAL_FACT_MISSING", "scenario_context.occasion_name", "请补充节日名称。")
        if ctx["occasion_date"] is None:
            notices.append({"code": "DETAIL_OMITTED", "field": "scenario_context.occasion_date", "message": "日期未知，请勿作同日或年龄推断。"})
    if scenario == "product_recommendation":
        budget = client.get("budget")
        ids = [p for p in request["product_ids"] if not budget or PRODUCTS[p]["price"] <= budget["max_amount"]]
        mapping = {"可斜挎": "crossbody", "斜挎": "crossbody", "可肩背": "shoulder", "肩背": "shoulder", "可手提": "handheld", "手提": "handheld"}
        for requirement in ctx["must_have"]:
            if requirement in mapping:
                ids = [p for p in ids if mapping[requirement] in PRODUCTS[p]["carrying_methods"]]
            elif requirement in {"托特", "托特包"}:
                ids = [p for p in ids if p == "CX-B02"]
            else:
                return clarify("ESSENTIAL_FACT_MISSING", "scenario_context.must_have", "目录中无法核实某项硬性需求，请确认可验证的要求。")
        if not ids:
            return clarify("NO_PRODUCT_FIT", "product_ids", "所选产品不满足已知预算或硬性用途要求。")
        color = ctx.get("preferred_color")
        prefs = "；".join(client["preferences"])
        if color and any(c in prefs and c != color for c in ["墨黑", "岩灰", "栗棕", "砂白"]):
            return clarify("SOURCE_CONFLICT", "scenario_context.preferred_color", "客户颜色偏好存在冲突，请确认当前偏好。")
        derived["eligible_product_ids"] = ids
        if not ctx["use_case"] or not client["preferences"]:
            notices.append({"code": "DETAIL_OMITTED", "field": "client.preferences", "message": "偏好信息有限，使用克制描述或适当询问。"})
    else:
        derived["eligible_product_ids"] = request["product_ids"]
    if scenario == "post_purchase_care":
        purchase = ctx["purchase"]
        when = purchase["purchased_on"]
        if when and purchase["assessment_used"] is not None:
            day = date.fromisoformat(when)
            end = day.replace(year=day.year + 1, day=min(day.day, calendar.monthrange(day.year + 1, day.month)[1]))
            derived["assessment_eligible"] = not purchase["assessment_used"] and day <= local_date(request) <= end
        if derived["assessment_eligible"] is not True:
            notices.append({"code": "ELIGIBILITY_UNCONFIRMED", "field": "scenario_context.purchase", "message": "未确认可用的免费评估权益；不能承诺免费服务。"})
    if scenario == "event_invitation":
        for key in ["title", "format", "starts_at", "ends_at", "venue", "rsvp_method"]:
            if ctx.get(key) is None:
                return clarify("ESSENTIAL_FACT_MISSING", f"scenario_context.{key}", "请补充已确认的活动详情。")
        if ctx["eligibility"] != "eligible":
            return clarify("ESSENTIAL_FACT_MISSING", "scenario_context.eligibility", "请确认活动参与资格。")
        if timestamp(ctx["starts_at"]) <= timestamp(request["reference_time"]) or (ctx.get("rsvp_deadline") and timestamp(ctx["rsvp_deadline"]) <= timestamp(request["reference_time"])):
            return clarify("ESSENTIAL_FACT_MISSING", "scenario_context.starts_at", "活动已开始或报名已截止，请确认有效邀请安排。")
    if scenario == "price_objection":
        if not messages:
            return clarify("ESSENTIAL_FACT_MISSING", "conversation_history", "请补充客户提出价格异议的消息。")
        comp = ctx.get("comparison")
        if comp:
            text = next(m["text"] for m in messages if m["message_id"] == ctx["objection_message_id"]).replace(",", "")
            amount = comp["reported_amount"]
            if (comp["reported_seller"] and comp["reported_seller"] not in text) or (amount is not None and str(int(amount) if float(amount).is_integer() else amount) not in text):
                return clarify("SOURCE_CONFLICT", "scenario_context.comparison", "比价信息未得到对应客户消息支持。")
    ref = timestamp(request["reference_time"])
    for item in request["trusted_context"]["inventory"]:
        if timestamp(item["confirmed_at"]) <= ref <= timestamp(item["valid_until"]):
            previous = next((i for i in derived["current_inventory"] if (i["product_id"], i["color"]) == (item["product_id"], item["color"])), None)
            if previous and previous["status"] != item["status"]:
                return clarify("SOURCE_CONFLICT", "trusted_context.inventory", "有效库存记录互相矛盾。")
            derived["current_inventory"].append(item)
        else:
            notices.append({"code": "INVENTORY_STALE", "field": "trusted_context.inventory", "message": "库存证据不在有效时间内，不作可用性承诺。"})
    return None, derived, notices
