"""Narrow evidence checks for observed defects; not complete semantic verification."""

import re
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

from .context import resolved_products
from .contracts import timestamp
from .source_checks import check_sources

RECEIPT = re.compile(r"已经?收到|已经?到手|已经?签收|已经?送达|收到了|已拿到|已经拿到|刚收到|刚拿到|收到包了")


def asserted_matches(text, pattern):
    """Skip simple conditional/negated clauses, without claiming full language parsing."""
    for clause in re.split(r"[。！？!?；;，,\n]", text):
        for match in pattern.finditer(clause):
            prefix = clause[:match.start()]
            if re.search(r"如果|假如|若|要是|等到|不能(?:说|断言|确认)|无法(?:确认|核实|判断)|不确定|尚未|暂未|未确认|还没|还未|并未|并非|没有", prefix):
                continue
            yield match.group(0)


def receipt_assertions(text):
    for clause in re.split(r"[。！？!?；;，,\n]", text):
        if re.search(r"收到.{0,8}(?:消息|邀请|通知|微信|邮件|反馈|问题|记录)", clause):
            continue
        yield from asserted_matches(clause, RECEIPT)


def receipt_evidence(request):
    """Only explicit positive client reports can establish receipt for this baseline."""
    for message in request["conversation_history"]:
        if message["role"] != "client":
            continue
        for clause in re.split(r"[。！？!?；;，,\n]", message["text"]):
            if re.search(r"包|皮具|卡夹|长夹|商品|货|快递|订单", clause) and any(receipt_assertions(clause)):
                return {"confirmed": True, "source_message_id": message["message_id"]}
    return {"confirmed": False, "source_message_id": None}


def candidate_lenses(request):
    scenario = request["scenario"]
    if scenario == "post_purchase_care":
        if request["scenario_context"]["care_topic"] == "reported_issue":
            return ["回应客户当前问题，只给已批准的谨慎养护建议", "理解顾虑，说明可协助安排评估但不保证修复", "围绕客户问题提出一个有用的问题，不再重复完整养护清单"]
        return ["关于这只包，询问客户是否想了解使用/养护细节；不假设已经收货或已经使用", "只聚焦一种日常清洁建议：干净柔软的干布轻拭", "只聚焦保持干燥和防尘袋存放，可给一个简短的支持选项"]
    if scenario == "price_objection":
        ctx = request["scenario_context"]
        if ctx["objection_type"] == "comparison":
            return ["承认差价，说明已知价格与未核实边界", "直接回应为什么：报价条件未核实，不猜原因，不转推材质", "让客户慢慢比较，不重复材质/价格，不承诺替代方案"]
        inbound = " ".join(m["text"] for m in request["conversation_history"] if m["role"] == "client")
        if ctx["objection_type"] != "discount_request" and any(w in inbound for w in ["再考虑", "不要催", "考虑一下", "想一想"]):
            return ["简短确认，可以慢慢考虑", "说明不用急着决定，按自己的节奏", "结束本轮推介，客户方便时再联系即可"]
    return {
        "greeting": ["简洁温暖的生日或节日祝福", "从容生活角度的祝福，不推断个人经历", "轻松愉快的祝福，换一个自然切入点"],
        "product_recommendation": ["从已知用途/预算解释适配", "只介绍一个已知设计细节", "用一个偏好问题帮助选择，不假定已经选购"],
        "reactivation": ["简短问候，不附带购买要求", "问一个近期偏好问题", "给客户方便时再联系的空间，不重复偏好问题"],
        "event_invitation": ["直接简洁邀请，交代活动名称、日期时刻、完整地点，不写字段标签", "如果客户想看看设计，可参加这次活动；交代活动安排和完整地点，不假装客户已有兴趣", "让客户可自由安排时间，交代活动名称、日期时刻、完整地点，邀请有兴趣时回复；不用公文腔"],
        "price_objection": ["先理解顾虑，再简明说明已知价格/不议价政策", "认可顾虑，陈述一个已知产品细节与政策；绝不解释价格为何如此", "给客户慢慢考虑的空间，同时清楚回应折扣请求；不声称不存在所有替代品"],
    }[scenario]


def grounding_context(request):
    return {
        "receipt": receipt_evidence(request),
        "pricing_rationale_known": False,
        "alternative_absence_known": False,
        "candidate_lenses": candidate_lenses(request),
    }


def diversity_scores(messages, request):
    """Lexical near-copy proxy after removing shared logistics/product identifiers."""
    facts = [request["client"].get("preferred_address") or ""]
    facts.extend(p["name"] for p in resolved_products(request["product_ids"]))
    if request["scenario"] == "event_invitation":
        facts.extend(request["scenario_context"].get(k) or "" for k in ["title", "venue"])
    normalized = []
    for text in messages:
        for fact in facts:
            if fact:
                text = text.replace(fact, "")
        text = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2}", "", text)
        normalized.append(re.sub(r"[\s，。！？、；：,.!?;:]", "", text))
    return [{"pair": [j + 1, i + 1], "ratio": round(SequenceMatcher(None, normalized[i], normalized[j]).ratio(), 4)} for i in range(len(messages)) for j in range(i) if min(len(normalized[i]), len(normalized[j])) >= 12]


def check_grounding(parsed, request):
    if parsed.get("status") != "generated":
        return [], []
    errors = check_sources(parsed, request)
    evidence = receipt_evidence(request)
    products = resolved_products(request["product_ids"])
    available_colors = {color for product in products for color in product["colors"]}
    rationale = re.compile(r"(?:定价|价格|售价|报价).{0,12}(?:基于|考虑.{0,8}(?:材质|工艺|品质|成本|因素)|体现|反映|因为|取决|由于)|(?:基于|因为).{0,24}(?:材质|工艺|品质|设计).{0,15}(?:定价|价格)|(?:价格|价差|报价|售价).{0,8}(?:差异|不同).{0,10}(?:源于|来自|因为|由于|取决|与.{0,8}有关)|价差.{0,10}(?:源于|来自|因为|由于|与.{0,8}有关)")
    absence = re.compile(r"(?:没有|不存在|不提供|无)(?:任何|其他|更低价|低价|别的|其它).{0,10}(?:替代|款式|方案|尺寸)|不存在.{0,12}替代方案")
    for i, text in enumerate(parsed["messages"], 1):
        for color in {"墨黑", "岩灰", "栗棕", "砂白"} - available_colors if products else []:
            names = "|".join(re.escape(p["name"]) for p in products)
            if re.search(rf"(?:这款|这只|该款|本款).{{0,8}}{color}|{color}色?(?:款|的)?(?:{names})", text):
                errors.append(f"GROUNDING_PRODUCT_COLOR 候选{i}：所选目录不支持所述产品配色，不把客户颜色偏好当成商品事实。")
        if request["scenario"] == "post_purchase_care":
            negative = re.compile(r"(?:包|商品|货|快递|订单).{0,10}(?:还没|尚未|还未|未)收到|(?:还没|尚未|还未)(?:收到|到手)")
            negative_claim = bool(negative.search(text)) and not re.search(r"如果|假如|若|要是", text)
            client_negative = any(negative.search(m["text"]) for m in request["conversation_history"] if m["role"] == "client")
            if negative_claim and (evidence["confirmed"] or not client_negative):
                errors.append(f"GROUNDING_NON_RECEIPT 候选{i}：没有客户未收到的有效依据，或客户已明确收到；收货未知不等于未收到。删除未收到/未到手断言，直接谈使用或养护。")
        if request["scenario"] == "post_purchase_care" and not evidence["confirmed"] and any(receipt_assertions(text)):
            errors.append(f"GROUNDING_RECEIPT 候选{i}：没有已收货证据，删除已到手/已收到等断言；可直接说关于这只包的养护。")
        if request["scenario"] == "post_purchase_care" and not evidence["confirmed"] and any(asserted_matches(text, re.compile(r"最近.{0,8}(?:使用|用得|在用)|已经.{0,8}(?:使用|在用)"))):
            errors.append(f"GROUNDING_USAGE 候选{i}：尚未确认收货，不能假设最近已在使用；改为询问想了解什么使用细节。")
        if request["scenario"] == "price_objection":
            if any(asserted_matches(text, rationale)):
                errors.append(f"GROUNDING_PRICE_RATIONALE 候选{i}：未提供定价依据，删除价格基于材质/工艺/品质等因果解释；只说已知目录价和政策。")
            for clause in re.split(r"[。！？!?；;，,\n]", text):
                if absence.search(clause) and not re.search(r"(?:资料|信息|记录).{0,8}(?:没有|未|不含)|(?:没有|暂无|未提供).{0,8}(?:资料|信息|记录)", clause):
                    errors.append(f"GROUNDING_ALTERNATIVE_ABSENCE 候选{i}：未知是否存在其他方案，删除不存在其他尺寸/替代品等绝对否定。")
                if re.search(r"(?:其他|其它|别的)尺寸", clause) and not re.search(r"没有|未|不确定|不能|不涉及|资料|信息|确认", clause):
                    errors.append(f"GROUNDING_UNVERIFIED_SIZE 候选{i}：没有其他尺寸资料，不把其他尺寸作为可选方案提出。")
            if request["scenario_context"]["objection_type"] == "discount_request" and not re.search(r"(?:不|不能|无法|不会).{0,8}(?:折扣|打折|议价)|没有.{0,4}(?:折扣|议价)", text):
                errors.append(f"POLICY_DISCOUNT_REPLY 候选{i}：客户要求折扣，需明确说明不提供议价折扣。")
        if request["scenario"] == "event_invitation":
            ctx = request["scenario_context"]
            normalize = lambda value: re.sub(r"[\s·•・，,]", "", value)
            names = [ctx["title"]] + [alias for alias in ["私享预览", "私人预览", "新品预览", "皮具预览", "手提包预览"] if alias in ctx["title"]]
            if normalize(ctx["venue"]) not in normalize(text) or not any(name in text for name in names):
                errors.append(f"EVENT_LOGISTICS 候选{i}：每条是独立消息，须含活动名称{ctx['title']}和完整地点{ctx['venue']}。")
            start = timestamp(ctx["starts_at"]).astimezone(ZoneInfo("Asia/Shanghai"))
            date_pattern = rf"{start.month}月0?{start.day}[日号]|{start:%Y-%m-%d}"
            minutes = r"(?:整|0?0分)?" if start.minute == 0 else rf"{start.minute}分"
            time_pattern = rf"{start.hour}[:：]{start.minute:02}(?!\d)|{start.hour}点{minutes}(?!\d)"
            if start.hour >= 12:
                time_pattern += rf"|下午{start.hour-12 or 12}(?:点{minutes}(?!\d)|[:：]{start.minute:02}(?!\d))"
            if not re.search(date_pattern, text) or not re.search(time_pattern, text):
                errors.append(f"EVENT_TIME 候选{i}：明确写{start.month}月{start.day}日{start:%H:%M}，不要省略活动日期或开始时刻。")
            if "新品" in text and "新品" not in ctx["title"]:
                errors.append(f"GROUNDING_EVENT_LAUNCH 候选{i}：未提供新品发布事实，删除新品说法。")
    if request["scenario"] == "price_objection" and request["scenario_context"]["objection_type"] == "discount_request":
        texts = parsed["messages"]
        if not any(re.search(r"粒面牛皮|光面牛皮|拉链|旋锁|肩带|卡位|内衬|口袋|尺寸", t) for t in texts):
            detail = products[0]["detail"] if products else "已有的产品资料"
            errors.append(f"DIVERSITY_PRICE_FACT：第二条不能只重复政策，请加入一个已知事实：{detail}；不要将它说成定价理由。")
        if any(re.search(r"粒面牛皮|光面牛皮|拉链|旋锁|肩带|卡位|内衬|口袋|尺寸|厘米", texts[index]) for index in [0, 2]):
            errors.append("DIVERSITY_PRICE_OVERLOAD：只在第二条介绍一个产品细节；第一条只讲价格与政策，第三条只讲政策与慢慢考虑的空间，删除重复参数。")
        if not any(re.search(r"慢慢|再考虑|不(?:必|用)?(?:着)?急|按您自己的节奏|留.{0,5}时间|需要.{0,5}时间", t) for t in texts):
            errors.append("DIVERSITY_PRICE_SPACE：请重写第三条，明确不提供议价折扣，并写出慢慢考虑或不必急着决定的意思；不介绍属性、不问其他需求。")
    scores = diversity_scores(parsed["messages"], request)
    if any(pair["ratio"] >= .9 for pair in scores):
        errors.append("DIVERSITY_NEAR_COPY：至少两条去除共同事实后仍近乎重复；按照三个不同侧重点重写，不只换开头。")
    return errors, scores
