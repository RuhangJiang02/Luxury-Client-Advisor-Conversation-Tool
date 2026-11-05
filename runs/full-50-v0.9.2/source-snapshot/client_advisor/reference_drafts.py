"""Evidence-bound reference copy for actual local model editing.

These references are program-authored, not model-written outputs. They are always
recorded before inference and never used as a provider-failure fallback.
"""
import re
from .context import resolved_products
from .editorial import client_text


def references(request, derived):
    scenario=request['scenario'];ctx=request['scenario_context'];text=client_text(request)
    products=resolved_products(derived['eligible_product_ids'])
    address=request['client'].get('preferred_address');prefix=address+'，' if address else ''
    if scenario=='greeting':
        return ['愿您顺心自在，平常日子里也常有让您开心的小事。','愿您留些时间做喜欢的事，忙碌之余也能好好放松。','愿接下来的日子多些轻松与欢喜，每天都有好心情。']
    if scenario=='product_recommendation':
        p=products[0];use=ctx.get('use_case') or ''
        if '电脑' in text:return ['您方便量一下电脑的长宽厚吗？','您会连同电脑保护套一起携带吗？','您通勤还需要同时带哪些物品？']
        if p['category']=='card_holder':return ['您平时大约会带多少张卡？','您希望常用卡单独放，还是和其他卡放在一起？','您通常把卡夹放在衣袋还是包里？']
        if p['category']=='wallet':return ['您平时大约需要带多少张卡？','您取用卡片时，更习惯怎样整理和查找？','您一般是随身拿着，还是放进包里？']
        if not use:return ['您主要想在什么场合使用？','您平时更习惯怎样携带包？','您通常需要带哪些随身物品？']
        return ['您平时出门主要带哪些随身物品？','您更习惯把常用物品单独放，还是集中收在一起？','您有没有经常携带、需要先核对尺寸的物品？']
    if scenario=='event_invitation':
        second=('如果您想看看'+products[0]['name']+'的'+('旋锁开合和可拆卸肩带' if '旋锁' in products[0]['detail'] else products[0]['detail'])+'，可以来这次活动了解一下。') if products else '您那天方便参加吗？如果时间不合适，也没关系。'
        return ['有兴趣参加的话，直接回复我就好。',second,'您按自己的安排决定是否参加就好，不必特意调整时间。']
    p=products[0] if products else None;name=p['name'] if p else '皮具'
    if scenario=='post_purchase_care':
        if ctx['care_topic']=='reported_issue':
            if '水' not in text:
                return [prefix+'关于您提到的情况，方便说说目前皮具表面有哪些变化吗？仅凭描述还不能确认原因或处理效果。', prefix+'仅凭描述不能保证没有影响。您可以先把具体情况告诉我，再了解下一步，不先承诺修复效果。', prefix+'如果您想了解日常养护，可以用干净柔软的干布轻拭；具体异常还需先了解情况，不能据此保证没有影响。']
            second=('仅凭描述还不能保证没有影响。如想进一步确认，您这次购买尚有一次免费在店目视评估可用，需预约；不包含清洗或维修。' if derived['assessment_eligible'] is True else '仅凭描述还不能保证没有影响。如果您担心，可以先说说目前表面有没有明显变化，我们再了解具体情况。')
            return [prefix+'包刚碰到水，可以先用干净柔软的干布轻拭。仅凭描述还不能确认是否有影响，暂时也不能保证没有影响。',prefix+second,prefix+'现在包面还有水迹或明显变化吗？可以先用干净柔软的干布轻拭；仅凭描述，我不能保证没有影响。']
        not_received=bool(re.search(r'(?:还没|尚未|还未)收到',text))
        timing='收到后，' if not_received else ''
        first=f'关于您的{name}，使用或养护上有什么想了解的，都可以告诉我。'
        second=timing+f'{name}日常清洁可以用干净柔软的干布轻拭，尽量避免接触水、油和香水。'
        third=timing+f'{name}暂不使用时，保持干燥，放入随附防尘袋，并避免长时间日晒就好。'
        if ctx['care_topic']=='usage_check':
            first=f'关于您的{name}，有没有想了解的使用细节？方便时告诉我就好。'
            second=timing+f'如果您想了解{name}的日常清洁，可以用干净柔软的干布轻拭；有清洁方面的问题也可以告诉我。'
            third=timing+f'如果您想了解{name}的存放，暂不使用时保持干燥、放入随附防尘袋即可，避免长时间日晒。'
        return [prefix+t for t in [first,second,third]]
    if scenario=='reactivation':
        if re.search(r'不用催|不(?:要|用).{0,3}催|有问题我会',text):
            return [prefix+'明白，按您的节奏就好，我这边先不继续推介了。',prefix+'有问题时您再来问就好，不用为这条消息特意回复。',prefix+'好的，那先不打扰您了，之后是否再聊由您决定。']
        prefs=request['client']['preferences'];colour=next((c for c in ['岩灰','栗棕','墨黑','砂白'] if any(c in v for v in prefs)),None)
        question=f'您现在还是更喜欢{colour}色，还是有了别的颜色偏好？' if colour else '您平时挑选皮具时，喜欢什么颜色？'
        first='来向您问个好，愿您近来一切顺心。'
        third='不用为这条问候特意回复；之后想聊皮具时，您再联系我就好。'
        if ctx['reconnect_purpose']=='relationship_check_in':question='最近还好吗？只是来问候您，不聊购买的事，您方便时再回就好。'
        if '先不考虑' in text:
            first='上次那款先不考虑就好，不用急着决定。这次只是来问候您，愿您一切顺心。'
            question='先不聊上次那款了。'+question
        return [prefix+t for t in [first,question,third]]
    if scenario=='price_objection':
        from .recommendation_composition import structure_fact
        structure=structure_fact(p)
        price=f'{p["price"]}元';material=p['detail'].split('、')[0].split('，')[0];detail=p['detail'];discount=ctx['objection_type']=='discount_request' or bool(re.search(r'打折|[五八]折|折扣',text))
        if re.search(r'不要催|再想想|再考虑|考虑一下|想一想',text) and not discount:
            out=['可以的，您慢慢考虑就好。','不需要急着决定，按您自己的节奏来。','我这边先不继续推介了，之后想了解时您再联系我就好。']
        elif ctx['objection_type']=='comparison' and re.search(r'信息|介绍|讲讲|材质|细节',text):
            dims=' × '.join(f'{v:g}' for v in p['dimensions_cm'])
            out=[f'{name}采用{material}，目录价{price}。对方报价的具体条件还未核实，暂时无法判断差价原因。',f'{name}的设计细节是{structure}。可以先对照这些细节考虑用途；别处报价条件未核实，差价原因还不能确认。',f'{name}外部尺寸是{dims}厘米，可以先对照您常带的物品。对方报价条件还不清楚，您可以慢慢比较，不急着决定。']
        elif ctx['objection_type']=='comparison':
            comp=ctx.get('comparison');reported=f"您提到{comp['reported_seller']}报价{comp['reported_amount']:g}元，" if comp else '您提到别处报价更低，'
            out=[reported+f'这里{name}的目录价是{price}。对方报价条件还没核实，目前无法判断差价原因。','目前还不清楚对方报价包含哪些条件，暂时不能解释差价。您愿意的话，可以把具体报价条件发给我，先对照清楚。','两边报价条件是否一致还未确认，不能据此判断真假或质量。您可以慢慢比较，不必急着决定。']
        elif re.search(r'上次|答应|承诺',text) and discount:
            material=p['detail'].split('、')[0].split('，')[0]
            out=[f'您提到的之前优惠还需要核实，目前不能确认。{name}目录价{price}，不提供议价折扣。',f'您提到的旧优惠需要先核对记录，目前不提供议价折扣。供您了解，{name}采用{material}。','您对先前优惠的疑问还需要核实，目前不提供议价折扣。您可以慢慢考虑，不必急着决定。']
        elif re.search(r'预算|一万五|15000',text):
            match=re.search(r'预算(?:只有|是|为|大约|约|最多)?\s*([一二两三四五六七八九十百千万零点\d.,]+)',text)
            amount=match.group(1)+'元' if match else None
            boundary=f'您{amount}的预算' if amount else '您提到的预算'
            out=[f'{name}目录价{price}，确实超出了{boundary}，不用勉强增加预算。',f'先以{boundary}为界，不急着选款。您平时主要想在什么场合使用？我们先把用途了解清楚。',f'这款超出了{boundary}，可以先不选。之后是否继续看，按您的节奏就好。']
        elif re.search(r'卡夹.*肩包|需要.*肩包',text):
            out=[f'您需要的是肩包，不能只因为卡夹价格低就换成卡夹。{name}目录价{price}，可以先按肩包的用途来考虑。','肩包的用途先保留，不用为了价格改选卡夹。您希望把预算控制在多少？先了解清楚，再看是否继续比较。','卡夹不能替代您需要的肩包用途。这次可以先不决定，等功能和预算都适合自己时再考虑就好。']
        elif discount:
            material=p['detail'].split('、')[0].split('，')[0]
            out=[f'关于折扣，{name}目录价{price}，不提供议价折扣。您可以先按这个价格考虑。',f'这款不提供议价折扣。供您了解，{name}采用{material}，您可以结合实际需要判断是否继续考虑。','目前不提供议价折扣，您可以慢慢考虑，不必急着决定。']
        else:
            out=[f'这笔花费需要慎重考虑，{name}目录价{price}。您可以先看看是否符合自己的预算，不用急着决定。',f'{name}的设计包括{detail}。若想判断是否符合您的需要，您平时使用皮具最看重什么？','先按自己的用途和预算考虑就好，不必为了这次选款勉强决定。暂时不选也没关系。']
        return [prefix+t for t in out]
    raise ValueError('Unsupported scenario')
