"""Verified occasion framing around actual model-written wishes; no fallback."""
import re


def compose_greeting(parsed, request):
    if parsed.get('status') != 'generated':
        return parsed, None, []
    ctx = request['scenario_context']
    birthday = ctx['occasion_type'] == 'birthday'
    errors = []
    for i, body in enumerate(parsed['messages'], 1):
        if re.search(r'生日|节日|节庆|今天|明天|后天|\d+岁|[一二三四五六七八九十]+岁|亲爱的|宝子', body):
            errors.append(f'GREETING_BODY_SCOPE 候选{i}：只写一句简短祝愿，不写生日/节日开头、相对日期、年龄或亲昵称呼；程序添加已确认场景。')
        if not birthday and re.search(r'新的一岁|长大|成长一岁', body):
            errors.append(f'GREETING_BODY_SCOPE 候选{i}：这是节日祝福，不写年龄或新的一岁。')
    if errors:
        return parsed, None, errors
    occasion = '生日' if birthday else ctx['occasion_name']
    from .contracts import timestamp
    from datetime import date
    from zoneinfo import ZoneInfo
    supplied = ctx.get('occasion_date')
    early = bool(supplied and date.fromisoformat(supplied) > timestamp(request['reference_time']).astimezone(ZoneInfo(request['timezone'])).date())
    address = request['client'].get('preferred_address')
    frame = (address + '，' if address else '') + ('提前祝您' if early else '') + occasion + '快乐。'
    texts = [frame + body for body in parsed['messages']]
    meta = {'method':'verified-greeting-frame-v0.2','model_authored_bodies':parsed['messages'],
            'verified_frame':frame,'source_fields':['client.preferred_address','scenario_context.occasion_type','scenario_context.occasion_name'],
            'final_messages':texts}
    return {**parsed,'messages':texts},meta,[]
