"""FastAPI service for the API and Seller Agent comparison groups."""
from typing import Optional, Literal
import httpx
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field
from .store import public_profile, menu_items, available_slots, merchant_data
from .agent import mock_reply, llm_reply
from .buyer import run_buyer

app=FastAPI(title='Casa Oliva Seller-side Interface Sandbox', version='0.1.0',
            description='Simulation only. No bookings, inventory updates, or payments.')

@app.get('/demo',response_class=HTMLResponse)
def demo():
    return (Path(__file__).with_name('demo.html')).read_text(encoding='utf8')

@app.get('/health')
def health():
    d=merchant_data()
    return {'status':'ok','demo_only':True,'data_version':d['data_version']}

@app.get('/api/restaurant')
def restaurant():
    return public_profile()

@app.get('/api/menu')
def menu(vegetarian:Optional[bool]=None,max_price:Optional[float]=Query(default=None,ge=0)):
    return menu_items(vegetarian=vegetarian,max_price=max_price)

@app.get('/api/availability')
def availability(date:Optional[str]=Query(default=None,pattern=r'^\d{4}-\d{2}-\d{2}$'),
                 party_size:int=Query(default=4,ge=2,le=6),
                 seating:Optional[Literal['indoor','outdoor','all']]=None,
                 time:Optional[str]=Query(default=None,pattern=r'^([01]\d|2[0-3]):[0-5]\d$')):
    try:
        return available_slots(date=date,party_size=party_size,seating=seating,time=time)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

class ChatMessage(BaseModel):
    role:Literal['user','assistant']
    content:str=Field(min_length=1,max_length=4000)

class AgentRequest(BaseModel):
    message:str=Field(min_length=1,max_length=4000)
    mode:Literal['mock','llm']='mock'
    history:list[ChatMessage]=Field(default_factory=list,max_length=8)

@app.post('/agent/message')
def agent(req:AgentRequest):
    if req.mode=='mock':
        return mock_reply(req.message)
    try:
        return llm_reply(req.message,[m.model_dump() for m in req.history])
    except RuntimeError as exc:
        raise HTTPException(status_code=503,detail=str(exc))


PROJECT_ROOT=Path(__file__).resolve().parent.parent

@app.get('/seller/website', response_class=HTMLResponse)
def seller_website():
    return (PROJECT_ROOT/'website-v0'/'index.html').read_text(encoding='utf8')

@app.get('/seller/js-file/merchant.js', response_class=PlainTextResponse)
def seller_js_file():
    return (PROJECT_ROOT/'js-file'/'merchant.js').read_text(encoding='utf8')

class BuyerRequest(BaseModel):
    task:str=Field(min_length=1,max_length=2000)
    interface:Literal['website','js','api','seller_agent']='website'
    buyer_mode:Literal['mock','llm']='mock'
    seller_mode:Literal['mock','llm']='mock'

@app.post('/buyer/run')
async def buyer(req:BuyerRequest):
    try:
        return await run_buyer(req.task,req.interface,req.buyer_mode,req.seller_mode)
    except RuntimeError as exc:
        raise HTTPException(status_code=503,detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502,detail=f'Seller interface request failed ({exc.response.status_code}). Check Seller Agent mode/API key.')
