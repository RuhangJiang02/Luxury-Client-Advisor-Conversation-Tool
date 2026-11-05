"""Compose verified event logistics with real model-authored invitation bodies.

This is explicit structured composition, never a fallback for failed inference.
"""
import re
from zoneinfo import ZoneInfo
from .contracts import timestamp


def compose_event(parsed, request):
    if parsed.get('status') != 'generated':
        return parsed, None, []
    bodies = parsed['messages']
    errors = []
    for i, body in enumerate(bodies, 1):
        if re.search(r'\d|[一二三四五六七八九十]+[月日点]|如上|上述|上面|时间地点', body):
            errors.append(f'EVENT_BODY_SCOPE 候选{i}：只写邀请角度，不写日期时间或引用其他候选；活动信息由程序添加。')
        if request['scenario_context']['title'] in body or request['scenario_context']['venue'] in body:
            errors.append(f'EVENT_BODY_SCOPE 候选{i}：只写简短邀请句，不重复活动名称或地点。')
    if errors:
        return parsed, None, errors
    ctx = request['scenario_context']
    start = timestamp(ctx['starts_at']).astimezone(ZoneInfo(request['timezone']))
    address = request['client'].get('preferred_address')
    frame = (address + '，' if address else '') + f"{start.month}月{start.day}日{start:%H:%M}想邀请您参加{ctx['title']}，地点是{ctx['venue']}。"
    if ctx.get('rsvp_deadline'):
        deadline=timestamp(ctx['rsvp_deadline']).astimezone(ZoneInfo(request['timezone']))
        frame+=f'如想参加，请在{deadline.month}月{deadline.day}日{deadline:%H:%M}前回复我。'
    messages = [frame + body for body in bodies]
    evidence = {'method': 'verified-event-frame-v0.2', 'model_authored_bodies': bodies,
                'verified_frame': frame, 'source_id': ctx['source_id'],
                'source_fields': ['client.preferred_address', 'scenario_context.title', 'scenario_context.starts_at', 'timezone', 'scenario_context.venue', 'scenario_context.rsvp_deadline'],
                'final_messages': messages}
    return {**parsed, 'messages': messages}, evidence, []
