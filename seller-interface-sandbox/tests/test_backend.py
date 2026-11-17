from fastapi.testclient import TestClient
from backend.app import app
from backend.store import merchant_data

client=TestClient(app)

def test_facts_and_phone():
    r=client.get('/api/restaurant')
    assert r.status_code==200
    assert r.json()['phone']=='+852 6849 1948'
    assert r.json()['address']['english']=='2/F, 18 Olive Lane, Central, Hong Kong'
    assert 'menu' not in r.json() and 'availability' not in r.json()

def test_menu_and_currency():
    r=client.get('/api/menu')
    assert r.status_code==200 and r.json()['count']==6
    assert r.json()['currency']=='USD'
    assert [m['price'] for m in r.json()['items']]==[19,29,22,27,34,13]

def test_availability_full_and_alternative():
    r=client.get('/api/availability',params={'date':'2026-12-04','party_size':4,'seating':'outdoor','time':'19:00'})
    assert r.status_code==200 and r.json()['available_count']==0
    slot=r.json()['items'][0]
    assert slot['max_party_size']==0 and not slot['available_for_requested_party']
    r2=client.get('/api/availability',params={'date':'2026-12-04','party_size':4,'seating':'outdoor'})
    options=[slot['time'] for slot in r2.json()['items'] if slot['available_for_requested_party']]
    assert options==['18:30','20:00']

def test_slot_count_matches_html():
    d=merchant_data()
    assert len(d['availability'])==16
    assert d['timezone']=='Asia/Hong_Kong'

def test_rule_based_agent_disclaims_real_booking():
    r=client.post('/agent/message',json={'mode':'mock','message':'2026-12-04 19:00，4人，户外有位置吗？'})
    assert r.status_code==200
    result=r.json()
    assert result['mode']=='mock_rule_based'
    assert 'no matching demo slot' in result['reply']
    assert '18:30' in result['reply']
    assert 'No real reservation' in result['reply']

def test_missing_key_returns_error(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    r=client.post('/agent/message',json={'mode':'llm','message':'Hello'})
    assert r.status_code==503

def test_demo_page():
    r=client.get('/demo')
    assert r.status_code==200
    assert 'Run Experiment' in r.text
