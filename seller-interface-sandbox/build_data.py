"""One-off extraction of the canonical V0 merchant facts from the HTML baseline."""
from bs4 import BeautifulSoup
from pathlib import Path
import json, re

SOURCE = Path(__file__).resolve().parent / 'website-v0/index.html'
OUT = Path(__file__).resolve().parent / 'data/merchant.json'
soup = BeautifulSoup(SOURCE.read_text(encoding='utf8'), 'html.parser')
menus=[]
for index, tag in enumerate(soup.select('.menu-card'), 1):
    title=tag.select_one('h3').get_text(' ',strip=True)
    price_str=tag.select_one('.dish-bottom span').get_text(' ',strip=True)
    menus.append({
        'id':f'menu_{index:02}',
        'name':title,
        'description':tag.select_one('p').get_text(' ',strip=True),
        'category':tag.select_one('.dish-tag').get_text(' ',strip=True).split(' · ')[0].title(),
        'price':int(re.sub('[^0-9]','',price_str)),
        'dietary_note':tag.select_one('.dish-bottom span:last-child').get_text(' ',strip=True)
    })
slots=[]
for tag in soup.select('#availability-table tbody tr'):
    cap=int(tag['data-capacity'])
    slots.append({'date':tag['data-date'],'time':tag['data-time'],'seating':tag['data-seat'].lower(),'max_party_size':cap,'status':'available' if cap else 'fully_booked'})
obj={
    'schema_version':'0.1',
    'data_version':'casa-oliva-v0-2026-11-17',
    'merchant_id':'casa-oliva-hk-demo',
    'demo_only':True,
    'name':'Casa Oliva',
    'tagline':'Italian Kitchen & Gathering Place',
    'description':'A fictional Italian restaurant used in the Seller-side Interface Sandbox. Simple ingredients, honest cooking; a warm place to gather.',
    'cuisine':'Italian',
    'address':{'english':'2/F, 18 Olive Lane, Central, Hong Kong','chinese':'香港中環橄欖里18號2樓','fictional':True,'country':'Hong Kong'},
    'phone':'+852 6849 1948',
    'phone_is_user_supplied_demo':True,
    'timezone':'Asia/Hong_Kong',
    'currency':'USD',
    'average_price_per_person':65,
    'price_note':'Demo menu in USD; menu prices exclude tax and gratuity.',
    'opening_hours':{'monday':'17:00-22:00','tuesday':'17:00-22:00','wednesday':'17:00-22:00','thursday':'17:00-22:00','friday':'17:00-23:00','saturday':'17:00-23:00','sunday':'17:00-21:00'},
    'amenities':{'indoor_seating':True,'outdoor_seating':True,'vegetarian_options':True},
    'reservation_policy':{'demo_only':True,'party_size_min':2,'party_size_max':6,'cancel_at_least_hours_before':2,'real_booking_supported':False,'payments_supported':False},
    'menu':menus,
    'availability':slots,
    'data_freshness':'static_fixed_demo_snapshot',
    'notes':['The address is fictional.','This is not a real restaurant reservation system.','The listed phone is user-supplied demo contact data.','The sample availability covers Dec 4–6, 2026 only.']
}
OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('wrote',OUT,len(menus),len(slots))
