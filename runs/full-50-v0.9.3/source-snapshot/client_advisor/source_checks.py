"""Targeted source checks for observed major defects, not semantic proof."""
import re
from .contracts import timestamp
from .context import resolved_products

PROPERTIES = re.compile(r'耐磨|抗刮|防刮|防水|保值|光泽|触感细腻|更细腻|更加柔软|更耐用')
PRIOR_PROMISE = re.compile(r'(?:我们|本店|我)(?:在)?(?:上次|之前|此前|曾经|曾)?[^。；，!?]{0,10}(?:提到|答应|承诺|说过|说好|给过)[^。；，!?]{0,10}(?:八折|折扣|优惠)|(?:上次|之前|此前)(?:我们|我|本店)[^。；，!?]{0,10}(?:八折|折扣|优惠)')


def affirmations(text, pattern):
    for clause in re.split(r'[。；，!?！？\n]|但是|不过|但',text):
        for match in pattern.finditer(clause):
            before=clause[:match.start()]
            if re.search(r'无法确认|未确认|不保证|不能保证|不能确认|不确定|尚无|没有|不具备|不能说|您说|您提到|您所说|客户说|如果|假如|若',before):
                continue
            yield match.group(0)


def check_sources(parsed, request):
    if parsed.get('status') != 'generated':return []
    errors=[]
    # None of the approved baseline catalogue items establish these properties.
    advisor_evidence=any(m['role']=='advisor' and list(affirmations(m['text'],PRIOR_PROMISE)) for m in request['conversation_history'])
    for i,text in enumerate(parsed['messages'],1):
        if request['scenario'] in {'product_recommendation','price_objection','event_invitation'} and list(affirmations(text,PROPERTIES)):
            errors.append(f'GROUNDING_MATERIAL_PROPERTY 候选{i}：目录未确立耐磨、防刮、防水、保值、光泽或手感性能，只陈述已给材质/结构事实，不推导性能。')
        if request['scenario']=='product_recommendation':
            methods={method for p in resolved_products(request['product_ids']) for method in p['carrying_methods']}
            if '双肩' in text and 'backpack' not in methods:
                errors.append(f'GROUNDING_CARRY_METHOD 候选{i}：所选商品没有已确认双肩背法，不推荐或声称可双肩携带；只用所给背法。')
        if request['scenario']=='price_objection' and not advisor_evidence and list(affirmations(text,PRIOR_PROMISE)):
            errors.append(f'GROUNDING_DISCOUNT_HISTORY 候选{i}：只有客户说法，没有顾问曾承诺折扣的记录。不能写我们上次提到/答应优惠；可说您提到的优惠尚未核实，并说明当前政策。')
        if re.search(r'唯一(?:能|可)(?:以)?提供.{0,6}材质|仅(?:有|能提供).{0,6}(?:材质|款式)|收到后/以后|挂载|我们已明确说明',text):
            errors.append(f'EDITORIAL_UNSUPPORTED_OR_UNEDITED 候选{i}：删除无依据的唯一供应说法、未整理的分支或生硬术语，直接回应当前问题。')
        if re.match(r'^您[，,]',text):
            errors.append(f'EDITORIAL_PRONOUN_VOCATIVE 候选{i}：称呼未知直接进入正文，不写“您，”作为称呼。')
        if request['scenario']=='price_objection' and re.search(r'之前优惠|旧优惠|先前优惠',text):
            history=' '.join(m['text'] for m in request['conversation_history'])
            if not re.search(r'上次|之前|此前|先前|曾经',history):
                errors.append(f'GROUNDING_PRIOR_OFFER_CONTEXT 候选{i}：客户没有提到历史优惠，不能把当前折扣请求写成先前优惠待核实。')
        if request['scenario']=='greeting':
            ctx=request['scenario_context']
            if ctx['occasion_type']=='birthday':
                if '生日' not in text or re.search(r'节日快乐|节日愉快|节庆快乐',text):
                    errors.append(f'GREETING_OCCASION 候选{i}：每条明确祝生日快乐，不写节日快乐。')
            elif ctx['occasion_name'] not in text or '生日' in text:
                errors.append(f'GREETING_OCCASION 候选{i}：使用已给节日名称，不串入生日。')
            for word,delta in [('今天',0),('明天',1),('后天',2)]:
                if word in text:
                    from datetime import date, timedelta
                    supplied=ctx.get('occasion_date')
                    if not supplied or date.fromisoformat(supplied)!=timestamp(request['reference_time']).date()+timedelta(days=delta):
                        errors.append(f'GREETING_DATE 候选{i}：没有与{word}对应的场合日期依据，省略相对日期。')
    return errors
