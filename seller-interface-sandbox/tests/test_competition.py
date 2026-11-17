"""No paid provider calls. Tests validate the entire local competition path."""
import asyncio
import json
from pathlib import Path

import httpx
from backend.app import app
from backend.competition import SELLERS, seller_data, _verify_pricing


def call(method,path,**kwargs):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test.local') as c:
            return await c.request(method,path,**kwargs)
    return asyncio.run(run())


def test_two_seller_names_and_inventory():
    d1=seller_data('oliva');d2=seller_data('verde')
    assert d1['name']=='Casa Oliva' and d2['name']=='Casa Verde'
    assert len(d1['menu'])==len(d2['menu'])==6
    assert len(d1['availability'])==len(d2['availability'])==16
    assert d1['currency']==d2['currency']=='USD'
    assert d1['menu']!=d2['menu']
    assert d1['availability']==d2['availability']


def test_seller_resource_paths_are_genuinely_distinct():
    for seller in SELLERS:
        html=call('GET',f'/competition/website/{seller}')
        assert html.status_code==200
        assert SELLERS[seller]['name'] in html.text
        assert 'menu' in html.text.lower()
        src=call('GET',f'/competition/js/{seller}')
        assert src.status_code==200
        assert 'Object.freeze' in src.text
        profile=call('GET',f'/competition/api/{seller}/profile')
        menu=call('GET',f'/competition/api/{seller}/menu')
        assert profile.json()['name']==SELLERS[seller]['name']
        assert menu.json()['count']==6
        agent=call('POST',f'/competition/agent/{seller}',json={'mode':'mock','message':'What is on your menu?'})
        assert agent.status_code==200
        assert agent.json()['menu']['count']==6
        assert agent.json()['mode']=='mock_not_llm'


def test_info_parity_same_merchant_across_four_interfaces():
    from backend.competition import _extract_js_text
    for seller in SELLERS:
        d=seller_data(seller)
        js=json.loads(_extract_js_text(call('GET',f'/competition/js/{seller}').text))
        api=call('GET',f'/competition/api/{seller}/menu').json()
        agent=call('POST',f'/competition/agent/{seller}',json={'mode':'mock','message':'menu'}).json()
        assert d['menu']==js['menu']==api['items']==agent['menu']['items']
        from bs4 import BeautifulSoup
        visible=BeautifulSoup(call('GET',f'/competition/website/{seller}').text,'html.parser').get_text(' ',strip=True)
        assert all(i['name'] in visible for i in d['menu'])


def test_all_16_competition_pairings_mock_transport():
    ids=('website','js','api','seller_agent')
    for a in ids:
        for b in ids:
            rsp=call('POST','/competition/run',json={
                'preference':'喜欢蘑菇和芝士，至少两道菜，两人',
                'budget_usd':75,'party_size':2,
                'oliva_interface':a,'verde_interface':b,
                'buyer_mode':'mock','seller_mode':'mock'})
            assert rsp.status_code==200,(a,b,rsp.text[:400])
            result=rsp.json()
            assert result['decision']['selected_seller'] in ('oliva','verde')
            assert result['pricing_check']['verified'] is True
            assert result['pricing_check']['within_budget'] is True
            assert result['buyer_mode']=='mock_control_not_interface_sensitive'
            expected=(1 if a in ('website','js','seller_agent') else 2)+(1 if b in ('website','js','seller_agent') else 2)
            assert result['request_count']==expected


def test_price_verifier_rejects_invented_dishes():
    check=_verify_pricing({'selected_seller':'verde','chosen_dish_names':['Imaginary Pasta'],'estimated_total_usd':1})
    assert not check['verified']
    good=_verify_pricing({'selected_seller':'oliva','chosen_dish_names':['Margherita Pizza','Wild Mushroom Tagliatelle'],'estimated_total_usd':51})
    assert good['verified'] and good['sum_usd']==51 and good['matches_stated_total']


def test_missing_key_returns_safe_json(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    resp=call('POST','/competition/run',json={
        'preference':'请比较两家店，喜欢蘑菇和芝士',
        'budget_usd':75,'party_size':2,
        'oliva_interface':'website','verde_interface':'js',
        'buyer_mode':'llm','seller_mode':'mock'})
    assert resp.status_code==503
    assert 'OPENAI_API_KEY' in str(resp.json())


def test_page_has_competition_ui_and_original_interfaces():
    resp=call('GET','/demo')
    assert resp.status_code==200
    for value in ['controls-competition','oliva-interface','verde-interface','competition-budget','competition-run',
                  'controls-website','controls-js','controls-api','controls-agent','buyer-controls']:
        assert value in resp.text
    assert call('GET','/seller/website').status_code==200
    assert call('GET','/seller/js-file/merchant.js').status_code==200


def test_order_switch_and_budget_validation():
    rsp=call('POST','/competition/run',json={'preference':'喜欢披萨，越便宜越好','budget_usd':40,'party_size':2,
        'oliva_interface':'api','verde_interface':'website','presentation_order':'verde_first','buyer_mode':'mock'})
    assert rsp.status_code==200 and rsp.json()['conditions']['presentation_order']=='verde_first'
    assert rsp.json()['requests'][0]['seller']=='verde'
    bad=call('POST','/competition/run',json={'preference':'预算','budget_usd':-20})
    assert bad.status_code==422


def test_llm_buyer_response_with_fake_sdk(monkeypatch):
    """Validate provider integration without a secret or real paid request."""
    import sys
    from types import SimpleNamespace
    import backend.competition as comp
    monkeypatch.setenv('OPENAI_API_KEY','TEST_ONLY_NEVER_A_REAL_CREDENTIAL')
    monkeypatch.setenv('BUYER_OPENAI_MODEL','gpt-6.1-terra')
    captured={}
    class Responses:
        async def create(self,**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text=json.dumps({
                'selected_seller':'oliva','chosen_dish_names':['Wild Mushroom Tagliatelle','Margherita Pizza'],
                'estimated_total_usd':51,'reason_zh':'蘑菇意面和披萨符合偏好','comparison_zh':'两家都可选',
                'uncertainties':[],'would_book':False},ensure_ascii=False),
                usage=SimpleNamespace(input_tokens=180,output_tokens=90,total_tokens=270))
    class FakeAsyncOpenAI:
        def __init__(self,**kwargs):self.responses=Responses()
    monkeypatch.setattr(sys.modules['openai'],'AsyncOpenAI',FakeAsyncOpenAI,raising=False)
    result=call('POST','/competition/run',json={
        'preference':'两人喜欢蘑菇，想吃意大利面和披萨','budget_usd':75,'party_size':2,
        'oliva_interface':'website','verde_interface':'js', 'buyer_mode':'llm'})
    assert result.status_code==200,result.text
    d=result.json()
    assert d['buyer_mode']=='llm_evidence_reader'
    assert d['decision']['selected_seller']=='oliva'
    assert d['pricing_check']['sum_usd']==51
    assert d['usage']['buyer']['total_tokens']==270
    assert 'Casa Oliva' in captured['input'] and 'Casa Verde' in captured['input']
    assert 'menu_01' in captured['input'] or 'Burrata' in captured['input']


def test_llm_seller_responses_tool_calling_with_fake_sdk(monkeypatch):
    import sys
    from types import SimpleNamespace
    monkeypatch.setenv('OPENAI_API_KEY','TEST_ONLY_NEVER_A_REAL_CREDENTIAL')
    monkeypatch.setenv('OPENAI_MODEL','gpt-6.1-terra')
    calls=[]
    class Responses:
        def create(self,**kwargs):
            calls.append(kwargs)
            if len(calls)==1:
                return SimpleNamespace(output=[SimpleNamespace(type='function_call',name='get_menu',arguments='{}',call_id='call_1')],
                    output_text='',usage=SimpleNamespace(input_tokens=100,output_tokens=12,total_tokens=112))
            return SimpleNamespace(output=[],output_text='本店提供松露蘑菇宽面 USD 32。',
                usage=SimpleNamespace(input_tokens=95,output_tokens=25,total_tokens=120))
    class FakeOpenAI:
        def __init__(self,**kwargs):self.responses=Responses()
    monkeypatch.setattr(sys.modules['openai'],'OpenAI',FakeOpenAI,raising=False)
    result=call('POST','/competition/agent/verde',json={'mode':'llm','message':'你们有什么蘑菇意面，多少钱？'})
    assert result.status_code==200,result.text
    d=result.json()
    assert d['merchant_id']=='casa-verde-hk-demo'
    assert d['tool_trace'][0]['tool']=='get_menu'
    assert d['usage']['total_tokens']==232
    assert 'Casa Verde' in calls[0]['instructions']
    assert len(calls)==2
