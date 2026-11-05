"""Strict shape and cross-reference validation; semantic policy checks are separate."""

import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

from jsonschema import Draft202012Validator, FormatChecker

from .config import ROOT
from .context import PRODUCTS

SCHEMA = json.loads((ROOT / "data/request.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
SCENARIOS = tuple(SCHEMA["properties"]["scenario"]["enum"])


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def local_date(request):
    return timestamp(request["reference_time"]).astimezone(ZoneInfo("Asia/Shanghai")).date()


def validate_request(request):
    errors = []
    for err in sorted(VALIDATOR.iter_errors(request), key=lambda e: str(list(e.path))):
        # Avoid echoing arbitrary values, including accidentally pasted secrets.
        errors.append({"field": ".".join(map(str, err.path)) or "$", "message": f"Input failed {err.validator} validation."})
    if errors:
        return errors
    def check_blank(value, path="$"):
        if isinstance(value, str) and not value.strip():
            errors.append({"field": path, "message": "Nonempty text cannot contain whitespace only."})
        elif isinstance(value, dict):
            for key, item in value.items(): check_blank(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value): check_blank(item, f"{path}.{index}")
    check_blank(request)
    if errors:
        return errors
    ref = timestamp(request["reference_time"])
    today = local_date(request)
    scenario, ctx = request["scenario"], request["scenario_context"]

    def error(field, message):
        errors.append({"field": field, "message": message})

    messages = request["conversation_history"]
    by_id = {m["message_id"]: m for m in messages}
    if len(by_id) != len(messages):
        error("conversation_history", "Duplicate message IDs.")
    last = None
    for m in messages:
        if m["sent_at"]:
            current = timestamp(m["sent_at"])
            if current > ref or (last and current < last):
                error("conversation_history", "History chronology contradicts reference time or sequence.")
            last = current
    interaction = request["interaction"]
    reply = interaction["reply_to_message_id"]
    if interaction["mode"] == "reply":
        # Empty price-objection history is handled as missing essential content below.
        if not (scenario == "price_objection" and not messages) and (reply not in by_id or by_id[reply]["role"] != "client"):
            error("interaction.reply_to_message_id", "Reply must reference a client message.")
    elif reply is not None:
        error("interaction.reply_to_message_id", "Proactive interaction cannot reference a reply.")
    for mid in request["client"]["contact_preferences"]["source_message_ids"]:
        if mid not in by_id or by_id[mid]["role"] != "client":
            error("client.contact_preferences.source_message_ids", "Restriction must reference a client message.")
    refs = request["trusted_context"]["source_refs"]
    sources = {s["source_id"]: s for s in refs}
    if len(sources) != len(refs):
        error("trusted_context.source_refs", "Duplicate source IDs.")
    if request["product_ids"] and not any(s["kind"] == "catalogue" for s in refs):
        error("trusted_context.source_refs", "Catalogue source is required for product resolution.")

    def source(source_id, kind, field):
        if source_id not in sources or sources[source_id]["kind"] != kind:
            error(field, "Missing source reference or mismatched source kind.")

    for item in request["trusted_context"]["inventory"]:
        source(item["source_id"], "inventory", "trusted_context.inventory.source_id")
        if item["product_id"] not in PRODUCTS or item["color"] not in PRODUCTS[item["product_id"]]["colors"]:
            error("trusted_context.inventory", "Inventory product/color is outside the pinned catalogue.")
        if timestamp(item["confirmed_at"]) > timestamp(item["valid_until"]):
            error("trusted_context.inventory", "Inventory interval is inverted.")
    if scenario in {"greeting", "reactivation"} and request["product_ids"]:
        error("product_ids", "This scenario does not accept product selection.")
    if scenario == "greeting" and ctx["occasion_type"] == "birthday" and ctx["occasion_name"] is not None:
        error("scenario_context.occasion_name", "Birthday occasion_name must be null.")
    if scenario == "post_purchase_care":
        purchase = ctx["purchase"]
        source(purchase["source_id"], "purchase", "scenario_context.purchase.source_id")
        if request["product_ids"] != [purchase["product_id"]]:
            error("product_ids", "Purchase and selected product must match exactly.")
        if purchase["purchased_on"] and date.fromisoformat(purchase["purchased_on"]) > today:
            error("scenario_context.purchase.purchased_on", "Purchase date cannot be in the future.")
        if ctx["care_topic"] == "reported_issue":
            mid = ctx["issue_message_id"]
            if mid not in by_id or by_id[mid]["role"] != "client":
                error("scenario_context.issue_message_id", "Reported issue must reference a client message.")
        elif ctx["issue_message_id"] is not None:
            error("scenario_context.issue_message_id", "Only reported_issue accepts an issue reference.")
    if scenario == "reactivation":
        for key in ["last_contact_on", "last_purchase_on"]:
            if ctx[key] and date.fromisoformat(ctx[key]) > today:
                error(f"scenario_context.{key}", "Past-contact date cannot be in the future.")
    if scenario == "event_invitation":
        source(ctx["source_id"], "event", "scenario_context.source_id")
        if ctx["starts_at"] and ctx["ends_at"] and timestamp(ctx["ends_at"]) <= timestamp(ctx["starts_at"]):
            error("scenario_context.ends_at", "Event end must be later than start.")
        if ctx.get("rsvp_deadline") and ctx["starts_at"] and timestamp(ctx["rsvp_deadline"]) > timestamp(ctx["starts_at"]):
            error("scenario_context.rsvp_deadline", "RSVP deadline cannot follow event start.")
    if scenario == "price_objection":
        if interaction["mode"] != "reply" or ctx["objection_message_id"] != reply:
            error("interaction", "Price objection must reply to its referenced objection message.")
        if len(request["product_ids"]) > 1:
            error("product_ids", "Price objection accepts exactly one product.")
        comp = ctx.get("comparison")
        if comp and (ctx["objection_type"] != "comparison" or (comp["reported_amount"] is not None and comp["currency"] != "CNY")):
            error("scenario_context.comparison", "Comparison context/type/currency are inconsistent.")
    return errors
