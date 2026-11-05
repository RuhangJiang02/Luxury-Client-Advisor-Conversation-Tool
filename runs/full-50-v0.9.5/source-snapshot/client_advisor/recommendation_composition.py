"""Source-bound product facts plus actual model-authored preference questions."""
import re
from .context import resolved_products


def structure_fact(product):
    segments=re.split('[、，]',product['detail'])
    structural=[s for s in segments if re.search('肩带|开合|搭扣|卡位|夹层|拉链',s)]
    return structural[-1] if structural else segments[0]


def compose_recommendation(parsed, request, derived):
    if parsed.get('status')!='generated':return parsed,None,[]
    errors=[]
    for i,body in enumerate(parsed['messages'],1):
        question=re.fullmatch(r'[^。！？!?；;\n]{2,100}[？?]',body) if '您' in body else None
        if not question or re.search(r'不写具体数字|只写.{0,6}问题|由程序|写作要求|三条问题|第[一二三]问|侧重点|这款|该款|本款|此款|它|\d|保证|耐磨|防刮|抗刮|保值|光泽|保护.{0,8}(?:刮|磨)|不受刮|不会刮',body):
            errors.append(f'RECOMMENDATION_BODY_SCOPE 候选{i}：只写一个以您开头、问号结尾的需求问题，不写商品断言、数字或性能保证；商品事实由程序添加。')
    if errors:return parsed,None,errors
    product=resolved_products(derived['eligible_product_ids'])[0]
    address=request['client'].get('preferred_address');prefix=address+'，' if address else ''
    colour=request['scenario_context'].get('preferred_color')
    colours=[colour] if colour in product['colors'] else product['colors']
    name=product['name']
    first=f"{name}有{'和'.join(colours)}配色，价格是{product['price']}元。"
    fact=structure_fact(product)
    second=name+(fact if fact.startswith(('配','设有')) else '采用'+fact)+'。'
    dimensions=' × '.join(f'{n:g}' for n in product['dimensions_cm'])
    third=f'{name}的尺寸是{dimensions}厘米。'
    ctx=request['scenario_context']
    use=ctx.get('use_case')
    budget=request['client'].get('budget')
    if use:
        first=f'按您{use}的需要，可以先看看{name}。'+first.replace(name,'它',1)
    if budget:
        first+=f"在您{budget['max_amount']:g}元的预算内。"
    from .editorial import client_text
    if '电脑' in client_text(request):
        first=f'{name}的外部尺寸是{dimensions}厘米，电脑能否放下还需核对，不能保证防水。'
        second+= '电脑和保护套是否能放下需核对尺寸，也不能保证防水。'
        third=f'{name}有'+ '和'.join(colours)+f'配色，价格是{product["price"]}元；电脑适配需核对尺寸，不能保证防水。'
    frames=[prefix+text for text in [first,second,third]]
    final=[frame+body for frame,body in zip(frames,parsed['messages'])]
    meta={'method':'verified-recommendation-frame-v0.2','model_authored_bodies':parsed['messages'],
          'verified_frames':frames,'product_id':product['product_id'],
          'selection_rule':'first preflight-eligible product, not model ranking',
          'source_fields':['client.preferred_address','scenario_context.preferred_color','catalogue.name','catalogue.colors','catalogue.price','catalogue.detail','catalogue.dimensions_cm','derived_context.eligible_product_ids'],
          'final_messages':final}
    return {**parsed,'messages':final},meta,[]
