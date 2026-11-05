> Historical working draft; superseded by current project documents. Relative evidence links adjusted for this location.

# Six-Scenario UI Demonstration

Revision: **ui-demo-v0.1**, November 5, 2026 (Asia/Shanghai). Application: **tool-v0.8.2 / prompt-v0.8.2**, architecture arch-v0.3.

This is a rehearsal guide for the current Streamlit application. It separates a reliable template walkthrough, real local inference and isolated UI verification. Existing 50-case repair/reruns/scoring remain deferred; these demo inputs are separate and do not replace that evidence.

## 1. Start and explain the workspace

Follow the [running guide](../../running-and-evaluation.md), then open [the local app](http://127.0.0.1:8501). The page title is “客户沟通工作台”. The sidebar contains “沟通场景” and “生成方式”; the main columns are “01 / 沟通背景” and “02 / 候选消息”.

Explain the product in one sentence: **the advisor supplies a client context and scenario, receives three Chinese drafts, and reviews one before sending outside this application.** Everything is fictional; selecting a draft does not send WeChat or book a service.

Use these modes deliberately:

| Mode label | What the operator sees | Meaning |
| --- | --- | --- |
| “离线模板预览” | Three preloaded handwritten candidates on each scenario | A UI demonstration, with no model call and no model-quality evidence |
| “本地模型真实生成” | A blank live result until explicit submit, then a saved outcome | Actual local inference through Ollama; generated copy still needs review |

For greeting, recommendation and invitation, the local tool combines actual model bodies with source-bound facts. Product selection is the first preflight-eligible item, not LLM ranking. Care, reactivation and price responses use full model-authored drafts. The [methodology](../../methodology.md) explains this authorship boundary.

The example business clock is **2026-11-04 20:30 Asia/Shanghai**, not the current wall clock. Event/purchase checks use that request value. Execution timestamps are separate. Do not claim that a demonstration date is today's date; an operator-controlled advanced request can carry another internally consistent reference time.

## 2. Repeatable interaction for every scenario

1. Select the matching scenario in the sidebar. Start in template preview to explain the fields without inference.
2. Use the fictional defaults or the values below. Review contact permission and applicable product/context.
3. Press “预览三条候选消息 →” for template changes, or deliberately switch to local live mode and press “生成三条候选消息 →”. Switching modes/scenarios alone does not invoke the model.
4. On success, compare all three cards. Their headings are fixed presentation labels, not quality scores or proof of distinct meanings.
5. Select “选择此条”. Confirm that the selection is for advisor review and has not been sent. Selection does not regenerate.
6. Use “下载本次运行记录 · JSON” and the “查看已提交输入与运行信息” expander to explain the submitted input and result. Native browser download is a manual browser step; automated verification only checks that the control is present.
7. If a field is edited after submission, the visible result still belongs to the previous submitted request. Submit again only if a new model run is intended.

Each intentional UI submission gets a fresh request ID. Use the recorded provider, `execution_kind`, model/run IDs and composition metadata to interpret provenance. The current download filename may contain “preview” even in live mode; the artifact contents and visible mode are authoritative.

## 3. Demonstrate the six scenarios

Default address: **林女士**; contact preference: “允许主动联系”; preferences: “偏爱岩灰色”. Scenario-specific deviations are listed below. The steps describe expected supported paths, not guaranteed actual model text.

| Order / scenario | Form setup and action | What to explain on a successful live result | One useful boundary to demonstrate |
| --- | --- | --- | --- |
| **1 — “生日与节日问候”** | Keep birthday. Submit once. Optionally switch “问候类型” to festival and enter “虚构示例节”. | The actual birthday/festival opening and address are source-bound; the model provides three wish bodies. No age or sales benefit is authorized. | Clear the festival name while festival is selected: clarification, zero candidates. |
| **2 — “产品推荐”** | Select **轻步斜挎包 / CX-B04**, use “周末出行”, keep budget **15000**. Fixture hard requirement remains crossbody carrying. | The known product colour/price, structure detail and dimensions are catalogue-derived; the model asks preference questions. No stock or wear-resistance promise follows from the catalogue. | Change budget to **500** and submit: the selected item cannot meet it; clarification, no provider call. Restore 15000 afterward. |
| **3 — “购后关怀”** | Select **循线肩包 / CX-B01**, purchase date **2026-10-20**; use the default general-care context. | Three care drafts should refer to supported guidance. A purchase date alone does not prove receipt. Review any service or care claims. | Simple form exposes general care only. Specific reported issues, prior assessment use and fuller service evidence require advanced JSON; do not infer service readiness from the simple controls. |
| **4 — “沉睡客户唤醒”** | Keep “了解近期偏好”, or deliberately choose “轻量关系问候”. Submit once. | This is a low-pressure reconnection, not a campaign trigger; avoid guilt about inactivity or invented reasons for absence. | Set “主动联系偏好” to “已拒绝主动联系”: blocked, zero sendable candidates. Restore permission before another success path. |
| **5 — “活动邀请”** | Keep **澄序皮具私享预览**, **2026-11-08**, and **澄序虚构示范精品店·二层会客区**. Form time is fixed at **14:00–17:00 Beijing time**. | Source-bound title/start/venue precede model-written invitation bodies. Attendance stays optional; no event gift, reservation or exclusivity is implied. | Empty the venue: clarification rather than invented location. Other times/eligibility/RSVP details require advanced JSON. |
| **6 — “价格异议”** | Select **循线肩包**, keep “要求折扣” and the client message “循线肩包有点超预算，可以打折吗？”. | The reply should address the actual concern and current no-negotiated-discount policy. Client-reported promises and channel prices are not independently verified facts. | Clear the client message: clarification. For comparisons, use a consistent client message and comparison record in advanced JSON, not only a changed dropdown. |

The care form currently contains a legacy caption saying dedicated service/issue handling is not implemented. It describes the limited simple-form controls; the shared backend and advanced contract do have care eligibility/issue fields. The recent-message box also collapses its content into one client-message record. Use advanced JSON for real multi-turn role/source distinctions. These are known presentation limitations, not reasons to invent additional form functionality.

## 4. Advanced JSON walkthrough

Separate inputs are under [examples/ui-demo](../../../examples/ui-demo/manifest.json). They contain requests only, not model outputs. For one example:

1. Select the scenario named in the file; keep the selector and JSON scenario consistent.
2. Switch to local live mode.
3. Open “高级输入 · 完整请求 JSON”. Check “本次使用下方 JSON，替代上面的表单输入”.
4. Paste the whole file, then submit. The checkbox is essential: without it, the simple form remains authoritative.
5. Review the outcome and source context. The UI replaces the file's sample request ID with a new ID on submission.
6. Uncheck advanced JSON before returning to the simple-form walkthrough. Each scenario remembers its own controls/result.

| Request file | Scenario | Expected service path |
| --- | --- | --- |
| [greeting.json](../../../examples/ui-demo/greeting.json) / [festival.json](../../../examples/ui-demo/festival.json) | Greeting | Eligible for generation with the exact supplied occasion |
| [product_recommendation.json](../../../examples/ui-demo/product_recommendation.json) | Recommendation | Eligible crossbody product within known budget |
| [post_purchase_care.json](../../../examples/ui-demo/post_purchase_care.json) | Care | Eligible general-care request |
| [reactivation.json](../../../examples/ui-demo/reactivation.json) | Reactivation | Eligible permitted proactive request |
| [event_invitation.json](../../../examples/ui-demo/event_invitation.json) | Invitation | Eligible future event under the demo business clock |
| [price_objection.json](../../../examples/ui-demo/price_objection.json) | Price | Eligible reply to the referenced client message |

Preview mode supports simple forms only. An advanced-JSON submission in preview displays a warning and does not exercise the real validator. A real model may return clarification/failure or weak copy even for an eligible request; the deterministic test-double success paths do not guarantee live model quality.

## 5. Non-success demonstration

Use live mode plus the matching advanced request. These preflight examples require no provider call, even though they use the live service path.

| Example / action | Expected outcome | What the UI should show |
| --- | --- | --- |
| [blocked-contact.json](../../../examples/ui-demo/blocked-contact.json) | `blocked` | No candidates; explanation of contact restriction |
| [unknown-permission.json](../../../examples/ui-demo/unknown-permission.json) | `needs_clarification` | No candidates; request to confirm permitted contact |
| [missing-venue.json](../../../examples/ui-demo/missing-venue.json) | `needs_clarification` | No candidates; missing event details |
| [over-budget.json](../../../examples/ui-demo/over-budget.json) | `needs_clarification` | No candidates; no supported product fit |
| [invalid-unknown-field.json](../../../examples/ui-demo/invalid-unknown-field.json) | `invalid_input` | No candidates; schema validation explanation |
| Paste `{broken` in the advanced editor | `invalid_input` | No candidates; invalid input after JSON parsing fails |
| Unavailable/missing local model or exhausted output checks | `generation_failed` | No fabricated drafts or automatic provider/template fallback |

The unavailable-model UI path is verified with an explicit simulated adapter failure, not by stopping the working shared server during the presentation. Incorrect environment configuration can instead show a configuration error before service execution; it is distinct from a saved generation failure.

## 6. Presenter close and verification limits

Close by showing that the same backend supports interactive drafting and scriptable evidence, while known facts, model language and human judgments remain distinct. Mention current care/price/context weaknesses without claiming acceptance. The preserved 50-case set is pending human scoring and is not being rerun for this walkthrough.

[Current isolated verification](../../verification/ui-demo-verification-2026-11-05.json) covers six preview paths, six explicit live-form success paths with labelled fake inference, selection/no-auto-generation, advanced non-success inputs and simulated provider failure. It uses temporary storage, blocks network inference and never contributes to real model-output counts. It does not verify browser visuals, native download behavior or actual model semantics. No walkthrough recording, hosted URL or browser-based visual review is claimed.
