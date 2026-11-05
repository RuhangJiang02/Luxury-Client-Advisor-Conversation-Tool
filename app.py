"""Streamlit UI preview. Run: .venv/bin/python -m streamlit run app.py."""

import copy
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from preview_service import preview
from client_advisor.context import PRODUCTS
from client_advisor import TOOL_VERSION
from client_advisor.config import Config
from client_advisor.service import GenerationService

ROOT = Path(__file__).resolve().parent
FIXTURES = json.loads((ROOT / "examples/io-v0.1/examples.json").read_text())["scenario_requests"]
SCENARIOS = {
    "greeting": ("01", "生日与节日问候", "让一句问候，有恰到好处的温度。"),
    "product_recommendation": ("02", "产品推荐", "从具体偏好出发，找到值得了解的细节。"),
    "post_purchase_care": ("03", "购后关怀", "让服务延续到购买之后的日常。"),
    "reactivation": ("04", "沉睡客户唤醒", "留一份轻盈的问候，把选择交给客户。"),
    "event_invitation": ("05", "活动邀请", "清楚传达安排，留出从容考虑的空间。"),
    "price_objection": ("06", "价格异议", "认真回应顾虑，保持坦诚与分寸。"),
}

st.set_page_config(page_title="澄序 · 顾问工作台", page_icon="◈", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1440px;}
h1, h2, h3 {letter-spacing: .025em;}
.brand-title {font-family: 'Songti SC', 'STSong', serif; font-size: 2.6rem; font-weight: 600; margin-bottom: .2rem;}
.eyebrow {font-size: .7rem; letter-spacing: .24em; color: #6a7b70; margin-bottom: .7rem;}
.subheading {color: #798176; font-size: .95rem; margin-bottom: 1.6rem;}
[data-testid="stSidebar"] {border-right: 1px solid #dedfd4;}
[data-testid="stSidebar"] .block-container {padding-top: 2rem;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 10px;}
.stButton > button[kind="primary"] {border-radius: 5px;}
.rule-line {border-top: 1px solid #dcded3; margin: 1.8rem 0;}
.footer-note {font-size: .75rem; color: #84897e; margin-top: 2rem; letter-spacing: .04em;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="eyebrow">CHENGXU · CLIENT ADVISOR</div>', unsafe_allow_html=True)
    st.markdown("## 澄序")
    st.caption("让日常，自有从容。")
    st.divider()
    scenario = st.selectbox("沟通场景", list(SCENARIOS), format_func=lambda k: f"{SCENARIOS[k][0]}  {SCENARIOS[k][1]}", key="scenario-selector")
    st.divider()
    st.markdown("**工作模式**")
    config_error = None
    try:
        runtime_config = Config.load()
    except (ValueError, OSError):
        runtime_config = Config()
        config_error = "模型配置格式有误，请检查 .env。"
    mode = st.radio("生成方式", ["preview", "live"], format_func=lambda x: "离线模板预览" if x == "preview" else ("本地模型真实生成" if runtime_config.provider == "ollama" else "OpenAI 真实生成"), key="generation-mode")
    if mode == "preview":
        st.info("人工模板，不调用 API，不计入正式测试。")
    else:
        st.caption(f"模型：{runtime_config.model}")
        if config_error:
            st.error(config_error)
        elif runtime_config.provider == "ollama":
            st.success("本地推理 · 不需要 API Key")
            st.caption("Ollama 服务与模型需在本机运行。")
        elif runtime_config.api_key:
            st.success("API 密钥已配置（不显示内容）。")
        else:
            st.warning("尚未配置 OPENAI_API_KEY。请在项目 .env 中配置后重新提交。")
    st.caption(f"品牌规则 brand-v0.1\n\n输入输出 io-v0.1\n\n应用版本 {TOOL_VERSION}")
    st.caption("所有客户、产品与活动均为虚构。")
    st.caption("示例业务参考时间：2026-11-04 20:30（北京时间）。")

st.markdown('<div class="eyebrow">RELATIONSHIPS, THOUGHTFULLY WRITTEN</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title">客户沟通工作台</div>', unsafe_allow_html=True)
st.markdown('<div class="subheading">为每一次沟通，留出专业与温度。</div>', unsafe_allow_html=True)
if mode == "preview":
    st.warning("离线预览：候选消息来自人工模板，不计入正式评测。切换左侧生成方式可调用配置的真实模型。")
else:
    st.info(("本地模型模式：不使用付费 API。" if runtime_config.provider == "ollama" else "OpenAI 模式：") + "仅在提交时调用模型并保存运行记录。候选消息需由顾问审阅，自动检查不代表语义完全正确。")

fixture = copy.deepcopy(next(r for r in FIXTURES if r["scenario"] == scenario))
prefix = scenario
left, right = st.columns([1, 1.15], gap="large")

with left:
    st.subheader("01 / 沟通背景")
    st.caption(SCENARIOS[scenario][2])
    with st.form(f"form-{scenario}"):
        c1, c2 = st.columns(2)
        address = c1.text_input("客户称呼", value=fixture["client"]["preferred_address"], key=f"{prefix}-address")
        relationship = c2.selectbox("客户关系", ["established", "new", "unknown"], format_func=lambda x: {"established": "已有往来", "new": "初次接触", "unknown": "尚不确定"}[x], key=f"{prefix}-relationship")
        preferences = st.text_input("已知偏好", value="；".join(fixture["client"]["preferences"]), key=f"{prefix}-preferences", help="仅填写客户明确表达的偏好。真实模型模式会将明确偏好作为上下文；模板模式不会推理匹配。")
        consent = st.selectbox("主动联系偏好", ["allowed", "opted_out", "unknown"], format_func=lambda x: {"allowed": "允许主动联系", "opted_out": "已拒绝主动联系", "unknown": "尚未确认"}[x], key=f"{prefix}-consent")
        history = st.text_area("客户最近消息 / 对话背景", value="\n".join(m["text"] for m in fixture["conversation_history"]), height=95, key=f"{prefix}-history", help="预览版将此内容作为一条客户消息保存；完整多轮编辑待后续实现。真实模式会筛查已知限制并传入模型；可在高级 JSON 中编辑完整多轮历史。")
        st.markdown("**场景信息**")
        ctx = copy.deepcopy(fixture["scenario_context"])
        product_ids = fixture["product_ids"]
        budget = None
        if scenario in {"product_recommendation", "post_purchase_care", "price_objection", "event_invitation"}:
            ids = list(PRODUCTS)
            default = product_ids[0] if product_ids else ids[0]
            pid = st.selectbox("相关产品", ids, index=ids.index(default), format_func=lambda p: f"{PRODUCTS[p]['name']} · ¥{PRODUCTS[p]['price']:,}", key=f"{prefix}-product")
            product_ids = [pid]
            st.caption(PRODUCTS[pid]["detail"])
        if scenario == "greeting":
            occasion = st.selectbox("问候类型", ["birthday", "festival"], format_func=lambda x: "生日" if x == "birthday" else "节日", key=f"{prefix}-occasion")
            festival = st.text_input("节日名称（生日时留空）", key=f"{prefix}-festival")
            ctx.update(occasion_type=occasion, occasion_name=(festival.strip() or None) if occasion == "festival" else None)
        elif scenario == "product_recommendation":
            ctx["use_case"] = st.text_input("使用场景", value=ctx["use_case"], key=f"{prefix}-use")
            amount = st.number_input("预算上限（元；0 表示未知）", min_value=0, value=15000, step=1000, key=f"{prefix}-budget")
            budget = {"max_amount": amount, "currency": "CNY"} if amount else None
        elif scenario == "post_purchase_care":
            purchased = st.date_input("购买日期", value=datetime.fromisoformat(ctx["purchase"]["purchased_on"]).date(), key=f"{prefix}-date")
            ctx["purchase"].update(product_id=pid, purchased_on=purchased.isoformat())
            st.caption("本次展示日常养护。专属服务资格与问题件处理尚未实现。")
        elif scenario == "reactivation":
            ctx["reconnect_purpose"] = st.selectbox("联系目的", ["preference_update", "relationship_check_in"], format_func=lambda x: "了解近期偏好" if x == "preference_update" else "轻量关系问候", key=f"{prefix}-purpose")
            st.caption("不以长期未购买为由施压；未知时间不补造。")
        elif scenario == "event_invitation":
            ctx["title"] = st.text_input("活动名称", value=ctx["title"], key=f"{prefix}-title")
            ctx["venue"] = st.text_input("活动地点", value=ctx["venue"], key=f"{prefix}-venue")
            event_date = st.date_input("活动日期", value=datetime.fromisoformat(ctx["starts_at"]).date(), key=f"{prefix}-event-date")
            ctx["starts_at"] = f"{event_date.isoformat()}T14:00:00+08:00"
            ctx["ends_at"] = f"{event_date.isoformat()}T17:00:00+08:00"
            ctx["rsvp_deadline"] = None
            st.caption("示例时段为北京时间 14:00–17:00；客户资格沿用虚构示例。")
        elif scenario == "price_objection":
            ctx["objection_type"] = st.selectbox("异议类型", ["discount_request", "too_expensive", "comparison"], format_func=lambda x: {"discount_request": "要求折扣", "too_expensive": "认为太贵", "comparison": "其他渠道比价"}[x], key=f"{prefix}-objection")
            st.caption("保持品牌不议价政策，不编造竞品或渠道结论。")
        with st.expander("高级输入 · 完整请求 JSON"):
            use_json = st.checkbox("本次使用下方 JSON，替代上面的表单输入", key=f"{prefix}-use-json")
            advanced_json = st.text_area("完整请求（仅本地操作者可编辑）", value=json.dumps(fixture, ensure_ascii=False, indent=2), height=220, key=f"{prefix}-json")
            st.caption("支持 io-v0.1 的完整多轮历史、日期、权益与活动字段。外部文本不会改变已批准的品牌政策。")
        submitted = st.form_submit_button("预览三条候选消息 →" if mode == "preview" else "生成三条候选消息 →", type="primary", width="stretch")

    request = copy.deepcopy(fixture)
    request["client"].update(preferred_address=address.strip() or None, relationship_stage=relationship, preferences=[v.strip() for v in preferences.split("；") if v.strip()], budget=budget)
    request["client"]["contact_preferences"]["proactive_status"] = consent
    request["product_ids"] = product_ids
    request["scenario_context"] = ctx
    request["conversation_history"] = [{"message_id": "msg-001", "role": "client", "text": history.strip(), "sent_at": None}] if history.strip() else []
    if scenario == "price_objection":
        request["interaction"].update(mode="reply", reply_to_message_id="msg-001")
    if scenario == "post_purchase_care":
        request["client"]["owned_product_ids"] = product_ids

    result_key = f"result-{mode}-{scenario}"
    if submitted or (mode == "preview" and result_key not in st.session_state):
        if not submitted:
            request = copy.deepcopy(fixture)
        if submitted and use_json:
            try:
                request = json.loads(advanced_json)
            except ValueError:
                request = {"invalid_json": True}
        if isinstance(request, dict):
            request["request_id"] = str(uuid4())
        if mode == "live":
            if config_error:
                st.error(config_error)
            else:
                with st.spinner("正在校验并生成消息…"):
                    try:
                        artifact = GenerationService(config=runtime_config).generate(request)
                        st.session_state[result_key] = {"request": request, "response": artifact["response"], "artifact": artifact, "initial": False}
                    except (OSError, ValueError):
                        st.error("配置或本地运行存储不可用，请检查服务器设置。")
        else:
            if submitted and use_json:
                st.warning("高级 JSON 请在真实模型模式下提交；模板模式仅支持表单。")
            else:
                st.session_state[result_key] = {"request": request, "response": preview(request), "initial": not submitted}

with right:
    st.subheader("02 / 候选消息")
    saved = st.session_state.get(result_key)
    if saved is None:
        st.caption("填写左侧信息并提交后，三条候选消息将显示在这里。")
        st.caption("不会在切换场景或刷新页面时自动调用模型。")
    response = saved["response"] if saved else None
    if saved:
        if saved["initial"]:
            st.caption("下方是该场景的预置示例。修改左侧信息并提交，可更新模板预览。")
        else:
            st.caption("以下结果对应最近一次提交；表单修改后需要重新提交才会更新。")
        if response["status"] == "generated":
            st.caption("人工模板 · 非 LLM 生成 · 未计入测试集" if mode == "preview" else f"{saved.get('artifact', {}).get('config', {}).get('provider', 'model')} · {response['metadata']['model_id']} · 已保存运行记录")
            for c, label in zip(response["candidates"], ["简洁表达", "细节与关怀", "从容回应"]):
                with st.container(border=True):
                    st.markdown(f"**候选 0{c['candidate_id']}**　·　{label}")
                    st.write(c["text"])
                    a, b = st.columns([1, 2])
                    if a.button("选择此条", key=f"choose-{scenario}-{c['candidate_id']}"):
                        st.session_state[f"selection-{scenario}"] = {"run_id": response["metadata"]["run_id"], "candidate_id": c["candidate_id"]}
                    b.caption(f"{len(c['text'])} 字符")
            selected = st.session_state.get(f"selection-{scenario}")
            if selected and selected["run_id"] == response["metadata"]["run_id"]:
                st.success(f"已选择候选 0{selected['candidate_id']}，仅供顾问审阅，未发送。")
        else:
            st.warning("本次未生成候选消息。")
            for notice in response["notices"]:
                st.write(notice["message"])
            st.caption(f"状态：{response['status']}")
        st.download_button("下载本次运行记录 · JSON", data=json.dumps(saved.get("artifact") or {"preview_notice": "Hand-written offline templates; not model outputs or evaluation evidence.", "request": saved["request"], "response": response}, ensure_ascii=False, indent=2), file_name=f"chengxu-preview-{scenario}.json", mime="application/json", width="stretch")
        with st.expander("查看已提交输入与运行信息"):
            st.json({"request": saved["request"], "response": response})

st.divider()
with st.expander("品牌与产品参考"):
    st.caption("以下为虚构目录信息，不代表实时库存。")
    st.dataframe([{"产品": v["name"], "目录价格 / CNY": v["price"], "配色": "、".join(v["colors"]), "产品信息": v["detail"]} for v in PRODUCTS.values()], hide_index=True, width="stretch")
st.markdown('<div class="footer-note">澄序 CHENGXU　/　顾问审阅后使用　/　支持本地模型 · 离线模板独立标注</div>', unsafe_allow_html=True)
