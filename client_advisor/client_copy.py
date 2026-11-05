"""Transparent, narrow source framing and polite-pronoun normalization.

Only runs on a successfully parsed model result. Never supplies replacement
messages on provider failure. All transformations and original text are retained.
"""
import re
from .editorial import client_text


def compose_client_copy(parsed,request):
    if parsed.get('status')!='generated':return parsed,None,[]
    address=request['client'].get('preferred_address');original=list(parsed['messages']);texts=[];changes=[]
    inbound=client_text(request)
    discount=request['scenario']=='price_objection' and (request['scenario_context']['objection_type']=='discount_request' or bool(re.search(r'打折|[五八]折|折扣',inbound)))
    prior=discount and bool(re.search(r'(?:上次|之前|此前|先前|曾经).{0,15}(?:答应|承诺|优惠|折)|(?:答应|承诺).{0,10}(?:过|上次|之前)',inbound))
    for i,text in enumerate(original,1):
        before=text
        if address and text.startswith(address):text=text[len(address):].lstrip('，,：: ')
        text=re.sub(r'你(?!们)','您',text).replace('通通勤','通勤')
        additions=[]
        if prior and not re.search(r'(?:先前|上次|之前|此前|旧).{0,10}(?:优惠|承诺)|(?:优惠|承诺).{0,12}(?:核实|核对)',text):
            additions.append('关于您提到的先前优惠，还需要核对具体记录。')
        if discount and not re.search(r'(?:不|不能|无法|不会|不支持).{0,8}(?:折扣|打折|议价)|没有.{0,4}(?:折扣|议价)',text):
            additions.append('目前不提供议价折扣。')
        text=(address+'，' if address else '')+''.join(additions)+text
        texts.append(text)
        if text!=before:changes.append({'candidate_id':i,'before':before,'after':text,'source_additions':additions})
    meta={'method':'verified-client-copy-v0.1','original_messages':original,'source_fields':['client.preferred_address','scenario_context.objection_type','conversation_history','docs/brand-and-rules.md#br-02-pricing-and-discounts'],'transformations':changes,'final_messages':texts,'provider_failure_fallback':False}
    return {**parsed,'messages':texts},meta,[]
