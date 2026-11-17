"""Buyer Agent v0.1 interface smoke tests without network or an API key."""
from fastapi.testclient import TestClient
from backend.app import app

client=TestClient(app)
TASK='2026-12-04 19:00，4人，户外有座位吗？请给出替代时段。'


def test_buyer_four_interfaces_same_demo_outcome():
    expected={'website':1,'js':1,'api':3,'seller_agent':1}
    for interface,n in expected.items():
        res=client.post('/buyer/run',json={'task':TASK,'interface':interface,'buyer_mode':'mock'})
        assert res.status_code==200, (interface,res.text)
        data=res.json()
        assert data['request_count']==n
        assert len(data['requests'])==n
        assert all(x['status']==200 for x in data['requests'])
        assert '18:30' in data['answer'] and '20:00' in data['answer']
        assert 'demo_only' in data
        assert data['token_usage'] is None
        assert data['buyer_mode']=='mock_rule_based_not_llm'


def test_buyer_second_date_available():
    for interface in ['website','js','api','seller_agent']:
        res=client.post('/buyer/run',json={
            'task':'2026-12-06 19:00，4人，户外有座位吗？',
            'interface':interface,'buyer_mode':'mock'})
        assert res.status_code==200
        if interface!='seller_agent':
            assert '可满足需求' in res.json()['answer']
        else:
            assert 'a matching demo slot is available' in res.json()['answer']


def test_buyer_lacks_date_requests_clarification():
    result=client.post('/buyer/run',json={'task':'Can I book a table?','interface':'website','buyer_mode':'mock'})
    assert result.status_code==200
    assert '仅支持明确的日期' in result.json()['answer']


def test_missing_key_for_llm_buyer(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    result=client.post('/buyer/run',json={'task':TASK,'interface':'js','buyer_mode':'llm'})
    assert result.status_code==503
    assert 'OPENAI_API_KEY' in result.json()['detail']


def test_local_http_source_routes():
    html=client.get('/seller/website')
    js=client.get('/seller/js-file/merchant.js')
    assert html.status_code==200 and 'availability-table' in html.text
    assert js.status_code==200 and 'Object.freeze' in js.text
    assert 'Casa Oliva' in html.text and 'Casa Oliva' in js.text


def test_dashboard_has_buyer_control():
    page=client.get('/demo')
    assert page.status_code==200
    assert 'buyer-controls' in page.text
    assert 'buyer-interface' in page.text
    assert '/buyer/run' in page.text
