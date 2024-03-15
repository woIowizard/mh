import requests,json,sys

def usage():print('usage: %s [cookie] [integer]\n'%(sys.argv[0].split('\\')[-1])); quit()

try: 
    n = int(sys.argv[2])
    assert n > 0 and len(sys.argv) == 3
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
baits = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='bait' and 'quantity' in l.keys()}

def craft(d,qty=1):
    d = {'parts[%s]'%k:d[k] for k in d}
    d['craftQty'],d['uh'] = qty,hash
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',d,cookies=cookies,headers=post_headers)
def travel(dest): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':hash,'destination':dest},headers=post_headers,cookies=cookies)

sb = baits['super_brie_cheese'] if 'super_brie_cheese' in baits else 0
me = crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts else 0
ea = crafts['essence_a_crafting_item'] if 'essence_a_crafting_item' in crafts else 0
rc = crafts['rift_cheese_curd_crafting_item'] if 'rift_cheese_curd_crafting_item' in crafts else 0
print('[INVENTORY CHECK] SB: %s, ME: %s, rift curd: %s, a essence: %s'%(sb,me,rc,ea))

if sb + me < n or ea < n:
    if sb + me < n: print('[INVENTORY CHECK] lacking %s SB'%(n-me-sb))
    if ea < n: print('[INVENTORY CHECK] lacking %s a essence'%(n-ea))
    print('[INVENTORY CHECK] quitting!')
    quit()

if me < n:
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'uh':hash,'item_type':'super_brie_cheese','item_qty':n-me},headers=post_headers,cookies=cookies)
    print('[EXECUTION] hammered %s SB'%(n-me))
    
if rc < n:
    if current_location != 'rift_gnawnia': travel('rift_gnawnia')
    requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':hash,'type':'rift_cheese_curd_crafting_item','quantity':n-rc,'buy':1},headers=post_headers,cookies=cookies)
    if current_location != 'rift_gnawnia': travel(current_location)
    print('[EXECUTION] bought %s rift curds'%(n-rc))
    
craft({'rift_cheese_curd_crafting_item':1,'magic_essence_craft_item':1,'essence_a_crafting_item':1},n)
print('[EXECUTION] crafted %s MSC'%n)
print('done!')
    