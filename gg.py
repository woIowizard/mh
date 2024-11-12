import json,sys,cloudscraper
requests = cloudscraper.create_scraper()

def usage():print('usage: %s cookie [integer]\n'%(sys.argv[0].split('\\')[-1])); quit()

try: 
    assert len(sys.argv) in [2,3]
    n = int(sys.argv[2]) if len(sys.argv) == 3 else 0
    assert n >= 0
except: usage()

cache = {
    'cookie-name':'cookie-val'
}

cookies = {'HG_TOKEN':cache[sys.argv[1]] if sys.argv[1] in cache else sys.argv[1]}
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}
try: 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    hash = j['user']['unique_hash']
except: print('invalid cookie'); quit()
    
crafts = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='crafting_item' and 'quantity' in l.keys()}
current_location = j['user']['environment_type']

def craft(d,qty=1):
    d = {'parts[%s]'%k:d[k] for k in d}
    d['craftQty'],d['uh'] = qty,hash
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',d,cookies=cookies,headers=post_headers)

def buy(item,quantity): requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':hash,'type':item,'quantity':quantity,'buy':1},headers=post_headers,cookies=cookies)
def travel(dest): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':hash,'destination':dest},headers=post_headers,cookies=cookies)

cf = crafts['cavern_fungus_crafting_item'] if 'cavern_fungus_crafting_item' in crafts else 0
ns = crafts['cave_nightshade_crafting_item'] if 'cave_nightshade_crafting_item' in crafts else 0
ls = crafts['living_shard_crafting_item'] if 'living_shard_crafting_item' in crafts else 0
cw = crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0
si = crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0
n = min(cf//3,ns) if not n else min(cf//3,ns,n)

print('[INVENTORY CHECK] CF: %s, NS: %s, shard: %s, curds: %s, salt: %s'%(cf,ns,ls,cw,si))
if not n: print('[INVENTORY CHECK] lacking ingredients. quitting!'); quit()

if ls < n*3 or cw < n*30 or si < n*6:
    if current_location != 'fungal_cavern': travel('fungal_cavern')
    if ls < n*3: buy('living_shard_crafting_item',n*3-ls); print('[BUYING] bought %s living shards'%(n*3-ls))
    if cw < n*30: buy('curds_and_whey_craft_item',n*30-cw); print('[BUYING] bought %s curds'%(n*30-cw))
    if si < n*6: buy('ionized_salt_craft_item',n*6-si); print('[BUYING] bought %s salt'%(n*6-si))    
    if current_location != 'fungal_cavern': travel(current_location)

craft({'cavern_fungus_crafting_item':3,'cave_nightshade_crafting_item':1,'living_shard_crafting_item':3,'curds_and_whey_craft_item':30,'ionized_salt_craft_item':6},n)
print('[EXECUTION] crafted %s GG'%(n*3))
print('done!')
