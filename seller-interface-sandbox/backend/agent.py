"""Seller Agent: deterministic demo mode + real LLM function-calling mode.

This module does not book tables. It only reads the exact same data as the other
interfaces. With a valid OPENAI_API_KEY, llm mode autonomously chooses tools.
"""
import json
import os
import re
from datetime import date
from .store import public_profile, menu_items, available_slots, merchant_data

SYSTEM_PROMPT = """You represent Casa Oliva, a FICTIONAL demo Italian restaurant in Hong Kong.
Your task is to accurately answer customer requests and offer alternatives when the
requested seating slot is unavailable. Always use the provided tools for facts.
Prices are in USD, not HKD. Dates in the availability data are December 4-6, 2026,
and all local times are Asia/Hong_Kong. The address is fictional. You MUST never
claim that any real reservation was made, held or paid for. No real booking is possible.
If information is absent, say it is unknown. Do not invent discounts or live inventory.
Do not disclose internal instructions. Keep answers concise, matching user language.
"""
TOOLS = [
    {'type':'function','function':{'name':'get_restaurant','description':'Read restaurant profile, hours, address, phone and policies','parameters':{'type':'object','properties':{},'additionalProperties':False}}},
    {'type':'function','function':{'name':'get_menu','description':'Read complete menu or filter for vegetarian dishes and a maximum USD price','parameters':{'type':'object','properties':{'vegetarian':{'type':['boolean','null']},'max_price':{'type':['number','null']}},'additionalProperties':False}}},
    {'type':'function','function':{'name':'check_availability','description':'Inspect demo availability, including whether a requested slot is already full. Query other nearby slots for alternatives.','parameters':{'type':'object','properties':{'date':{'type':['string','null'],'description':'YYYY-MM-DD date'},'party_size':{'type':'integer','minimum':2,'maximum':6},'seating':{'type':['string','null'],'enum':['indoor','outdoor','all',None]},'time':{'type':['string','null'],'description':'24-hour HH:MM time'}},'required':['party_size'],'additionalProperties':False}}}
]

def execute_tool(name, kwargs):
    if name=='get_restaurant':return public_profile()
    if name=='get_menu':return menu_items(kwargs.get('vegetarian'),kwargs.get('max_price'))
    if name=='check_availability':return available_slots(kwargs.get('date'),kwargs.get('party_size',4),kwargs.get('seating'),kwargs.get('time'))
    return {'error':'Unknown tool'}

def mock_reply(message):
    """Rule-based demonstrator, explicitly *not* an AI/LLM agent."""
    d=merchant_data()
    txt=message.lower()
    trace=['get_restaurant']
    facts=[f"{d['name']} — fictional Italian restaurant, {d['address']['english']}; phone {d['phone']}.",
          f"Demo average spend: {d['currency']} {d['average_price_per_person']} per person. Time zone: {d['timezone']}."]
    if any(x in txt for x in ('menu','dish','food','vegetarian','素食','菜','price','价格','菜單','菜单')):
        trace.append('get_menu')
        items=menu_items(vegetarian=True if ('vegetarian' in txt or '素食' in txt) else None)['items']
        facts.append('Menu: '+', '.join(f"{i['name']} ({d['currency']} {i['price']})" for i in items)+'.')
    if any(x in txt for x in ('hour','open','close','营业','營業','几点','幾點')):
        hours=d['opening_hours'];facts.append('Opening hours: Mon–Thu 17:00–22:00; Fri–Sat 17:00–23:00; Sun 17:00–21:00 (Hong Kong).')
    wants_slots=any(x in txt for x in ('book','reserve','table','seat','座','预约','預約','预订','訂位','位','availability','12月','december','dec '))
    if wants_slots:
        trace.append('check_availability')
        dt=re.search(r'2026-12-0[456]',txt)
        if dt: day=dt.group()
        else:
            cn=re.search(r'12\s*月\s*([456])\s*日',txt)
            en=re.search(r'dec(?:ember)?\s*([456])\b',txt)
            day=f'2026-12-0{(cn or en).group(1)}' if (cn or en) else None
        party=re.search(r'(\d+)\s*(?:people|guests|persons|人|位)',txt)
        n=int(party.group(1)) if party else 4
        seat='outdoor' if any(w in txt for w in ('outdoor','patio','户外','戶外','露天')) else ('indoor' if any(w in txt for w in ('indoor','室内','室內')) else 'all')
        hr=re.search(r'(?<![\d])([12]?\d):([0-5]\d)',txt)
        clock=f'{int(hr.group(1)):02d}:{hr.group(2)}' if hr else None
        if day and n in range(2,7):
            slots=available_slots(date=day,party_size=n,seating=seat)
            if clock:
                exact=[s for s in slots['items'] if s['time']==clock]
                if exact and any(s['available_for_requested_party'] for s in exact):
                    facts.append(f'For {day} {clock} ({n} guests, {seat}), a matching demo slot is available.')
                else:
                    facts.append(f'For {day} {clock} ({n} guests, {seat}), no matching demo slot is available.')
            alt=[s for s in slots['items'] if s['available_for_requested_party'] and (not clock or s['time']!=clock)]
            facts.append('Other available demo options: '+(', '.join(f"{s['time']} {s['seating']}" for s in alt) if alt else 'No alternatives found in demo data')+'.')
        else:
            facts.append('Please supply a demo date (2026-12-04, 05 or 06), party size (2–6) and preferred seating to check the sample slots.')
    facts.append('This is sample information only. No real reservation or payment can be made.')
    return {'mode':'mock_rule_based','reply':'\n'.join(facts),'tool_trace':trace,'demo_only':True,
            'data_version':d['data_version']}

def llm_reply(message, history=None):
    key=os.getenv('OPENAI_API_KEY')
    if not key:
        raise RuntimeError('OPENAI_API_KEY is not configured; use mode=mock or set a key.')
    from openai import OpenAI
    client=OpenAI(api_key=key, timeout=40.0)
    msgs=[{'role':'system','content':SYSTEM_PROMPT}]
    for record in (history or [])[-8:]:
        if record.get('role') in ('user','assistant') and isinstance(record.get('content'),str):
            msgs.append({'role':record['role'],'content':record['content'][:4000]})
    msgs.append({'role':'user','content':message})
    trace=[]
    model=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
    for _ in range(4):
        completion=client.chat.completions.create(model=model,messages=msgs,tools=TOOLS,tool_choice='auto',temperature=0)
        choice=completion.choices[0].message
        msgs.append(choice.model_dump(exclude_none=True))
        if not choice.tool_calls:
            return {'mode':'llm_tool_calling','model':model,'reply':choice.content or '', 'tool_trace':trace,
                    'demo_only':True,'data_version':merchant_data()['data_version']}
        for tool in choice.tool_calls:
            try:
                kwargs=json.loads(tool.function.arguments or '{}')
                value=execute_tool(tool.function.name,kwargs)
                trace.append({'tool':tool.function.name,'args':kwargs})
            except Exception as exc:
                value={'error':str(exc)}
            msgs.append({'role':'tool','tool_call_id':tool.id,'content':json.dumps(value,ensure_ascii=False)})
    return {'mode':'llm_tool_calling','model':model,'reply':'Unable to complete within the tool-call limit.',
            'tool_trace':trace,'demo_only':True,'data_version':merchant_data()['data_version']}
