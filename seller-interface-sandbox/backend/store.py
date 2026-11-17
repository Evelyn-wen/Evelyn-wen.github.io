"""Authoritative, versioned demo data shared by the API and Seller Agent."""
import json
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).resolve().parent.parent / 'data' / 'merchant.json'

def merchant_data():
    return json.loads(DATA_PATH.read_text(encoding='utf-8'))

def public_profile():
    d=merchant_data()
    omit={'menu','availability'}
    return {k:v for k,v in d.items() if k not in omit}

def menu_items(vegetarian: Optional[bool] = None, max_price: Optional[float] = None):
    d=merchant_data()
    result=d['menu']
    if vegetarian is not None:
        result=[m for m in result if ('vegetarian' in m['dietary_note'].lower()) == vegetarian]
    if max_price is not None:
        result=[m for m in result if m['price']<=max_price]
    return {'currency':d['currency'],'data_version':d['data_version'],'items':result,'count':len(result)}

def available_slots(date: Optional[str]=None, party_size: int=4, seating: Optional[str]=None, time: Optional[str]=None):
    if party_size < 2 or party_size > 6:
        raise ValueError('Party size must be between 2 and 6 in the demo')
    if seating not in (None, 'indoor', 'outdoor', 'all'):
        raise ValueError('seating must be indoor, outdoor, or all')
    d=merchant_data()
    items=[]
    for slot in d['availability']:
        if date is not None and date != slot['date']: continue
        if time is not None and time != slot['time']: continue
        if seating not in (None, 'all') and seating != slot['seating']: continue
        can=slot['max_party_size'] >= party_size
        items.append({**slot,'available_for_requested_party':can})
    return {'data_version':d['data_version'], 'date':date, 'party_size':party_size,
            'seating':seating, 'time':time, 'items':items,
            'available_count':sum(s['available_for_requested_party'] for s in items),
            'demo_only':True}
