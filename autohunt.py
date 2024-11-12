# login
username = ''
password = ''
cookie = ''

# params
interval = 15
randomness = 300
miss_chance = .15


########## CODE BEGINS HERE ##########
import time,random,datetime,json,re,argparse,subprocess,functools,base64,cloudscraper
max_fail,timeout = 3,30

requests = cloudscraper.create_scraper()
requests.get = functools.partial(requests.get,timeout=timeout)
requests.post = functools.partial(requests.post,timeout=timeout)

##### ARGUMENT HANDLING #####
defined_cycles = ['gnawnia','windmill','harbour','mountain','mousoleum','tree','furoma','burglar','digby','toxic','gauntlet','tribal','iceberg','zzt','city','train','fiery','fort','garden','grift','brift','frift','bwrift','vrift','fungal','queso','mp','bb','sos','halloween','lny','bday']

p = argparse.ArgumentParser()
p.add_argument('-i',help='horn interval in mins (default %s)'%interval)
p.add_argument('-m',help='miss probability (default %s)'%miss_chance)
p.add_argument('-r',help='randomness interval in seconds (default %s)'%randomness)
p.add_argument('-A',action='store_true',help='aggressive mode: interval=15 mins, miss_probability=0, randomness=1')
p.add_argument('-P',action='store_true',help='paranoid mode: interval=15 mins, miss_probability=0.2, randomness=1800')
p.add_argument('-w',help='min first wait time')
p.add_argument('-a',action='store_true',help='minimal mode')
p.add_argument('-ua',help='user agent string. preset options: firefox (default), chrome, edge, mac, iphone')
p.add_argument('-s',action='store_true',help='antibot silent mode')
p.add_argument('-b',action='store_true',help='antibot bypass mode')
p.add_argument('-o',help='antibot auto-solve')
p.add_argument('-C',help='follow preset cycle. \'list\' for options')
p.add_argument('-z',help='cycle parameters')
args = p.parse_args()

if args.C == 'list':
    print('='*140+'\n-C option\tDescription\t\t\tRequirements\t\t\t\t\t\t\t-z options\n'+'='*140)
    d = [('gnawnia','town of gnawnia quest','None','None'),
    ('windmill','windmill quest','access to windmill','None'),
    ('harbour','pirates quest','access to harbour','None'),
    ('mountain','mountain quest','access to mountain + charm conduit','None'),
    ('gauntlet','catch eclipse','access to gauntlet',[('s','use superbrie formula for potions')]),
    ('tree','catch fairy/cherry/hydra','access to great gnarled tree',[('f','aim for fairy'),('c','aim for cherry'),('h','aim for hydra')]),
    ('mousoleum','catch mousevina','access to laboratory + shadow trap','None'),
    ('digby','catch big bad burroughs','access to digby','None'),
    ('burglar','catch master burglar','access to bazaar','None'),
    ('toxic','pollutinum quest','access to toxic spill + hydro trap',[('r','refine when possible'),('c','collect when possible'),('integer','max crude pollutinum while collecting')]),
    ('furoma','furoma cycle','access to furoma + tactical trap',[('integer','number of onyx stone to keep')]),
    ('tribal','tribal isles quests','balack: access to balack\'s cove + forgotten trap',[('no opts','balack')]),
    ('','','dragon: access to dracano + draconic trap',[('d','dragon')]),
    ('','','horde: access to jungle + shadow trap',[('h','horde')]),
    ('','','chieftian: access to isles + physical/tactical/hydro traps',[('c','chieftians')]),
    ('','','',[('e','hammer dragon embers for fire salt')]),
    ('city','claw shot city quest','access to claw shot city + law trap','None'),
    ('train','train quest','ongoing train quest + law trap',[('s','smuggle items instead of submitting'),('f','don\'t spend fools gold')]),
    ('fort','trap setup for fort rox','access to fort rox + law/shadow/arcane traps',[('m','use moon cheese at night if available'),('t','use tower before dawn if hp is not max')]),
    ('fiery','desert warpath quest','access to fiery warpath',[('g','go for gargantua at streak 6+ (default 8+)'),('integer','streak at which to go for commander'),('c','don\'t craft mage and cavalry charms')]),
    ('garden','living garden quest','access to living garden + hydro/arcane/shadow traps',[('c','don\'t go beyond city'),('d','don\'t go beyond dunes')]),
    ('zzt','go through zzt','access to zzt + tactical trap',[('m','aim for mystic'),('t','aim for technic'),('d','aim for double king'),('c','aim for chess master'),('q','use checkmate cheese on queen'),('s','use superbrie formula for checkmate cheese')]),
    ('iceberg','go through iceberg','access to iceberg','None'),
    ('queso','queso canyon quests','access to queso canyon + law/shadow/arcane traps',[('b/m/e/h/f','set target to bland/mild/med/hot/flaming queso'),('k','keep target queso'),('q','use target queso at quarry'),('p','use target queso at plains'),('u','auto upgrade pump')]),
    ('fungal','fungal cavern quest','access to fungal cavern + hydro/forgotten traps',[('g','farm glowing gruyere'),('b','keep materials for crystal crucible')]),
    ('mp','moussu picchu','access to moussu picchu + shadow/arcane/draconic traps',[('w','aim for wind'),('r','aim for rain'),('d','aim for dragons'),('s','use SB formula for dragonvine'),('g','use GG when not aiming'),('f','use fbf for dragons when not max')]),
    ('bb','bountiful beanstalk quest','access to bountiful beanstalk + physical trap',[('r','r1r instead of farming'),('g','don\'t plant vine'),('l','prioritise farming lavish')]),
    ('sos','school of sorcery','access to school of sorcery',[('c','always use cc'),('a/s','choose arcane/shadow course'),('m/b','use MM/AA cheese'),('f','sustainable farming')]),
    ('grift','gnawnia rift quest','access to gnawnia rift',[('b','keep 10 seed, grass, and dust'),('r','don\'t use resonator')]),
    ('brift','burroughs rift quest','access to burroughs rift + rift trap',[('t','go for behemoth burroughs'),('b','go for monstrous abomination'),('g','stay in green zone')]),
    ('frift','furoma rift cycle','access to furoma rift + rift trap',[('integer','number of onyx stone to keep'),('c','use enerchi charm outside')]),
    ('bwrift','bristle woods rift quest','access to bw rift + rift trap',[('q','use QQ for some normal rooms')]),
    ('vrift','valour rift quest','access to vrift + rift trap',[('f','use champion\'s fire outside eclipse'),('s','estimate probability of crossing next eclipse'),('#','benchmark floor for simulations')]),
    ('lny','lunar new year','event','None'),
    ('bday','birthday','event',[('s','use speedy coggy colby'),('c','use factory repair charm'),('g','use gouda cheese'),('m/b/p/q','hunt at mixing/break/pump/qa room'),('h','use SB'),('t','autosolve event map')]),
    ('halloween','halloween','event',[('r','don\'t brew root'),('b','don\'t use bonefort')]),
    ]
    for c in d: print('{4}{0:<10}\t{1:<30}\t{2:<60}\t{3}'.format(c[0],c[1],c[2],'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t'.join('%s: %s'%(p[0],p[1]) for p in c[3]) if c[3] != 'None' else c[3],'\n' if c[0] else ''))
    print('')
    quit()

if args.A and args.P: print('Incompatible options. Choose at most one of -A -P'); quit()
if args.A: interval,miss_chance,randomness = 15,0,1
elif args.P: interval,miss_chance,randomness = 15,.2,1800
if args.a and args.C: print('Cycles cannot be used with minimal mode'); quit()

try:
    if args.i: interval = float(args.i)
    if args.m: miss_chance = float(args.m)
    if args.r: randomness = float(args.r)
except: print('imr parameters must be numeric'); quit()
cycle = args.C if args.C in defined_cycles else ''
args.z = args.z if args.z else ''
antibot_mode = 'silent' if args.s else 'bypass' if args.b or args.a else 'auto-solve' if args.o else 'standard'

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0' if args.ua == 'firefox' or not args.ua else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.3' if args.ua == 'chrome' else 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15' if args.ua == 'mac' else 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1' if args.ua == 'iphone' else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edge/100.0.1185.39' if args.ua == 'edge' else args.ua

print('[%s] starting autohunt. %sinterval: %s, miss_prob: %s, randomness: %s, antibot: %s'%(datetime.datetime.now().replace(microsecond=0),'minimal mode. ' if args.a else 'cycle: %s, '%(cycle if cycle else 'none'),interval,miss_chance,randomness,antibot_mode))

##### AUTHENTICATION #####
def login():
    global cookie,hash,cookies
    if not username or not password: print('[%s] credentials not provided. aborting'%(datetime.datetime.now().replace(microsecond=0))); quit()
    r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',{'action':'loginHitGrab','username':username,'password':password},headers=post_headers)
    try: 
        cookie,hash = r.cookies['HG_TOKEN'], json.loads(r.text)['user']['unique_hash']
        cookies = {'HG_TOKEN':cookie}
        print('[%s] authentication successful. session cookie: %s'%(datetime.datetime.now().replace(microsecond=0),cookie))
    except: print('[%s] login failed. aborting'%(datetime.datetime.now().replace(microsecond=0))); quit()

try: cookie = cookie
except: cookie = ''
try: username,password = username,password
except: username,password = '',''
hash,horns,antibot_triggered,allowed_regions,lpt,user_id,lrje = '',0,0,[],0,'',0
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent':useragent}
get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-GB,en;q=0.5', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '1', 'TE': 'trailers', 'Upgrade-Insecure-Requests': '1', 'User-Agent':useragent}
api_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'file://', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
cookies = {'HG_TOKEN':cookie}

if cookie: print('[%s] logging in with cookie: %s'%(datetime.datetime.now().replace(microsecond=0),cookie))
else: login()

##### CYCLE HELPERS #####
def choose_cycle():
    if cycle == 'gnawnia': gnawnia()
    elif cycle == 'windmill': windmill()
    elif cycle == 'harbour': harbour()
    elif cycle == 'mountain': mountain()
    elif cycle == 'mousoleum': mousoleum()
    elif cycle == 'tree': tree()
    elif cycle == 'burglar': burglar()
    elif cycle == 'furoma': furoma()
    elif cycle == 'gauntlet': gauntlet()
    elif cycle == 'tribal': tribal()
    elif cycle == 'digby': digby()
    elif cycle == 'toxic': toxic()
    elif cycle == 'iceberg': iceberg()
    elif cycle == 'zzt': zzt()
    elif cycle == 'city': city()
    elif cycle == 'train': train()
    elif cycle == 'fiery': fiery()
    elif cycle == 'garden': garden()
    elif cycle == 'fort': fort()
    elif cycle == 'grift': grift()
    elif cycle == 'brift': brift()
    elif cycle == 'frift': frift()
    elif cycle == 'fungal': fungal()
    elif cycle == 'queso': queso()
    elif cycle == 'mp': mp()
    elif cycle == 'bb': bb()
    elif cycle == 'sos': sos()
    elif cycle == 'bwrift': bwrift()
    elif cycle == 'vrift': vrift()
    elif cycle == 'halloween': halloween()
    elif cycle == 'xmas': xmas()
    elif cycle == 'lny': lny()
    elif cycle == 'bday': bday()
    
def travel(dest): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':hash,'destination':dest},headers=post_headers,cookies=cookies)
def arm_bait(bait): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'bait':bait},headers=post_headers,cookies=cookies)
def arm_weapon(weapon): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'weapon':weapon},headers=post_headers,cookies=cookies)
def arm_base(base): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'base':base},headers=post_headers,cookies=cookies)
def arm_charm(charm): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'trinket':charm},headers=post_headers,cookies=cookies)
def hammer(item,quantity): requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'uh':hash,'item_type':item,'item_qty':quantity},headers=post_headers,cookies=cookies)
def buy(item,quantity): requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':hash,'type':item,'quantity':quantity,'buy':1},headers=post_headers,cookies=cookies)
def potion(p,i,qty=1): requests.post('https://www.mousehuntgame.com/managers/ajax/users/usepotion.php',{'potion':p,'num_potions':qty,'recipe_index':i,'uh':hash},cookies=cookies,headers=post_headers)
def get_recipes(j,p):
    r = [l for l in j['components'] if l['classification']=='potion' if l['type']==p and l['quantity']]
    if not r: return []
    s = max(r[0]['recipe_list'],key=lambda x:x['produced_item_yield'])['recipe_index']
    m = max([l for l in r[0]['recipe_list'] if l['consumed_item_name'] != 'SUPER|brie+'],key=lambda x:x['produced_item_yield'])['recipe_index']
    return s,m

def craft(d,qty=1):
    d = {'parts[%s]'%k:d[k] for k in d}
    d['craftQty'],d['uh'] = qty,hash
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',d,cookies=cookies,headers=post_headers).text

def prologue(): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    
    current_location = j['user']['environment_type']
    current_base = j['user']['base_name'].lower().replace(' ','_').replace('\'','')
    cache = {'attuned_enerchi_induction_base':'furoma_rift_energy_upgraded_base','bamboozler_base':'bamboo_base','enerchi_induction_base':'furoma_rift_energy_base','overgrown_ember_stone_base':'queso_canyon_base'}
    if current_base in cache: current_base = cache[current_base]
    
    cache = {'timesplit_dissonance_trap_weapon':'temporal_dissonance_weapon'}
    current_weapon = j['user']['weapon_name'].lower().replace(' ','_').replace('\'','') + '_weapon'
    if current_weapon in cache: current_weapon = cache[current_weapon]
    current_bait = j['user']['bait_name'].lower().replace(' ','_').replace('\'','') if j['user']['bait_name'] else 0
    current_trinket = j['user']['trinket_name'].lower().replace('charm','trinket').replace(' ','_').replace('\'','') if 'trinket_name' in j['user'] and j['user']['trinket_name'] else None
        
    baits = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='bait' and 'quantity' in l.keys()}
    crafts = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='crafting_item' and 'quantity' in l.keys()}
    stats = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='stat' and 'quantity' in l.keys()}
    trinkets = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='trinket' and 'quantity' in l.keys()}
    potions = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='potion' and 'quantity' in l.keys()}
    bases = [c['type'] for c in j['components'] if c['classification']=='base']
    weapons = [c['type'] for c in j['components'] if c['classification']=='weapon']
    chests = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='convertible' and 'quantity' in l.keys()}
    
    best_weapons = {}
    for k in set([c['power_type_name'] for c in j['components'] if c['classification']=='weapon']): best_weapons[k] = max([c for c in j['components'] if c['classification']=='weapon' and c['power_type_name']==k],key=lambda x:x['power'])['type']
    best_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['power'] if 'power' in x else 0)['type']
    best_weapon = max([c for c in j['components'] if c['classification']=='weapon'],key=lambda x:x['power'] if 'power' in x else 0)['type']

    return current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j
        
##### CYCLES #####
def gnawnia(loop_counter=0): 
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_location != 'town_of_gnawnia':
        travel('town_of_gnawnia')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    if j['user']['quests']['QuestTownOfGnawnia']['state'] == 'allBountiesComplete': return print('[%s] [%s] all bounties complete'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    elif j['user']['quests']['QuestTownOfGnawnia']['can_accept'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/town_of_gnawnia.php',{'uh':hash,'action':'accept_bounty'},headers=post_headers,cookies=cookies)
    elif j['user']['quests']['QuestTownOfGnawnia']['can_claim'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/town_of_gnawnia.php',{'uh':hash,'action':'claim_reward'},headers=post_headers,cookies=cookies)
    elif 'bait_like_type' in j['user']['quests']['QuestTownOfGnawnia']: target_bait = j['user']['quests']['QuestTownOfGnawnia']['bait_like_type']
    if target_bait:
        if target_bait not in baits or baits[target_bait] < 2: buy(target_bait,2)
        if current_bait != target_bait: arm_bait(target_bait)
        print('[%s] [%s] hunting %s with %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestTownOfGnawnia']['mouse_name'].lower(),target_bait.replace('_',' ')))
    elif loop_counter > 5: print('looped too many times. quitting!'); quit()
    else: gnawnia(loop_counter+1)    

def windmill():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()    
    if 'windmill' not in allowed_regions: return print('[%s] [%s] no access to windmill. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'windmill':
        travel('windmill')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    num_cheese = int(j['user']['quests']['QuestWindmill']['items']['grilled_cheese']['quantity'])
    num_flour = int(j['user']['quests']['QuestWindmill']['items']['flour_stat_item']['quantity'])
    if num_cheese: 
        if current_bait != 'grilled_cheese': arm_bait('grilled_cheese')
        print('[%s] [%s] using grilled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),num_cheese))
    elif num_flour >= 60: 
        buy('grilled_cheese_pack_convertible',1)
        windmill()
    else: 
        print('[%s] [%s] getting flour: have %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),num_flour))
        if 'swiss_cheese' not in baits: buy('swiss_cheese',5)
        if current_bait != 'swiss_cheese': arm_bait('swiss_cheese')

def harbour():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'harbour' not in allowed_regions: return print('[%s] [%s] no access to harbour. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'harbour':
        travel('harbour')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_weapon != best_weapon: arm_weapon(best_weapon)
    if current_bait != 'brie_cheese':
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 5: buy('brie_cheese',10)
        arm_bait('brie_cheese')
    if j['user']['quests']['QuestHarbour']['status'] == 'searchStarted' and j['user']['quests']['QuestHarbour']['can_claim_status'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/harbour.php',{'action':'claimBooty','uh':hash},headers=post_headers,cookies=cookies)
    elif j['user']['quests']['QuestHarbour']['status'] == 'canBeginSearch': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/harbour.php',{'action':'beginSearch','uh':hash},headers=post_headers,cookies=cookies)
        
def mountain(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()  
    if 'mountain' not in allowed_regions: return print('[%s] [%s] no access to mountain. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'mountain':
        travel('mountain')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    if 'power_trinket' not in trinkets or trinkets['power_trinket'] <= 5: buy('power_trinket',5)
    if current_trinket != 'power_trinket': arm_charm('power_trinket')
    if 'abominable_asiago_cheese' in baits: 
        target_bait = 'abominable_asiago_cheese'
        print('[%s] [%s] using abominable asiago'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    elif 'faceted_sugar_crafting_item' in crafts and crafts['faceted_sugar_crafting_item'] >= 3 and 'ice_curd_crafting_item' in crafts and crafts['ice_curd_crafting_item'] >= 3: craft({'faceted_sugar_crafting_item':3,'ice_curd_crafting_item':3},qty=min(crafts['faceted_sugar_crafting_item']//3,crafts['ice_curd_crafting_item']//3))
    elif 'cheddore_cheese' in baits: 
        target_bait = 'cheddore_cheese'
        print('[%s] [%s] using cheddore. faceted sugar: %s, ice curd: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['faceted_sugar_crafting_item'] if 'faceted_sugar_crafting_item' in crafts else 0,crafts['ice_curd_crafting_item'] if 'ice_curd_crafting_item' in crafts else 0))
    elif j['user']['quests']['QuestMountain']['boulder_status'] == 'can_claim': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mountain.php',{'action':'claim_reward','uh':hash},cookies=cookies,headers=post_headers)
    else:
        target_bait = 'brie_cheese'
        if target_bait not in baits or baits[target_bait] <= 10: buy(target_bait,100)
        print('[%s] [%s] hitting boulder. boulder hp: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestMountain']['boulder_hp']))
        
    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
    elif loop_counter > 5: print('looped too many times. quitting!'); quit()
    else: mountain(loop_counter+1)

def mousoleum(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait,target_location,target_weapon = '','',''
    
    if 'laboratory' not in allowed_regions: return print('[%s] [%s] no access to laboratory. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Shadow' not in best_weapons: return print('[%s] [%s] no shadow weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 70: buy('brie_cheese',66)
    
    if 'radioactive_blue_cheese' not in baits or 'mousoleum' not in allowed_regions: 
        if 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
        elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
        else: 
            target_bait,target_location,target_weapon = 'brie_cheese','laboratory',best_weapons['Shadow']
            print('[%s] [%s] using %s at %s: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),target_location.replace('_',' '),baits[target_bait]))
    else:         
        if current_location != 'mousoleum':
            travel('mousoleum')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        if j['user']['quests']['QuestMousoleum']['has_wall']:
            if j['user']['quests']['QuestMousoleum']['wall_health'] <= 20 and int(j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity']): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mousoleum.php',{'action':'repair_wall','uh':hash},cookies=cookies,headers=post_headers)
            elif 'crimson_cheese' in baits: 
                target_bait,target_location,target_weapon = 'crimson_cheese','mousoleum',best_weapons['Shadow']
                print('[%s] [%s] using %s at %s. wall health: %s, slats obtained: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),target_location.replace('_',' '),j['user']['quests']['QuestMousoleum']['wall_health'],j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))
            elif 'crimson_curd_crafting_item' in crafts and crafts['crimson_curd_crafting_item'] >= 6: craft({'crimson_curd_crafting_item':6},qty=crafts['crimson_curd_crafting_item']//6)
            else: 
                target_bait,target_weapon,target_location = 'radioactive_blue_cheese',best_weapons['Shadow'],'mousoleum'
                print('[%s] [%s] wall up, collecting crimson curds. curds: %s, wall health: %s, slats on hand: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['crimson_curd_crafting_item'] if 'crimson_curd_crafting_item' in crafts else 0,j['user']['quests']['QuestMousoleum']['wall_health'],j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))
        elif int(j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity']) >= 30: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mousoleum.php',{'action':'build_wall','uh':hash},cookies=cookies,headers=post_headers)
        else:
            target_bait,target_weapon,target_location = 'radioactive_blue_cheese',best_weapons['Shadow'],'mousoleum'
            print('[%s] [%s] collecting slats for wall. slats obtained: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))

    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
        if current_location != target_location: travel(target_location)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
    elif loop_counter > 5: print('looped too many times. quitting!'); quit()
    else: mousoleum(loop_counter+1)       

def tree(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location,target_weapon,target_bait = '',best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon  ,''
    
    if 'great_gnarled_tree' not in allowed_regions: return print('[%s] [%s] no access to tree. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] <= 15: buy('brie_cheese',10)
    
    if 'gnarled_cheese' in baits and ('f' in args.z or ('h' in args.z and 'lagoon' not in allowed_regions)):
        target_location, target_bait = 'great_gnarled_tree','gnarled_cheese'
        print('[%s] [%s] using gnarled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['gnarled_cheese']))
    elif 'cherry_cheese' in baits and 'c' in args.z: 
        target_location,target_bait = 'great_gnarled_tree','cherry_cheese'
        print('[%s] [%s] using cherry cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['cherry_cheese']))
    elif 'wicked_gnarly_cheese' in baits and 'h' in args.z and 'lagoon' in allowed_regions:
        target_location,target_bait = 'lagoon','wicked_gnarly_cheese'
        print('[%s] [%s] hunting for hydra with wicked gnarly cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['wicked_gnarly_cheese']))
    elif 'gnarled_cheese' in baits and 'h' in args.z: 
        target_location,target_bait = 'lagoon','gnarled_cheese'
        print('[%s] [%s] hunting for hydra with gnarled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['gnarled_cheese']))
    elif 'gnarled_cheese_potion' in potions and ('f' in args.z or 'h' in args.z): potion('gnarled_cheese_potion',get_recipes(j,'gnarled_cheese_potion')[1])
    elif 'wicked_gnarly_potion' in potions and 'h' in args.z: potion('wicked_gnarly_potion',get_recipes(j,'wicked_gnarly_potion')[1])
    elif 'cherry_potion' in potions and 'c' in args.z: potion('cherry_potion',get_recipes(j,'cherry_potion')[1])
    else: 
        target_location,target_bait = 'great_gnarled_tree','brie_cheese'
        print('[%s] [%s] hunting for potions'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
        
    if target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_location != target_location and target_location in allowed_regions: travel(target_location)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: tree(loop_counter+1)

def furoma(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    
    if 'dojo' not in allowed_regions: return print('[%s] [%s] no access to furoma. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Tactical' not in best_weapons: return print('[%s] [%s] no tactical weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_weapon != best_weapons['Tactical']: arm_weapon(best_weapons['Tactical'])
    
    keep_onyx = int(''.join([c for c in '0'+args.z if c.isdigit()]))
    
    if 'onyx_gorgonzola_cheese' in baits: target_location, target_bait = 'pinnacle_chamber', 'onyx_gorgonzola_cheese'
    elif 'onyx_stone_craft_item' in crafts and crafts['onyx_stone_craft_item'] >= keep_onyx:
        num = crafts['onyx_stone_craft_item']-keep_onyx
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',60*num)
        buy('ionized_salt_craft_item',6*num)
        craft({'curds_and_whey_craft_item':60,'ionized_salt_craft_item':6,'onyx_stone_craft_item':1},num)
    elif 'rumble_cheese' in baits: target_location, target_bait = 'pinnacle_chamber', 'rumble_cheese'
    elif 'masters_seal_craft_item' in crafts:
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',20*crafts['masters_seal_craft_item'])
        buy('ionized_salt_craft_item',crafts['masters_seal_craft_item'])
        craft({'curds_and_whey_craft_item':20,'ionized_salt_craft_item':1,'masters_seal_craft_item':1},crafts['masters_seal_craft_item'])
    elif 'master_claw_shard_craft_item' not in crafts:
        if 'susheese_cheese' in baits: target_location, target_bait = 'meditation_room', 'susheese_cheese'
        elif 'token_of_the_cheese_claw_craft_item' in crafts and crafts['token_of_the_cheese_claw_craft_item'] >= 3:
            num = crafts['token_of_the_cheese_claw_craft_item']//3
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',num)
            buy('nori_craft_item',3*num)
            buy('burroughs_salmon_craft_item',num)
            craft({'token_of_the_cheese_claw_craft_item':3,'curds_and_whey_craft_item':3,'nori_craft_item':1,'burroughs_salmon_craft_item':1},num)
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [%s] hunting for claw token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['token_of_the_cheese_claw_craft_item'] if 'token_of_the_cheese_claw_craft_item' in crafts else 0))
    elif 'master_fang_shard_craft_item' not in crafts:
        if 'combat_cheese' in baits: target_location, target_bait = 'meditation_room', 'combat_cheese'
        elif 'token_of_the_cheese_fang_craft_item' in crafts and crafts['token_of_the_cheese_fang_craft_item'] >= 3:
            num = crafts['token_of_the_cheese_fang_craft_item']//3
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',5*num)
            buy('splintered_wood_craft_item',num)
            buy('paintbrand_paint_craft_item',num) 
            craft({'token_of_the_cheese_fang_craft_item':3,'curds_and_whey_craft_item':5,'splintered_wood_craft_item':1,'paintbrand_paint_craft_item':1},num)
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [%s] hunting for fang token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['token_of_the_cheese_fang_craft_item'] if 'token_of_the_cheese_fang_craft_item' in crafts else 0))
    elif 'master_belt_shard_craft_item' not in crafts:
        if 'glutter_cheese' in baits: target_location, target_bait = 'meditation_room', 'glutter_cheese'
        elif 'token_of_the_cheese_belt_craft_item' in crafts and crafts['token_of_the_cheese_belt_craft_item'] >= 3:
            if current_location != 'meditation_room': travel('meditation_room')
            num = crafts['token_of_the_cheese_belt_craft_item']//3
            buy('curds_and_whey_craft_item',7*num)
            buy('invisiglu_craft_item',num)
            buy('cheesy_fluffs_craft_item',num)
            craft({'token_of_the_cheese_belt_craft_item':3,'curds_and_whey_craft_item':7,'invisiglu_craft_item':1,'cheesy_fluffs_craft_item':1},num)
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [%s] hunting for belt token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['token_of_the_cheese_belt_craft_item'] if 'token_of_the_cheese_belt_craft_item' in crafts else 0))
    else:
        num = min(crafts['master_belt_shard_craft_item'],crafts['master_claw_shard_craft_item'],crafts['master_fang_shard_craft_item'])
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',20*num)
        buy('ionized_salt_craft_item',num)
        craft({'curds_and_whey_craft_item':20,'ionized_salt_craft_item':1,'master_claw_shard_craft_item':1,'master_belt_shard_craft_item':1,'master_fang_shard_craft_item':1},num)
                
    if target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_location and current_location != target_location: travel(target_location)
        if target_location != 'dojo': print('[%s] [%s] using %s at %s: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),target_location.replace('_',' '),baits[target_bait]))
    elif loop_counter > 5: print('looped too many times. quitting!'); quit()
    else: furoma(loop_counter+1)

def burglar(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()    
    if 'bazaar' not in allowed_regions: return print('[%s] [%s] no access to bazaar. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 10: buy('brie_cheese',10)
    target_bait = 'gilded_cheese' if 'gilded_cheese' in baits else 'brie_cheese'    
    if current_weapon != best_weapon: arm_weapon(best_weapon)
    if current_location != 'bazaar': travel(target_location)
    if current_bait != target_bait: arm_bait(target_bait)
    print('[%s] [%s] using %s: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),baits[target_bait]))

def gauntlet(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait,target_weapon = '',''
    
    if 'kings_gauntlet' not in allowed_regions: return print('[%s] [%s] no access to gauntlet. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'kings_gauntlet': travel('kings_gauntlet')
            
    if 'gauntlet_cheese_8' in baits: target_bait, target_weapon = 'gauntlet_cheese_8', best_weapons['Forgotten'] if 'Forgotten' in best_weapons else best_weapon
    elif 'gauntlet_potion_8' in potions: 
        s,m = get_recipes(j,'gauntlet_potion_8')
        potion('gauntlet_potion_8',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_7' in baits: target_bait, target_weapon = 'gauntlet_cheese_7', best_weapons['Hydro'] if 'Hydro' in best_weapons else best_weapon
    elif 'gauntlet_potion_7' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 2: buy('brie_cheese',2)
        s,m = get_recipes(j,'gauntlet_potion_7')
        potion('gauntlet_potion_7',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_6' in baits: target_bait, target_weapon = 'gauntlet_cheese_6', best_weapons['Arcane'] if 'Arcane' in best_weapons else best_weapon
    elif 'gauntlet_potion_6' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 3: buy('brie_cheese',3)
        s,m = get_recipes(j,'gauntlet_potion_6')
        potion('gauntlet_potion_6',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_5' in baits: target_bait, target_weapon = 'gauntlet_cheese_5', best_weapons['Shadow'] if 'Shadow' in best_weapons else best_weapon
    elif 'gauntlet_potion_5' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 4: buy('brie_cheese',4)
        s,m = get_recipes(j,'gauntlet_potion_5')
        potion('gauntlet_potion_5',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_4' in baits: target_bait, target_weapon = 'gauntlet_cheese_4', best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon
    elif 'gauntlet_potion_4' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 4: buy('brie_cheese',4)
        s,m = get_recipes(j,'gauntlet_potion_4')
        potion('gauntlet_potion_4',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_3' in baits: target_bait, target_weapon = 'gauntlet_cheese_3', best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon
    elif 'gauntlet_potion_3' in potions: 
        if 'swiss_cheese' not in baits or baits['swiss_cheese'] < 5: buy('swiss_cheese',5)
        s,m = get_recipes(j,'gauntlet_potion_3')
        potion('gauntlet_potion_3',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_2' in baits: target_bait, target_weapon = 'gauntlet_cheese_2', best_weapons['Physical']
    elif 'gauntlet_potion_2' in potions: 
        if 'swiss_cheese' not in baits or baits['swiss_cheese'] < 4: buy('swiss',4)
        s,m = get_recipes(j,'gauntlet_potion_2')
        potion('gauntlet_potion_2',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    else:
        target_bait, target_weapon = 'brie_cheese', best_weapons['Physical']
        if 'brie_cheese' not in baits: buy('brie_cheese',10)
    if target_bait:
        if target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_bait != current_bait: arm_bait(target_bait)
        print('[%s] [%s] hunting at tier %s with %s. %s bait left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait[-1] if target_bait[-1] in '8765432' else '1',target_weapon.replace('_weapon','').replace('_',' '),baits[target_bait]))
    elif loop_counter > 5: print('looped too many times. quitting!'); quit()
    else: gauntlet(loop_counter+1)

def tribal(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_bait, target_location, target_item = '','','',''
    
    if 'nerg_plains' not in allowed_regions: return print('[%s] [%s] no access to tribal isles. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Hydro','Physical','Tactical']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
        
    if 'dragons_chest_convertible' in chests: requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'dragons_chest_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    done,seeds_num = 0,0
    
    if ('c' not in args.z and 'h' not in args.z and 'd' not in args.z and 'balacks_cove' in allowed_regions and 'Forgotten' in best_weapons) and ('vengeful_vanilla_stilton_cheese' in baits or ('raisins_of_wrath' in crafts and 'pinch_of_annoyance_crafting_item' in crafts and 'bottled_up_rage_crafting_item' in crafts and 'vanilla_bean_crafting_item' in crafts) or 'vanilla_stilton_cheese' in baits or ('vanilla_bean_crafting_item' in crafts and crafts['vanilla_bean_crafting_item'] >= 15)):
        if current_location != 'balacks_cove': travel('balacks_cove')
        if json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies).text)['user']['quests']['QuestBalacksCove']['tide']['level'] == 'low': 
            done = 1
            if 'vengeful_vanilla_stilton_cheese' in baits: target_location, target_bait, target_weapon = 'balacks_cove','vengeful_vanilla_stilton_cheese',best_weapons['Forgotten']
            elif 'raisins_of_wrath' in crafts and 'pinch_of_annoyance_crafting_item' in crafts and 'bottled_up_rage_crafting_item' in crafts and 'vanilla_bean_crafting_item' in crafts:
                num = min(crafts['raisins_of_wrath'],crafts['pinch_of_annoyance_crafting_item'],crafts['bottled_up_rage_crafting_item'],crafts['vanilla_bean_crafting_item'])
                buy('curds_and_whey_craft_item',num)
                buy('coconut_milk_craft_item',num)
                buy('ionized_salt_craft_item',num)
                craft({'curds_and_whey_craft_item':1,'coconut_milk_craft_item':1,'ionized_salt_craft_item':1,'vanilla_bean_crafting_item':1,'raisins_of_wrath':1,'pinch_of_annoyance_crafting_item':1,'bottled_up_rage_crafting_item':1},num)
            elif 'vanilla_stilton_cheese' in baits: 
                target_bait, target_weapon, target_item = 'vanilla_stilton_cheese',best_weapons['Forgotten'],'pinch'
                print('[%s] [%s] using vanilla stilton. raisins of wrath: %s, pinch of annoyance: %s, bottled-up rage: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['raisins_of_wrath'] if 'raisins_of_wrath' in crafts else 0,crafts['pinch_of_annoyance_crafting_item'] if 'pinch_of_annoyance_crafting_item' in crafts else 0,crafts['bottled_up_rage_crafting_item'] if 'bottled_up_rage_crafting_item' in crafts else 0))
            else: 
                buy('curds_and_whey_craft_item',15*crafts['vanilla_bean_crafting_item']//15)
                buy('coconut_milk_craft_item',15*crafts['vanilla_bean_crafting_item']//15)
                buy('salt_craft_item',15*crafts['vanilla_bean_crafting_item']//15)
                craft({'curds_and_whey_craft_item':15,'coconut_milk_craft_item':15,'salt_craft_item':15,'vanilla_bean_crafting_item':15},crafts['vanilla_bean_crafting_item']//15)
    if done: done = 0
    elif 'c' not in args.z and 'h' not in args.z and 'dracano' in allowed_regions and 'Draconic' in best_weapons and 'inferno_havarti_cheese' in baits: target_location, target_bait, target_weapon, target_item = 'dracano','inferno_havarti_cheese',best_weapons['Draconic'],'vanilla_bean_crafting_item'
    elif 'c' not in args.z and 'h' not in args.z and 'inferno_pepper_craft_item' in crafts and crafts['inferno_pepper_craft_item'] >= 6 and 'fire_salt_craft_item' in crafts and crafts['fire_salt_craft_item'] >= 6:
        num = min(crafts['inferno_pepper_craft_item']//6,crafts['fire_salt_craft_item']//6)
        buy('curds_and_whey_craft_item',18*num)
        buy('coconut_milk_craft_item',16*num)
        craft({'curds_and_whey_craft_item':18,'coconut_milk_craft_item':16,'fire_salt_craft_item':6,'inferno_pepper_craft_item':6},num)
    elif 'c' not in args.z and 'h' not in args.z and ('inferno_pepper_craft_item' not in crafts or crafts['inferno_pepper_craft_item'] < 6):
        if 'blue_pepper_seed_craft_item' in crafts and 'red_pepper_seed_craft_item' in crafts and 'yellow_pepper_seed_craft_item' in crafts and 'c' not in args.z:
            num = min(crafts['blue_pepper_seed_craft_item'],crafts['red_pepper_seed_craft_item'],crafts['yellow_pepper_seed_craft_item'])
            if 'plant_pot_craft_item' not in crafts: 
                if current_location not in ['dracano','derr_dunes','elub_shore','nerg_plains']: travel('dracano')
                buy('plant_pot_craft_item',num)
            craft({'blue_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1,'yellow_pepper_seed_craft_item':1,'plant_pot_craft_item':1},num)
            time.sleep(1)
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'white_pepper_plant_convertible','uh':hash,'item_qty':num},cookies=cookies,headers=post_headers)
        else: done,seeds_num = 1,1
    elif ('fire_salt_craft_item' not in crafts or crafts['fire_salt_craft_item'] < 6 or 'h' in args.z) and 'c' not in args.z and 'Shadow' in best_weapons and 'jungle_of_dread' in allowed_regions:
        if 'e' in args.z and 'dragon_ember' in crafts and 'h' not in args.z: hammer('dragon_ember',crafts['dragon_ember'])
        for havarti in ['spicy_havarti_cheese','magical_havarti_cheese','sweet_havarti_cheese','crunchy_havarti_cheese','creamy_havarti_cheese','pungent_havarti_cheese']:
            if havarti in baits: 
                target_location, target_bait, target_weapon, target_item = 'jungle_of_dread',havarti,best_weapons['Shadow'],'fire_salt_craft_item'
                break
        else:
            for pepper in [('magical_blue_pepper_craft_item',2),('sweet_yellow_pepper_craft_item',6),('spicy_red_pepper_craft_item',12),('crunchy_green_pepper_craft_item',4),('pungent_purple_pepper_craft_item',8),('creamy_orange_pepper_craft_item',10)]:
                if pepper[0] in crafts and crafts[pepper[0]] >= 6:
                    if current_location != 'jungle_of_dread': travel('jungle_of_dread')
                    num = crafts[pepper[0]]//6
                    buy('curds_and_whey_craft_item',18*num)
                    buy('salt_craft_item',6*num)
                    buy('coconut_milk_craft_item',pepper[1]*num)
                    craft({'curds_and_whey_craft_item':18,'salt_craft_item':6,'coconut_milk_craft_item':pepper[1],pepper[0]:6},num)
                    done = 1
            if done: done = 0
            elif 'blue_pepper_seed_craft_item' in crafts and 'red_pepper_seed_craft_item' in crafts and 'yellow_pepper_seed_craft_item' in crafts and crafts['blue_pepper_seed_craft_item'] >= 4 and crafts['red_pepper_seed_craft_item'] >= 4 and crafts['yellow_pepper_seed_craft_item'] >= 4:
                print('[%s] [%s] crafting plants. wait about 15s...'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
                if current_location != 'jungle_of_dread': travel('jungle_of_dread')
                buy('plant_pot_craft_item',6)
                craft({'plant_pot_craft_item':1,'blue_pepper_seed_craft_item':2})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'red_pepper_seed_craft_item':2})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'yellow_pepper_seed_craft_item':2})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'blue_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'yellow_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'blue_pepper_seed_craft_item':1,'yellow_pepper_seed_craft_item':1})
                for colour in ['blue','red','yellow','green','purple','orange']:
                    time.sleep(1)
                    requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'%s_pepper_plant_convertible'%colour,'uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
            else: done,seeds_num = 1,4
    else: done = 1
    if not done: pass
    elif 'red_pepper_seed_craft_item' not in crafts or ('c' in args.z and 'yellow_pepper_seed_craft_item' in crafts and crafts['red_pepper_seed_craft_item'] < crafts['yellow_pepper_seed_craft_item'] and 'blue_pepper_seed_craft_item' in crafts and crafts['red_pepper_seed_craft_item'] < crafts['blue_pepper_seed_craft_item']) or crafts['red_pepper_seed_craft_item'] < seeds_num:
        if 'crunchy_cheese' in baits: target_location, target_bait, target_weapon = 'derr_dunes','crunchy_cheese',best_weapons['Physical']
        elif 'delicious_stone_craft_item' in crafts and crafts['delicious_stone_craft_item'] >= 30: 
            num = crafts['delicious_stone_craft_item']//30
            if current_location != 'derr_dunes': travel('derr_dunes')
            buy('curds_and_whey_craft_item',10*num)
            buy('coconut_milk_craft_item',20*num)
            buy('salt_craft_item',30*num)
            craft({'curds_and_whey_craft_item':10,'coconut_milk_craft_item':20,'salt_craft_item':30,'delicious_stone_craft_item':30},num)
        else: target_location, target_bait, target_weapon, target_item = 'derr_dunes','gouda_cheese',best_weapons['Physical'],'delicious_stone_craft_item'
    elif 'yellow_pepper_seed_craft_item' not in crafts or ('c' in args.z and 'blue_pepper_seed_craft_item' in crafts and crafts['yellow_pepper_seed_craft_item'] < crafts['blue_pepper_seed_craft_item']) or crafts['yellow_pepper_seed_craft_item'] < seeds_num:
        if 'gumbo_cheese' in baits: target_location, target_bait, target_weapon = 'nerg_plains','gumbo_cheese',best_weapons['Tactical']
        elif 'savoury_vegetables_craft_item' in crafts and crafts['savoury_vegetables_craft_item'] >= 30: 
            num = crafts['savoury_vegetables_craft_item']//30
            if current_location != 'nerg_plains': travel('nerg_plains')
            buy('curds_and_whey_craft_item',90*num)
            buy('coconut_milk_craft_item',15*num)
            buy('salt_craft_item',num)
            craft({'curds_and_whey_craft_item':90,'coconut_milk_craft_item':15,'salt_craft_item':1,'savoury_vegetables_craft_item':30},num)
        else: target_location, target_bait, target_weapon, target_item = 'nerg_plains','gouda_cheese',best_weapons['Tactical'], 'savoury_vegetables_craft_item'
    else: 
        if 'shell_cheese' in baits: target_location, target_bait, target_weapon = 'elub_shore','shell_cheese',best_weapons['Hydro']
        elif 'seashell_craft_item' in crafts and crafts['seashell_craft_item'] >= 30: 
            num = crafts['seashell_craft_item']//30
            if current_location != 'elub_shore': travel('elub_shore')
            buy('curds_and_whey_craft_item',60*num)
            buy('coconut_milk_craft_item',10*num)
            buy('salt_craft_item',40*num)
            craft({'curds_and_whey_craft_item':60,'coconut_milk_craft_item':10,'salt_craft_item':40,'seashell_craft_item':30},num)
        else: target_location, target_bait, target_weapon, target_item = 'elub_shore','gouda_cheese',best_weapons['Hydro'], 'seashell_craft_item'

    if target_weapon or target_bait or target_location:
        if target_location and current_location != target_location: travel(target_location)
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if not target_item: print('[%s] [%s] hunting at %s with %s: %s %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_location.replace('_',' '),target_weapon.replace('_',' '),baits[target_bait],target_bait.replace('_',' ')))
        elif target_item != 'pinch': print('[%s] [%s] hunting for %s, gotten %s. %s %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_item.replace('_craft_item','').replace('_',' '),crafts[target_item] if target_item in crafts else 0,baits[target_bait],target_bait.replace('_',' ')))
    elif loop_counter > 10: print('looped too many times. quitting!'); quit()
    else: tribal(loop_counter+1)
    
def digby(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_location, target_bait, target_base, target_trinket = '','','','',''
    
    if 'laboratory' not in allowed_regions: return print('[%s] [%s] no access to laboratory. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'town_of_digby' not in allowed_regions: return print('[%s] [%s] no access to digby. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    if 'limelight_cheese' in baits: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'town_of_digby', 'limelight_cheese', best_weapons['Physical'], best_base,'drilling_trinket' if 'drilling_trinket' in trinkets else None
        print('[%s] [%s] using limelight at digby: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['limelight_cheese']))
    elif 'radioactive_sludge_craft_item' in crafts and crafts['radioactive_sludge_craft_item'] >= 3:
        num = crafts['radioactive_sludge_craft_item']//3
        if current_location != 'town_of_digby': travel('town_of_digby')
        buy('curds_and_whey_craft_item',30*num)
        buy('living_shard_crafting_item',3*num)
        craft({'curds_and_whey_craft_item':30,'living_shard_crafting_item':3,'radioactive_sludge_craft_item':3},num)
    elif 'radioactive_blue_cheese' in baits:
        target_location, target_bait, target_weapon, target_base, target_trinket = 'mountain', 'radioactive_blue_cheese', best_weapons['Physical'], 'explosive_base' if 'explosive_base' in bases else best_base, None
        print('[%s] [%s] getting sludge: have %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['radioactive_sludge_craft_item'] if 'radioactive_sludge_craft_item' in crafts else 0))
    elif 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
    elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
    else: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'laboratory', 'brie_cheese', best_weapons['Physical'], best_base, None
        print('[%s] [%s] hunting for radioactive potion'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
        
    if target_location:
        if target_location != current_location: travel(target_location)
        if target_bait != current_bait: arm_bait(target_bait)
        if target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_base != current_base: arm_base(target_base)
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: digby(loop_counter+1)

def toxic(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_location, target_bait, target_base, target_trinket = '','','','',''
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 30: buy('brie_cheese',30)
    
    if 'pollution_outbreak' not in allowed_regions: return print('[%s] [%s] no access to toxic spill. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Hydro' not in best_weapons: return print('[%s] [%s] no hydro trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    done,rank_diff = 0,[]
    
    if 'radioactive_sludge_craft_item' in crafts and 'radioactive_curd_crafting_item' in crafts and crafts['radioactive_curd_crafting_item'] >= 2:
        num = min(crafts['radioactive_curd_crafting_item']//2,crafts['radioactive_sludge_craft_item'])
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < num: buy('ionized_salt_craft_item',num)
        craft({'ionized_salt_craft_item':1,'radioactive_sludge_craft_item':1,'radioactive_curd_crafting_item':2},qty=num)
    if 'super_radioactive_blue_potion' in potions and 'radioactive_blue_cheese' in baits and baits['radioactive_blue_cheese'] >= 6: potion('super_radioactive_blue_potion',get_recipes(j,'super_radioactive_blue_potion')[1],qty=min(potions['super_radioactive_blue_potion'],baits['radioactive_blue_cheese']//6))
    
    if 'super_radioactive_blue_cheese' in baits or 'magical_radioactive_blue_cheese' in baits:
        k = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Travel'},cookies=cookies,headers=post_headers).text)
        ranks = ['Hero','Knight','Lord/Lady','Baron/Baroness','Count/Countess','Duke/Duchess','Grand Duke/Grand Duchess','Archduke/Archduchess']
        current_rank = ranks.index(k['user']['title_name'])
        required_rank = ranks.index([p for p in [p for p in k['page']['tabs'][0]['regions'] if p['type']=='burroughs'][0]['environments'] if p['type']=='pollution_outbreak'][0]['title_name'])
        if required_rank > current_rank: rank_diff = [required_rank,current_rank]
        else:
            if current_location != 'pollution_outbreak':
                travel('pollution_outbreak')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            j = j['user']['quests']['QuestPollutionOutbreak']
            done,target_location,target_weapon,target_base = 1,'pollution_outbreak',best_weapons['Hydro'],best_base
            mp,rs,rq,rp,cp = min(j['max_pollutinum'],int(''.join([c for c in '0'+args.z if c.isdigit()]))),j['refine_status'],j['refine_quantity'],j['refined_pollutinum'],j['items']['crude_pollutinum_stat_item']['quantity'] if 'crude_pollutinum_stat_item' in j['items'] else 0
            
            if (rs == 'default' and (cp + rq > mp or ('r' in args.z and cp > rq))) or (rs == 'active' and (cp < rq or ('c' in args.z and cp + rq < mp))): 
                requests.post('https://www.mousehuntgame.com/managers/ajax/environment/pollution_outbreak.php',{'uh':hash,'action':'toggle_refine_mode'},headers=post_headers,cookies=cookies)
                rs = 'default' if rs == 'active' else 'active'
            
            if 'magical_radioactive_blue_cheese' in baits: target_bait = 'magical_radioactive_blue_cheese'
            else: target_bait = 'super_radioactive_blue_cheese'
            if rs == 'active': 
                target_trinket = 'super_soap_trinket' if 'super_soap_trinket' in trinkets else 'soap_trinket' if 'soap_trinket' in trinkets else None
                if 'super_scum_scrubber_weapon' in weapons: target_weapon = 'super_scum_scrubber_weapon'
            else: target_trinket = 'super_staling_trinket' if 'super_staling_trinket' in trinkets else 'staling_trinket' if 'staling_trinket' in trinkets else None
            
            print('[%s] [%s] hunting at spill with %s. bait left: %s, mode: %s, crude: %s, refined: %s. '%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),'magical' if target_bait=='magical_radioactive_blue_cheese' else 'rancid',baits[target_bait],'collecting' if rs == 'default' or rs == 'disabled' else 'refining',cp, rp))
                
    if done: pass
    elif 'radioactive_sludge_craft_item' in crafts and 'radioactive_blue_cheese' in baits and baits['radioactive_blue_cheese'] >= 2: hammer('radioactive_blue_cheese',min(crafts['radioactive_sludge_craft_item'],baits['radioactive_blue_cheese']//2)*2)
    elif 'super_radioactive_blue_potion' not in potions and 'radioactive_blue_cheese' in baits:
        target_location, target_bait, target_weapon, target_base = 'mountain', 'radioactive_blue_cheese', best_weapons['Physical'], 'explosive_base'
        print('[%s] [%s] getting sludge: have %s%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['radioactive_sludge_craft_item'] if 'radioactive_sludge_craft_item' in crafts else 0,'. required rank: %s, current rank: %s'%(rank_diff[0],rank_diff[1]) if rank_diff else ''))
    elif 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
    elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
    else: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'laboratory', 'brie_cheese', best_weapons['Physical'], best_base, None
        print('[%s] [%s] hunting for radioactive potion%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),'. required rank: %s, current rank: %s'%(rank_diff[0],rank_diff[1]) if rank_diff else ''))
        
    if target_bait:
        if target_location and target_location != current_location: travel(target_location)
        if target_bait and target_bait != current_bait: arm_bait(target_bait)
        if target_weapon and target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_base and target_base != current_base: arm_base(target_base)
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: toxic(loop_counter+1)

def iceberg():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'iceberg' not in allowed_regions: return print('[%s] [%s] no access to iceberg. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    if current_location != 'iceberg':
        travel('iceberg')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    progress = int(j['user']['quests']['QuestIceberg']['user_progress'])
    turns = j['user']['quests']['QuestIceberg']['turns_taken']
    
    num_trinket = 0
    if 'trinket_name' in j['user'] and current_trinket in ['sticky_trinket','wax_trinket']: num_trinket = int(j['user']['trinket_quantity'])
    elif 'wax_trinket' in trinkets: 
        current_trinket,num_trinket = 'wax_trinket',trinkets['wax_trinket']
        arm_charm(current_trinket)
    elif 'sticky_trinket' in trinkets: 
        current_trinket,num_trinket = 'sticky_trinket',trinkets['sticky_trinket']
        arm_charm(current_trinket)
    
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] <= 10: buy('gouda_cheese',100)
    if current_bait != 'gouda_cheese': arm_bait('gouda_cheese')
    
    good_weapons = ['steam_laser_mk_iii_weapon','steam_laser_mk_ii_weapon','steam_laser_mk_i_weapon']
    for weapon in good_weapons: 
        if weapon in weapons: 
            target_weapon = weapon
            break
    else: 
        print('[%s] [%s] no steam laser weapon. aborting!'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
        quit()
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    
    if progress <= 300: segment,target_base = 'treacherous tunnels','magnet_base'
    elif progress <= 600: segment,target_base = 'brutal bulwark','spiked_base'
    elif progress <= 1600: segment,target_base = 'bombing run','remote_detonator_base'
    elif progress < 1800: segment,target_base = 'mad depths','hearthstone_base'
    elif progress == 1800: segment,target_base = 'icewing\'s lair','deep_freeze_base'
    else: segment,target_base = 'hidden depths','deep_freeze_base'
    
    target_base = 'iceberg_boiler_base' if 'iceberg_boiler_base' in bases else target_base if target_base in bases else best_base
    if target_base != current_base: arm_base(target_base)
    print('[%s] [%s] progress: %s feet (%s), hunt #%s. %s left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),progress,segment,turns,current_trinket,num_trinket))

def zzt_parse(i): return 'not trying' if i < 0 else 'done' if i > 15 else 'got queen' if i > 14 else 'got %s rook%s'%(i-12,'s' if i-13 else '') if i > 12 else 'got %s bishop%s'%(i-10,'s' if i-11 else '') if i > 10 else 'got %s knight%s'%(i-8,'s' if i-9 else '') if i > 8 else 'got %s pawn%s'%(i,'' if i == 1 else 's')
def zzt():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait, target_weapon, target_trinket, target_base = '','','',''
    
    if 'seasonal_garden' not in allowed_regions: return print('[%s] [%s] no access to zzt. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Tactical' not in best_weapons: return print('[%s] [%s] no tactical trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    if current_location not in ['seasonal_garden','zugzwang_tower']:
        travel('zugzwang_tower')
        travel('seasonal_garden')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    amplifier, maxamp = int(j['user']['viewing_atts']['zzt_amplifier']), int(j['user']['viewing_atts']['zzt_max_amplifier'])
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] <= 10: buy('gouda_cheese',100)
    
    if 'mystic_curd_crafting_item' in crafts and 'tech_cheese_mould_crafting_item' in crafts:
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < 12: buy('ionized_salt_craft_item',12)
        num_sb = baits['super_brie_cheese'] if 'super_brie_cheese' in baits and args.z and 's' in args.z else 0
        num_me = crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts and args.z and 's' in args.z else 0
        if num_sb + num_me >= 6:
            hammer('super_brie_cheese',6-num_me)
            craft({'tech_cheese_mould_crafting_item':1,'mystic_curd_crafting_item':1,'ionized_salt_craft_item':12,'magic_essence_craft_item':6})
        else: craft({'tech_cheese_mould_crafting_item':1,'mystic_curd_crafting_item':1,'ionized_salt_craft_item':12})
        
    if amplifier == maxamp or (current_location == 'zugzwang_tower' and amplifier):
        if current_location != 'zugzwang_tower': 
            travel('zugzwang_tower')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        tech_progress, mage_progress = int(j['user']['viewing_atts']['zzt_tech_progress']), int(j['user']['viewing_atts']['zzt_mage_progress'])
        target_base = best_base if amplifier < 60 or 'wooden_base_with_target' not in bases else 'wooden_base_with_target'
        
        if args.z and 'm' in args.z and 't' not in args.z: tech_progress = -1 if mage_progress < 16 else tech_progress
        elif args.z and 't' in args.z and 'm' not in args.z: mage_progress = -1 if tech_progress < 16 else mage_progress
        if mage_progress == tech_progress:
            if random.random() >= 0.5: mage_progress -= 1
            else: tech_progress -= 1

        if (mage_progress == 16 or tech_progress == 16) and 'c' in args.z and 'checkmate_cheese' in baits: target_bait,target_weapon,target_trinket = 'checkmate_cheese',best_weapons['Tactical'],None
        elif mage_progress == 16 or (tech_progress > mage_progress and tech_progress < 16): 
            target_weapon = 'technic_low_weapon' if tech_progress < 8 else 'obvious_ambush_weapon' if 'obvious_ambush_weapon' in weapons else best_weapons['Tactical']
            target_trinket = 'rook_crumble_trinket' if tech_progress in [12,13] and 'rook_crumble_trinket' in trinkets else 'spellbook_trinket' if amplifier < 60 and 'spellbook_trinket' in trinkets else None
            target_bait = 'checkmate_cheese' if 'checkmate_cheese' in baits and tech_progress >= (14 if args.z and 'q' in args.z else 15) and (args.z and ('c' in args.z or 'd' in args.z)) and mage_progress != 16 else 'gouda_cheese'
        else: 
            target_weapon = 'mystic_low_weapon' if mage_progress < 8 else 'blackstone_pass_weapon' if 'blackstone_pass_weapon' in weapons else best_weapons['Tactical']
            target_trinket = 'rook_crumble_trinket' if mage_progress in [12,13] and 'rook_crumble_trinket' in trinkets else 'spellbook_trinket' if amplifier < 60 and 'spellbook_trinket' in trinkets else None
            target_bait = 'checkmate_cheese' if 'checkmate_cheese' in baits and mage_progress >= (14 if args.z and 'q' in args.z else 15) and (args.z and ('c' in args.z or 'd' in args.z)) and tech_progress != 16 else 'gouda_cheese'

        print('[%s] [%s] hunting at tower. mystic progress: %s/16 (%s), technic progress: %s/16 (%s). amplifier: %s/%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),mage_progress,zzt_parse(mage_progress),tech_progress,zzt_parse(tech_progress),amplifier,maxamp))
    else: 
        if current_location != 'seasonal_garden': 
            travel('seasonal_garden')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        season = j['user']['viewing_atts']['season']
        
        target_base = best_base
        target_bait,target_trinket = 'gouda_cheese','amplifier_trinket' if 'amplifier_trinket' in trinkets else None
        num_trinket = trinkets[target_trinket] if target_trinket in trinkets else 0
        if season == 'sr': target_weapon = best_weapons['Tactical']
        elif season == 'sg': target_weapon = best_weapons['Physical'] if 'Physical' in best_weapons else best_weapons['Tactical']
        elif season == 'fl': target_weapon = best_weapons['Shadow'] if 'Shadow' in best_weapons else best_weapons['Tactical']
        elif season == 'wr': target_weapon = best_weapons['Hydro'] if 'Hydro' in best_weapons else best_weapons['Tactical']
        
        print('[%s] [%s] charging amplifier: %s/%s. amplifier charms: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),amplifier,maxamp,num_trinket))
    
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    if current_bait != target_bait: arm_bait(target_bait)
    if current_base != target_base: arm_base(best_base)
    if current_trinket != target_trinket: arm_charm(target_trinket if target_trinket else 'disarm')

def city():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'claw_shot_city' not in allowed_regions: return print('[%s] [%s] no access to claw shot city. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Law' not in best_weapons: return print('[%s] [%s] no law trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'claw_shot_city': 
        travel('claw_shot_city')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_base != best_base: arm_base(best_base)
    if current_weapon != best_weapons['Law']: arm_weapon(best_weapons['Law'])
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 20: buy('brie_cheese',30)
    if current_bait != 'brie_cheese': arm_bait('brie_cheese')
    if 'mining_trinket' not in trinkets or trinkets['mining_trinket'] < 10: buy('mining_trinket',10)
    target_trinket = 'sheriff_badge_trinket' if 'sheriff_badge_trinket' in trinkets and j['user']['quests']['QuestClawShotCity']['phase'] in ['need_poster','has_reward'] and 'wanted_poster_convertible' not in chests else 'cactus_trinket' if 'cactus_trinket' in trinkets else 'mining_trinket'
    if current_trinket != target_trinket: arm_charm(target_trinket)
    if j['user']['quests']['QuestClawShotCity']['phase'] == 'has_reward': 
        mapid = j['user']['quests']['QuestRelicHunter']['maps'][0]['map_id']
        requests.post('https://www.mousehuntgame.com/managers/ajax/users/treasuremap.php',{'action':'claim','uh':hash,'map_id':mapid},headers=post_headers,cookies=cookies)
    if 'wanted_poster_convertible' in chests and j['user']['quests']['QuestClawShotCity']['phase'] in ['has_poster','has_reward']: requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'wanted_poster_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    if 'bounty_reward_f_convertible' in chests: requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'bounty_reward_f_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    
def train():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon,target_trinket = best_weapons['Law'],''
    
    if 'Law' not in best_weapons: return print('[%s] [%s] no law trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'train_station' not in allowed_regions: return print('[%s] [%s] no access to train station. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'train_station':
        travel('train_station')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'QuestTrainStation' not in j['user']['quests'] or not j['user']['quests']['QuestTrainStation']['on_train']: return print('[%s] [%s] no train quest active. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 20: buy('brie_cheese',30)
    if current_bait != 'brie_cheese': arm_bait('brie_cheese')

    fg = [c['quantity'] for c in j['components'] if c['type']=='fools_gold_stat_item']
    fg = fg[0] if fg else 0
    j = j['user']['quests']['QuestTrainStation']
    phase,phase_time,target_points,current_points = j['current_phase'],j['phase_seconds_remaining'],j['team_goal'],j['score']
    
    if phase == 'supplies':
        if 'engine_doubler_weapon' in weapons: target_weapon = 'engine_doubler_weapon'
        crates = j['minigame']['supply_crates']
        if crates and 's' not in args.z: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/train_station.php',{'uh':hash,'action':'load_supply_crates'},headers=post_headers,cookies=cookies)
        supply_hoarder_rounds = j['minigame']['supply_hoarder_turns']
        if supply_hoarder_rounds or ('book_warmer_trinket' not in trinkets and (current_points >= target_points or not fg or 'f' in args.z)):
            target_trinket = 'mining_trinket'
            if 'mining_trinket' not in trinkets or trinkets['mining_trinket'] < 10: buy('mining_trinket',30)    
            report = 'hoarder rounds: %s'%(supply_hoarder_rounds if supply_hoarder_rounds else 'not trying')   
        else: 
            target_trinket = 'book_warmer_trinket'
            if 'book_warmer_trinket' not in trinkets and fg: buy('book_warmer_trinket',1)
            report = 'using charm'
        report += ', crates: %s'%crates
    elif phase == 'boarding': 
        if 'bandit_deflector_weapon' in weapons: target_weapon = 'bandit_deflector_weapon'
        repellents = j['minigame']['mouse_repellent']
        if repellents and 's' not in args.z: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/train_station.php',{'uh':hash,'action':'use_mouse_repellent'},headers=post_headers,cookies=cookies)
        target_trinket = 'trouble_area_%s_trinket'%j['minigame']['trouble_area']        
        report = 'area: %s '%j['minigame']['trouble_area']
        if target_trinket not in trinkets and (current_points >= target_points or not fg or 'f' in args.z):
            target_trinket = 'mining_trinket'
            if 'mining_trinket' not in trinkets or trinkets['mining_trinket'] < 10: buy('mining_trinket',30)
            report += '(no charm)'
        else: 
            if target_trinket not in trinkets and fg: buy(target_trinket,1)
            report += '(charm)'
        report += ', repellant: %s'%repellents
    elif phase == 'bridge_jump':
        if 'supply_grabber_weapon' in weapons: target_weapon = 'supply_grabber_weapon'
        coals = j['minigame']['fuel_nuggets']
        points = coals if coals < 10 else coals*2 - 10
        if 's' not in args.z and (coals >= 20 or (points >= target_points - current_points and current_points < target_points)): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/train_station.php',{'uh':hash,'action':'use_fuel_nuggets'},headers=post_headers,cookies=cookies)
        for trinket in ['train_magmatic_crystal_trinket','train_black_powder_trinket','train_coal_trinket']:
            if trinket in trinkets and current_points < target_points: 
                target_trinket = trinket
                break
        else:
            if fg and 'f' not in args.z and current_points < target_points:
                target_trinket = 'train_coal_trinket'
                if target_trinket not in trinkets: buy(target_trinket,1)            
            else: 
                target_trinket = 'mining_trinket'
                if target_trinket not in trinkets or trinkets[target_trinket] < 10: buy(target_trinket,30)
        report = 'coals: %s, charm: %s'%(coals,target_trinket)
    
    print('[%s] [%s] fools gold: %s, points: %s/%s. phase: %s (%02d:%02d:%02d left), %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),fg,current_points,target_points,phase,phase_time//3600,(phase_time%3600)//60,phase_time%60,report))
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    if current_base != best_base: arm_base(best_base)
    if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        
def fiery(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'desert_warpath' not in allowed_regions: return print('[%s] [%s] no access to fiery warpath. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'desert_warpath':
        travel('desert_warpath')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 20: buy('gouda_cheese',20)
    if current_bait != 'gouda_cheese': arm_bait('gouda_cheese')
    if current_base != best_base: arm_base(best_base)
    commander_threshold = int(''.join([c for c in '0'+args.z if c.isdigit()]))
    level = j['user']['viewing_atts']['desert_warpath']['wave']
    streak = j['user']['viewing_atts']['desert_warpath']['streak_quantity']   
    mice = {m:j['user']['viewing_atts']['desert_warpath']['mice'][m]['quantity'] for m in j['user']['viewing_atts']['desert_warpath']['mice'] if j['user']['viewing_atts']['desert_warpath']['mice'][m]['quantity']}
    
    if 'c' not in args.z and 'desert_horseshoe_crafting_item' in crafts and 'simple_orb_crafting_item' in crafts: 
        num = min(crafts['desert_horseshoe_crafting_item'],crafts['simple_orb_crafting_item'])
        if 'charmbit_crafting_item' not in crafts or crafts['charmbit_crafting_item'] < 2*num: buy('charmbit_crafting_item',2*num-(crafts['charmbit_crafting_item'] if 'charmbit_crafting_item' in crafts else 0))
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < num: buy('ionized_salt_craft_item',num-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        craft({'desert_horseshoe_crafting_item':1,'simple_orb_crafting_item':1,'ionized_salt_craft_item':1,'charmbit_crafting_item':2},num)
    if 'c' not in args.z and 'heatproof_mage_cloth_crafting_item' in crafts and 'simple_orb_crafting_item' in crafts: 
        num = min(crafts['heatproof_mage_cloth_crafting_item'],crafts['simple_orb_crafting_item'])
        if 'charmbit_crafting_item' not in crafts or crafts['charmbit_crafting_item'] < 2*num: buy('charmbit_crafting_item',2*num-(crafts['charmbit_crafting_item'] if 'charmbit_crafting_item' in crafts else 0))
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < num: buy('ionized_salt_craft_item',num-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        craft({'heatproof_mage_cloth_crafting_item':1,'simple_orb_crafting_item':1,'ionized_salt_craft_item':1,'charmbit_crafting_item':2},num)
    
    if commander_threshold and streak >= commander_threshold: target,target_weapon,target_trinket = 'commander',best_weapon,'super_flame_march_general_trinket' if 'super_flame_march_general_trinket' in trinkets else 'flame_march_general_trinket'
    elif streak > (6 if 'g' in args.z else 8): target,target_weapon,target_trinket = 'gargantua',best_weapons['Draconic'],'gargantua_trinket'
    elif level == 4: target,target_trinket,target_weapon = 'desert_elite_gaurd' if 'desert_elite_gaurd' in mice else 'desert_boss',None,best_weapons['Physical']
    else: 
        d = {1: ['desert_warrior_weak','desert_scout_weak','desert_archer_weak'], 2: ['desert_warrior','desert_scout','desert_archer','desert_mage','desert_cavalry'], 3: ['desert_warrior_epic','desert_scout_epic','desert_archer_epic','desert_mage_strong','desert_cavalry_strong','desert_artillery']}
        for m in [j['user']['viewing_atts']['desert_warpath']['streak_type']]+d[level]:
            if m in mice and mice[m]:
                type = m.split('_')[1]
                target,target_trinket,target_weapon = m,'super_flame_march_%s_trinket'%(type) if 'super_flame_march_%s_trinket'%(type) in trinkets else 'flame_march_%s_trinket'%(type),best_weapons['Tactical'] if type=='cavalry' else best_weapons['Hydro'] if type=='mage' else best_weapons['Arcane'] if type=='artillery' else best_weapons['Physical']; break
    
    if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
    if target_trinket not in trinkets:
        if target_trinket in ['flame_march_warrior_trinket','flame_march_scout_trinket','flame_march_archer_trinket']: buy(target_trinket,10)
        else: target_trinket = None
    if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    print('[%s] [%s] level: %s, streak: %s. target: %s, quantity: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),level,streak,target,mice[target] if target in mice else '1'))

def fort():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'fort_rox' not in allowed_regions: return print('[%s] [%s] no access to fort rox. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Law','Arcane','Shadow']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if current_location != 'fort_rox':
        travel('fort_rox')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    j = j['user']['quests']['QuestFortRox']
    if j['current_phase'] == 'day':
        if 'meteorite_piece_craft_item' in crafts and j['max_hp'] - j['hp'] <= crafts['meteorite_piece_craft_item']: pass
        target_weapon, target_bait = best_weapons['Law'],'gouda_cheese'
        print('[%s] [%s] DAY. meteorite: %s, howlite: %s, bloodstone: %s. wall: %s/%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['meteorite_piece_craft_item'] if 'meteorite_piece_craft_item' in crafts else 0,stats['howlite_stat_item'] if 'howlite_stat_item' in stats else 0,stats['blood_stone_stat_item'] if 'blood_stone_stat_item' in stats else 0,j['hp'],j['max_hp']))
    else:
        if j['current_stage'] in ['stage_one','stage_two']: target_weapon = best_weapons['Shadow']
        else: target_weapon = best_weapons['Arcane']
        
        if 't' in args.z and j['current_phase'] != 'dawn' and 'fort_rox_tower_mana_stat_item' in stats and ((j['hp'] < j['max_hp']) == (j['tower_status'] == 'normal inactive')): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/fort_rox.php',{'uh':hash,'action':'toggle_tower'},cookies=cookies,headers=post_headers)
        if 'moon_cheese' in baits and 'm' in args.z: target_bait = 'moon_cheese'
        elif 'crescent_cheese' in baits: target_bait = 'crescent_cheese'
        else: target_bait = 'gouda_cheese'
        
        print('[%s] [%s] NIGHT. phase: %s, hunts left: %s. meteorite: %s, howlite: %s, bloodstone: %s, dust: %s. wall: %s/%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),'twilight' if j['current_stage']=='stage_one' else 'midnight' if j['current_stage']=='stage_two' else 'pitch' if j['current_stage']=='stage_three' else 'darkness' if j['current_stage']=='stage_four' else 'first light' if j['current_stage']=='stage_five' else 'dawn',j['hunts_until_next_phase'] if j['hunts_until_next_phase'] else j['hunts_until_dawn'],crafts['meteorite_piece_craft_item'] if 'meteorite_piece_craft_item' in crafts else 0,stats['howlite_stat_item'] if 'howlite_stat_item' in stats else 0,stats['blood_stone_stat_item'] if 'blood_stone_stat_item' in stats else 0,stats['dawn_dust_stat_item'] if 'dawn_dust_stat_item' in stats else 0,j['hp'],j['max_hp']))
    
    if current_base != best_base: arm_base(best_base)
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 100: buy('gouda_cheese',100)
    if target_weapon:
        if current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_bait != target_bait: arm_bait(target_bait)

def garden(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_bait, target_location, target_trinket = '','','',''
    
    if 'desert_oasis' not in allowed_regions: return print('[%s] [%s] no access to living garden. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Hydro','Arcane','Shadow']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    
    if current_location not in ['desert_oasis','lost_city','sand_dunes']:
        travel('desert_oasis')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    for i in ['QuestLivingGarden','QuestLostCity','QuestSandDunes']:
        if i in j['user']['quests']: normal = j['user']['quests'][i]['is_normal']; break

    if ('dewthief_petal_crafting_item' in crafts and crafts['dewthief_petal_crafting_item'] > 1) or ('duskshade_petal_crafting_item' in crafts and crafts['duskshade_petal_crafting_item'] > 1 and 'dreamfluff_herbs_crafting_item' in crafts and crafts['dreamfluff_herbs_crafting_item'] > 1) or ('graveblossom_petal_crafting_item' in crafts and crafts['graveblossom_petal_crafting_item'] > 1) or ('lunaria_petal_crafting_item' in crafts and crafts['lunaria_petal_crafting_item'] > 1 and 'plumepearl_herbs_crafting_item' in crafts and crafts['plumepearl_herbs_crafting_item'] > 1):
        if current_location not in ['desert_oasis','lost_city','sand_dunes']: travel('desert_oasis')
        if 'dewthief_petal_crafting_item' in crafts and crafts['dewthief_petal_crafting_item'] > 1: buy('dewthief_camembert_cheese',crafts['dewthief_petal_crafting_item']-1)
        if 'duskshade_petal_crafting_item' in crafts and crafts['duskshade_petal_crafting_item'] > 1 and 'dreamfluff_herbs_crafting_item' in crafts and crafts['dreamfluff_herbs_crafting_item'] > 1: buy('duskshade_camembert_cheese',min(crafts['duskshade_petal_crafting_item'],crafts['dreamfluff_herbs_crafting_item'])-1)
        if 'graveblossom_petal_crafting_item' in crafts and crafts['graveblossom_petal_crafting_item'] > 1: buy('graveblossom_camembert_cheese',crafts['graveblossom_petal_crafting_item']-1)
        if 'lunaria_petal_crafting_item' in crafts and crafts['lunaria_petal_crafting_item'] > 1 and 'plumepearl_herbs_crafting_item' in crafts and crafts['plumepearl_herbs_crafting_item'] > 1: buy('lunaria_camembert_cheese',min(crafts['lunaria_petal_crafting_item'],crafts['plumepearl_herbs_crafting_item'])-1)    
    elif not normal:
        if ('lunaria_camembert_cheese' in baits and 'c' not in args.z and 'd' not in args.z) or 'graveblossom_camembert_cheese' not in baits:
            if current_location != 'desert_oasis':
                travel('desert_oasis')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
                
            bucket,red_drops,yellow_drops,timer = j['user']['quests']['QuestLivingGarden']['minigame']['vials_state'],j['user']['quests']['QuestLivingGarden']['minigame']['red_drops'],j['user']['quests']['QuestLivingGarden']['minigame']['yellow_drops'],j['user']['quests']['QuestLivingGarden']['minigame']['timer']
            target_weapon, target_bait, target_trinket = best_weapons['Hydro'],'lunaria_camembert_cheese' if 'lunaria_camembert_cheese' in baits else 'duskshade_camembert_cheese' if 'duskshade_camembert_cheese' in baits else 'gouda_cheese',None
            
            if target_bait == 'lunaria_camembert_cheese': pass
            elif red_drops >= 10 and yellow_drops >= 10: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/livinggarden.php',{'action':'dump_bucket','uh':hash},cookies=cookies,headers=post_headers)
            elif red_drops < 10: target_trinket = 'red_sponge_trinket'
            else: target_trinket = 'yellow_sponge_trinket'
            
            if target_trinket and target_trinket not in trinkets:
                if 'essence_b_crafting_item' in crafts: buy(target_trinket,1)
                else: target_trinket = None
                
            print(('[%s] [%s] using %s at twisted %s: %s left. %s bucket: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],bucket,'red: %s/10, yellow: %s/10, red charms: %s, yellow charms: %s'%(red_drops,yellow_drops,trinkets['red_sponge_trinket'] if 'red_sponge_trinket' in trinkets else 0,trinkets['yellow_sponge_trinket'] if 'yellow_sponge_trinket' in trinkets else 0) if bucket == 'filling' else '%s turns left'%timer)).replace('_cheese','').replace('_',' '))
            
        elif 'c' in args.z or ('d' not in args.z and 'lunaria_petal_crafting_item' in crafts and crafts['lunaria_petal_crafting_item'] > 1):
            if current_location != 'lost_city':
                travel('lost_city')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            
            curses = [d for d in j['user']['quests']['QuestLostCity']['minigame']['curses'] if d['active']]
            target_weapon, target_bait, target_trinket = best_weapons['Arcane'],'graveblossom_camembert_cheese',None
            if curses: target_trinket = curses[0]['charm']['name'].lower().replace(' charm','_trinket')
            
            if target_trinket and target_trinket not in trinkets:
                if 'essence_b_crafting_item' in crafts: buy(target_trinket,1)
                else: target_trinket = None
            
            print(('[%s] [%s] using %s at twisted %s: %s left. curses: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],', '.join(d['type'] for d in curses) if curses else 'off')).replace('_cheese','').replace('_',' '))
            
        else:
            if current_location != 'sand_dunes':
                travel('sand_dunes')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            
            salts = j['user']['quests']['QuestSandDunes']['minigame']['salt_charms_used']
            target_weapon, target_bait, target_trinket = best_weapons['Shadow'],'graveblossom_camembert_cheese','grub_scent_trinket' if salts >= 31 else 'grub_salt_trinket'
            
            if target_trinket and target_trinket not in trinkets:
                if target_trinket == 'grub_scent_trinket' and 'essence_c_crafting_item' in crafts: buy(target_trinket,min(5,crafts['essence_c_crafting_item']))
                elif target_trinket == 'grub_salt_trinket' and 'essence_b_crafting_item' in crafts: buy(target_trinket,min(5,crafts['essence_b_crafting_item']))
                else: target_trinket = None
            
            print(('[%s] [%s] using %s at twisted %s: %s left. salts: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],salts)).replace('_cheese','').replace('_',' '))
            
    elif ('duskshade_camembert_cheese' in baits and baits['duskshade_camembert_cheese'] > 20  and 'c' not in args.z and 'd' not in args.z) or 'dewthief_camembert_cheese' not in baits:
        if current_location != 'desert_oasis':
            travel('desert_oasis')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            
        bucket,drops,timer = j['user']['quests']['QuestLivingGarden']['minigame']['bucket_state'],j['user']['quests']['QuestLivingGarden']['minigame']['dewdrops'],j['user']['quests']['QuestLivingGarden']['minigame']['timer']
        target_weapon, target_bait = best_weapons['Hydro'],'duskshade_camembert_cheese' if 'duskshade_camembert_cheese' in baits and baits['duskshade_camembert_cheese'] > 20 else 'gouda_cheese'
        target_trinket = 'sponge_trinket' if bucket == 'filling' and drops < 20 and target_bait == 'gouda_cheese' else None
        
        if drops >= 20: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/livinggarden.php',{'action':'dump_bucket','uh':hash},cookies=cookies,headers=post_headers)        
        if target_trinket and target_trinket not in trinkets:
            if 'essence_a_crafting_item' in crafts: buy(target_trinket,min(crafts['essence_a_crafting_item'],20-drops))
            else: target_trinket = None
            
        print(('[%s] [%s] using %s at normal %s: %s left. %s bucket: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],bucket,'%s/%s, sponge charms: %s'%(drops,20,trinkets['sponge_trinket'] if 'sponge_trinket' in trinkets else 0) if bucket == 'filling' else '%s turns left'%timer)).replace('_cheese','').replace('_',' '))
        
    elif 'c' in args.z or ('d' not in args.z and 'duskshade_petal_crafting_item' in crafts and crafts['duskshade_petal_crafting_item'] > 1):
        if current_location != 'lost_city':
            travel('lost_city')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        curse = j['user']['quests']['QuestLostCity']['minigame']['is_cursed']
        target_weapon, target_bait, target_trinket = best_weapons['Arcane'],'dewthief_camembert_cheese', 'searcher_trinket' if curse else None
        
        if target_trinket and target_trinket not in trinkets:
            if 'essence_a_crafting_item' in crafts: buy(target_trinket,1)
            else: target_trinket = None
        
        print(('[%s] [%s] using %s at normal %s: %s left. curse: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],'on' if curse else 'off')).replace('_cheese','').replace('_',' '))
        
    else:
        if current_location != 'sand_dunes':
            travel('sand_dunes')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        
        stampede = j['user']['quests']['QuestSandDunes']['minigame']['has_stampede']
        target_weapon, target_bait, target_trinket = best_weapons['Shadow'],'dewthief_camembert_cheese','grubling_chow_trinket' if stampede else None
        if target_trinket and target_trinket not in trinkets:
            if 'essence_a_crafting_item' in crafts: buy(target_trinket,1)
            else: target_trinket = None
        
        print(('[%s] [%s] using %s at normal %s: %s left. stampede: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],'on' if stampede else 'off')).replace('_cheese','').replace('_',' '))

    best_base = 'living_base' if 'living_base' in bases else best_base
    if current_base != best_base: arm_base(best_base)
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 15: buy('gouda_cheese',15)    
    if target_weapon:
        if current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_bait != target_bait: arm_bait(target_bait)
        if current_trinket != target_trinket : arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: garden(loop_counter+1)

def grift(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'rift_gnawnia' not in allowed_regions: return print('[%s] [%s] no access to gnawnia rift. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'rift_gnawnia':
        travel('rift_gnawnia')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    
    try: best_base = max((c for c in j['components'] if c['classification']=='base' and 'tag_types' in c and 'rift' in c['tag_types']),key=lambda x:x['power'] if 'power' in x else 0)['type']
    except: pass
    if current_base != best_base: arm_base(best_base)
    target_weapon = best_weapons['Rift'] if 'Rift' in best_weapons else best_weapon
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    
    target_bait = ''
    b = 10 if 'b' in args.z else 0
    if 'gnawnia_boss_cheese' in baits and 'r' not in args.z: target_bait = 'gnawnia_boss_cheese'
    elif 'r' not in args.z and 'magic_seed_crafting_item' in crafts and crafts['magic_seed_crafting_item'] >= 3+b and 'riftgrass_crafting_item' in crafts and crafts['riftgrass_crafting_item'] >= 3+b and 'rift_dust_crafting_item' in crafts and crafts['rift_dust_crafting_item'] >= 3+b:
        n = min(crafts['magic_seed_crafting_item']-b,crafts['riftgrass_crafting_item']-b,crafts['rift_dust_crafting_item']-b)//3
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < n: buy('ionized_salt_craft_item',n-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        if 'rift_cheese_curd_crafting_item' not in crafts or crafts['rift_cheese_curd_crafting_item'] < n: buy('rift_cheese_curd_crafting_item',n-(crafts['rift_cheese_curd_crafting_item'] if 'rift_cheese_curd_crafting_item' in crafts else 0))
        craft({'magic_seed_crafting_item':3,'riftgrass_crafting_item':3,'rift_dust_crafting_item':3,'ionized_salt_craft_item':1,'rift_cheese_curd_crafting_item':1},n)
    elif 'riftiago_cheese' in baits: target_bait = 'riftiago_cheese'
    elif 'riftiago_potion' in potions: 
        buy('brie_string_cheese',3)
        potion('riftiago_potion',0,1)
    else: 
        target_bait = 'brie_string_cheese'
        if 'brie_string_cheese' not in baits or baits['brie_string_cheese'] < 10: buy('brie_string_cheese',10)
    
    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
        print('[%s] [%s] using %s: %s left. crystals: %s, seeds: %s, riftgrass: %s, riftdust: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,baits[target_bait] if target_bait in baits else 0,stats['raw_rift_crystal_stat_item'] if 'raw_rift_crystal_stat_item' in stats else 0,crafts['magic_seed_crafting_item'] if 'magic_seed_crafting_item' in crafts else 0,crafts['riftgrass_crafting_item'] if 'riftgrass_crafting_item' in crafts else 0,crafts['rift_dust_crafting_item'] if 'rift_dust_crafting_item' in crafts else 0))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: grift(loop_counter+1)

def fungal(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    for type in ['Hydro','Forgotten']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if 'fungal_cavern' not in allowed_regions: return print('[%s] [%s] no access to fungal cavern. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'fungal_cavern':
        travel('fungal_cavern')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if current_base != best_base: arm_base(best_base)
    target_weapon,target_bait = '',''
    
    if 'cavern_fungus_crafting_item' in crafts and crafts['cavern_fungus_crafting_item'] >= 3 and 'cave_nightshade_crafting_item' in crafts:
        n = min(crafts['cave_nightshade_crafting_item'],crafts['cavern_fungus_crafting_item']//3)
        if 'living_shard_crafting_item' not in crafts or crafts['living_shard_crafting_item'] < n*3: buy('living_shard_crafting_item',n*3-(crafts['living_shard_crafting_item'] if 'living_shard_crafting_item' in crafts else 0))
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < n*6: buy('ionized_salt_craft_item',n*6-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        if 'curds_and_whey_craft_item' not in crafts or crafts['curds_and_whey_craft_item'] < n*30: buy('curds_and_whey_craft_item',n*30-(crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0))
        craft({'cavern_fungus_crafting_item':3,'cave_nightshade_crafting_item':1,'living_shard_crafting_item':3,'ionized_salt_craft_item':6,'curds_and_whey_craft_item':30},n)
        if 'glowing_gruyere_cheese' not in baits: baits['glowing_gruyere_cheese'] = n
        else: baits['glowing_gruyere_cheese'] += n
    
    need_mineral = 'g' in args.z
    if 'diamond_cheese' in baits and not ('crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z): target_weapon,target_bait = best_weapons['Forgotten'],'diamond_cheese'
    elif 'diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 10 and 'mineral_crafting_item' in crafts and crafts['mineral_crafting_item'] >= 100 and not ('crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z):
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < 12: buy('ionized_salt_craft_item',12-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        if 'curds_and_whey_craft_item' not in crafts or crafts['curds_and_whey_craft_item'] < 3: buy('curds_and_whey_craft_item',3-(crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0))
        craft({'diamond_crafting_item':10,'mineral_crafting_item':100,'ionized_salt_craft_item':12,'curds_and_whey_craft_item':3},1)
    elif 'diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 10 and not ('crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z): need_mineral = True
    elif 'gemstone_cheese' in baits and not ('diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 5 and 'crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z): best_weapons['Forgotten'],'gemstone_cheese'
    elif 'gemstone_crafting_item' in crafts and crafts['gemstone_crafting_item'] >= 3 and 'mineral_crafting_item' in crafts and crafts['mineral_crafting_item'] >= 28 and not ('diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 5 and 'crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z): 
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < 6: buy('ionized_salt_craft_item',6-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        if 'curds_and_whey_craft_item' not in crafts or crafts['curds_and_whey_craft_item'] < 6: buy('curds_and_whey_craft_item',6-(crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0))
        craft({'gemstone_crafting_item':3,'mineral_crafting_item':28,'ionized_salt_craft_item':6,'curds_and_whey_craft_item':6},1)
    elif 'gemstone_crafting_item' in crafts and crafts['gemstone_crafting_item'] >= 3 and not ('diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 5 and 'crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z): need_mineral = True
    elif 'mineral_cheese' in baits and not ('gemstone_crafting_item' in crafts and crafts['gemstone_crafting_item'] >= 10 and 'diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 5 and 'crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z): target_weapon,target_bait = best_weapons['Forgotten'],'mineral_cheese'
    elif 'mineral_crafting_item' in crafts and crafts['mineral_crafting_item'] >= 12 and not ('gemstone_crafting_item' in crafts and crafts['gemstone_crafting_item'] >= 10 and 'diamond_crafting_item' in crafts and crafts['diamond_crafting_item'] >= 5 and 'crystal_crucible_crafting_item' in crafts and crafts['crystal_crucible_crafting_item'] >= 8 and 'b' in args.z):
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < 6: buy('ionized_salt_craft_item',6-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
        if 'curds_and_whey_craft_item' not in crafts or crafts['curds_and_whey_craft_item'] < 18: buy('curds_and_whey_craft_item',18-(crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0))
        craft({'mineral_crafting_item':12,'ionized_salt_craft_item':6,'curds_and_whey_craft_item':18},1)
    else: need_mineral = True
    
    if not need_mineral: pass
    elif 'g' not in args.z and 'glowing_gruyere_cheese' in baits: target_weapon,target_bait = best_weapons['Forgotten'],'glowing_gruyere_cheese'
    else: target_weapon,target_bait = best_weapons['Hydro'],'gouda_cheese'
    
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 100: buy('gouda_cheese',100)
    
    if target_weapon or target_bait:    
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if current_weapon != target_weapon: arm_weapon(target_weapon)
        print('[%s] [%s] using %s: %s left. %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_cheese','').replace('_',' '),baits[target_bait],', '.join('%s: %s'%(c.replace('_crafting_item','').replace('_',' '),crafts[c] if c in crafts else 0) for c in ['cavern_fungus_crafting_item','cave_nightshade_crafting_item','mineral_crafting_item','gemstone_crafting_item','diamond_crafting_item','crystal_crucible_crafting_item'])))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: fungal(loop_counter+1)
    
def brift():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'Rift' not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if 'rift_burroughs' not in allowed_regions: return print('[%s] [%s] no access to burroughs rift. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'rift_burroughs':
        travel('rift_burroughs')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    mist_level,canisters,misting,circuits = j['user']['quests']['QuestRiftBurroughs']['mist_released'],stats['mist_canister_stat_item'],bool(j['user']['quests']['QuestRiftBurroughs']['is_misting']),stats['rift_circuitry_stat_item'] if 'rift_circuitry_stat_item' in stats else 0
    
    try: best_base = max([c for c in j['components'] if c['classification']=='base' and 'tag_types' in c and 'rift' in c['tag_types']],key=lambda x:x['power'] if 'power' in x else 0)['type']
    except: pass
    
    if 'terre_ricotta_potion' in potions:
        buy('brie_string_cheese',potions['terre_ricotta_potion'])
        potion('terre_ricotta_potion',2,potions['terre_ricotta_potion'])
        if 'terre_ricotta_cheese' not in baits: baits['terre_ricotta_cheese'] = potions['terre_ricotta_potion']
        else: baits['terre_ricotta_cheese'] += potions['terre_ricotta_potion']
    if 'polluted_parmesan_potion' in potions:
        buy('brie_string_cheese',potions['polluted_parmesan_potion'])
        potion('polluted_parmesan_potion',2,potions['polluted_parmesan_potion'])
        if 'polluted_parmesan_cheese' not in baits: baits['polluted_parmesan_cheese'] = potions['polluted_parmesan_potion']
        else: baits['polluted_parmesan_cheese'] += potions['polluted_parmesan_potion']
    if 'brie_string_cheese' not in baits or baits['brie_string_cheese'] < 100: buy('brie_string_cheese',100)
    
    def toggle_mist(misting): 
        requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_burroughs.php',{'uh':hash,'action':('unmist' if misting else 'mist')},cookies=cookies,headers=post_headers)        
        return not misting
    
    if not mist_level:
        target_bait = 'brie_string_cheese'
        if (canisters > 100) != misting: misting = toggle_mist(misting)
    elif mist_level <= 5: target_bait = 'brie_string_cheese'
    elif mist_level <= 18:
        target_bait = 'terre_ricotta_cheese' if 'terre_ricotta_cheese' in baits and 'b' not in args.z and 't' not in args.z else 'brie_string_cheese'
        if ('g' in args.z and canisters and ((mist_level < 7) != misting)) or ('g' not in args.z and not misting): misting = toggle_mist(misting)
    elif 't' in args.z and 'terre_ricotta_cheese' not in baits:
        target_bait = 'brie_string_cheese'
        if misting: misting = toggle_mist(misting)
    else:
        target_bait = 'polluted_parmesan_cheese' if 'polluted_parmesan_cheese' in baits and 'b' not in args.z and 't' not in args.z else 'terre_ricotta_cheese' if 'terre_ricotta_cheese' in baits and 'b' not in args.z else 'brie_string_cheese'
        if canisters and ((mist_level == 19) != misting): misting = toggle_mist(misting)
        
    print('[%s] [%s] bait: %s. mist: %s, level: %s, canisters: %s, circuits: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_cheese','').replace('_',' '),'on' if misting else 'off',mist_level,canisters,circuits))
    if current_weapon != best_weapons['Rift']: arm_weapon(best_weapons['Rift'])
    if current_base != best_base: arm_base(best_base)
    if current_bait != target_bait: arm_bait(target_bait)

def frift(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'Rift' not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if 'rift_furoma' not in allowed_regions: return print('[%s] [%s] no access to furoma rift. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'rift_furoma':
        travel('rift_furoma')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    try: best_base = max([c for c in j['components'] if c['classification']=='base' and 'tag_types' in c and 'rift' in c['tag_types']],key=lambda x:x['power'] if 'power' in x else 0)['type']
    except: pass
    
    bml = sum(1 for c in j['user']['quests']['QuestRiftFuroma']['batteries'].values() if c['status'].split()[0] == 'unlocked')
    bcl = sum(1 for c in j['user']['quests']['QuestRiftFuroma']['batteries'].values() if c['status'].split()[0] == 'unlocked' and c['remaining'])
    bcp = max(c['total'] for c in j['user']['quests']['QuestRiftFuroma']['batteries'].values() if c['status'].split()[0] == 'unlocked')
    blf = j['user']['quests']['QuestRiftFuroma']['droid']['remaining_energy']
    enc = stats['combat_energy_stat_item'] if 'combat_energy_stat_item' in stats else 0
    lch = j['user']['quests']['QuestRiftFuroma']['view_state'] != 'trainingGrounds'
    target_bait,target_trinket,target_base = '','rift_furoma_energy_trinket' if 'rift_furoma_energy_trinket' in trinkets and 'c' in args.z else 'rift_vacuum_trinket' if 'rift_vacuum_trinket' in trinkets else '','furoma_rift_energy_upgraded_base' if 'furoma_rift_energy_upgraded_base' in bases else 'furoma_rift_energy_base' if 'furoma_rift_energy_base' in bases else best_base
        
    if not lch: 
        if enc >= bcp: 
            requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_furoma.php',{'uh':hash,'action':'charge_droid','charge_level':max((c for c in j['user']['quests']['QuestRiftFuroma']['batteries'] if j['user']['quests']['QuestRiftFuroma']['batteries'][c]['status'].split()[0] == 'unlocked'),key=lambda x:j['user']['quests']['QuestRiftFuroma']['batteries'][x]['total'])},cookies=cookies,headers=post_headers)
            blf,lch,bcl = bcp,True,bml
        else: 
            target_bait = 'brie_string_cheese'
            print('[%s] [%s] CHARGING: %s/%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),enc,bcp))
    
    if lch:
        onk = int(''.join([c for c in '0'+args.z if c.isdigit()]))
        tgw = min(['belt','claw','fang'],key=lambda x:crafts['rift_%s_shard_craft_item'%x] if 'rift_%s_shard_craft_item'%x in crafts else 0)
        tgc = {'belt':'rift_glutter_cheese','claw':'rift_susheese','fang':'rift_combat_cheese'}[tgw]
        
        if bcl == 10 and ('rift_onyx_cheese' in baits or ('rift_onyx_stone_craft_item' in crafts and crafts['rift_onyx_stone_craft_item'] > onk+3)):
            if 'rift_onyx_stone_craft_item' in crafts and crafts['rift_onyx_stone_craft_item'] > onk+3:
                n = (crafts['rift_onyx_stone_craft_item']-onk)//3
                if 'rift_cheese_curd_crafting_item' not in crafts or crafts['rift_cheese_curd_crafting_item'] < n*30: buy('rift_cheese_curd_crafting_item',n*30-(crafts['rift_cheese_curd_crafting_item'] if 'rift_cheese_curd_crafting_item' in crafts else 0))
                if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < n*12: buy('ionized_salt_craft_item',n*12-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
                craft({'rift_onyx_stone_craft_item':3,'rift_cheese_curd_crafting_item':30,'ionized_salt_craft_item':12},n)
                if 'rift_onyx_cheese' in baits: baits['rift_onyx_cheese'] += n*2
                else: baits['rift_onyx_cheese'] = n*2
            target_bait = 'rift_onyx_cheese'
            rep = 'target: sensei. branch: %s, onyx cheese: %s'%(crafts['rift_blossom_branch_crafting_item'] if 'rift_blossom_branch_crafting_item' in crafts else 0,baits['rift_onyx_cheese'])
            
        elif bcl >= 9 and ('rift_rumble_cheese' in baits or all('rift_%s_shard_craft_item'%c in crafts for c in ('fang','claw','belt'))):
            if all('rift_%s_shard_craft_item'%c in crafts for c in ('fang','claw','belt')):
                n = min(crafts['rift_%s_shard_craft_item'%c] for c in ('fang','claw','belt'))
                if 'rift_cheese_curd_crafting_item' not in crafts or crafts['rift_cheese_curd_crafting_item'] < n*2: buy('rift_cheese_curd_crafting_item',n*2-(crafts['rift_cheese_curd_crafting_item'] if 'rift_cheese_curd_crafting_item' in crafts else 0))
                if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < n*3: buy('ionized_salt_craft_item',n*3-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
                craft({'rift_belt_shard_craft_item':1,'rift_claw_shard_craft_item':1,'rift_fang_shard_craft_item':1,'rift_cheese_curd_crafting_item':2,'ionized_salt_craft_item':3},n)
                if 'rift_rumble_cheese' in baits: baits['rift_rumble_cheese'] += n*2
                else: baits['rift_rumble_cheese'] = n*2
            target_bait = 'rift_rumble_cheese'
            rep = 'target: GMOJO. onyx stone: %s, rumble cheese: %s'%(crafts['rift_onyx_stone_craft_item'] if 'rift_onyx_stone_craft_item' in crafts else 0,baits['rift_rumble_cheese'])     
        
        elif bcl >= 7 and ('rift_master_cheese' in baits or tgc in baits or ('rift_cheese_%s_token_crafting_item'%tgw in crafts and crafts['rift_cheese_%s_token_crafting_item'%tgw] >= 3)):
            if 'rift_cheese_%s_token_crafting_item'%tgw in crafts and crafts['rift_cheese_%s_token_crafting_item'%tgw] >= 3:
                n = crafts['rift_cheese_%s_token_crafting_item'%tgw]//3
                if 'rift_cheese_curd_crafting_item' not in crafts or crafts['rift_cheese_curd_crafting_item'] < n*2: buy('rift_cheese_curd_crafting_item',n*2-(crafts['rift_cheese_curd_crafting_item'] if 'rift_cheese_curd_crafting_item' in crafts else 0))
                craft({'rift_cheese_%s_token_crafting_item'%tgw:3,'rift_cheese_curd_crafting_item':2},n)
                if tgc in baits: baits[tgc] += n*2
                else: baits[tgc] = n*2
            if tgc in baits: target_bait = tgc
            else: target_bait = 'rift_master_cheese'
            rep = 'target: masters. %s. fusion: %s, %s: %s'%(', '.join('%s heirloom: %s'%(c,crafts['rift_%s_shard_craft_item'%c] if 'rift_%s_shard_craft_item'%c in crafts else 0) for c in ['belt','claw','fang']),baits['rift_master_cheese'] if 'rift_master_cheese' in baits else 0,tgc,baits[tgc] if tgc in baits else 0)
            
        elif bcl <= 3 and bml >= 4: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_furoma.php',{'uh':hash,'action':'leave_pagoda'},cookies=cookies,headers=post_headers)
        
        else: 
            target_bait = 'brie_string_cheese'
            rep = 'target: students. %s, fragments: %s'%(', '.join('%s token: %s'%(c,crafts['rift_cheese_%s_token_crafting_item'%c] if 'rift_cheese_%s_token_crafting_item'%c in crafts else 0) for c in ['belt','claw','fang']),crafts['rift_battery_piece_crafting_item'] if 'rift_battery_piece_crafting_item' in crafts else 0)
            
        if target_bait: print('[%s] [%s] LAUNCHED. batt: %s/%s (level %s). %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),blf,bcp,bcl,rep))
    
    if 'brie_string_cheese' not in baits or baits['brie_string_cheese'] <= 20: buy('brie_string_cheese',20)
    if current_weapon != best_weapons['Rift']: arm_weapon(best_weapons['Rift'])
    if target_bait:
        if current_base != target_base: arm_base(target_base)
        if current_bait != target_bait: arm_bait(target_bait)
        if current_trinket != target_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: frift(loop_counter+1)

def bwrift(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'Rift' not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if 'rift_bristle_woods' not in allowed_regions: return print('[%s] [%s] no access to BW rift. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'rift_bristle_woods':
        travel('rift_bristle_woods')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if current_weapon != best_weapons['Rift']: arm_weapon(best_weapons['Rift'])
    try: best_base = max([c for c in j['components'] if c['classification']=='base' and 'tag_types' in c and 'rift' in c['tag_types']],key=lambda x:x['power'] if 'power' in x else 0)['type']
    except: pass
    if current_base != best_base: arm_base(best_base)
    if 'brie_string_cheese' not in baits or baits['brie_string_cheese'] <= 100: buy('brie_string_cheese',100)
    if 'rift_vacuum_trinket' not in trinkets or trinkets['rift_vacuum_trinket'] <= 10: buy('rift_vacuum_trinket',100)
    
    ts = stats['rift_hourglass_sand_stat_item'] if 'rift_hourglass_sand_stat_item' in stats else 0
    qq = stats['rift_quantum_quartz_stat_item'] if 'rift_quantum_quartz_stat_item' in stats else 0
    rsc = baits['runic_string_cheese'] if 'runic_string_cheese' in baits else 0
    asc = baits['ancient_string_cheese'] if 'ancient_string_cheese' in baits else 0

    eff = [c for c in j['user']['quests']['QuestRiftBristleWoods']['status_effects'] if j['user']['quests']['QuestRiftBristleWoods']['status_effects'][c] == 'active']
    tsn = 110 - 20*(('ac' in eff) + ('ng' in eff))
    tsn -= min(qq*3//4,tsn*2//7)
    if 'st' in eff or 'un' in eff: tsn = 200
    
    if j['user']['quests']['QuestRiftBristleWoods']['chamber_status'] == 'closed': ct = j['user']['quests']['QuestRiftBristleWoods']['chamber_type']
    else:
        ca = [d['type'] for d in j['user']['quests']['QuestRiftBristleWoods']['portals'] if d['status'] == '']
        
        if 'ancient_string_cheese_potion' in potions:
            n = potions['ancient_string_cheese_potion']
            buy('brie_string_cheese',n)
            potion('ancient_string_cheese_potion',0,n)
            asc += n
        n = min(potions['runic_string_cheese_potion'] if 'runic_string_cheese_potion' in potions else 0,asc//2,(tsn-rsc)//2+1)
        if n > 0:
            potion('runic_string_cheese_potion',0,n)
            rsc += n*2
            asc -= n*2
                    
        if 'entrance_chamber' in ca: ct = 'basic_chamber'
        elif 'hidden_treasury' in ca: ct = 'hidden_treasury'
        elif 'lucky_chamber' in ca: ct = 'lucky_chamber'
        elif 'guard_chamber' in ca: ct = 'guard_chamber'
        elif 'silence_chamber' in ca: ct = 'silence_chamber'
        elif 'stalker_chamber' in ca: ct = 'stalker_chamber'
        elif 'icy_chamber' in ca: ct = 'icy_chamber'
        elif 'acolyte_chamber' in ca and min(ts,rsc) > tsn: ct = 'acolyte_chamber'        
        elif 'ingress_chamber' in ca: ct = 'ingress_chamber'
        elif 'icebreak_chamber' in ca: ct = 'icebreak_chamber'
        elif 'timewarp_chamber' in ca and rsc > 20 and (ts < tsn or rsc > tsn): ct = 'timewarp_chamber'
        elif 'potion_chamber' in ca: ct = 'potion_chamber'
        elif 'magic_chamber' in ca and asc > 20 and rsc < tsn: ct = 'magic_chamber'
        elif 'timewarp_chamber' in ca: ct = 'timewarp_chamber'
        elif 'magic_chamber' in ca: ct = 'magic_chamber'
        elif 'acolyte_chamber' in ca: ct = 'acolyte_chamber'
        elif 'basic_chamber' in ca: ct = 'basic_chamber'
        else: print(ca); quit()
        
        requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_bristle_woods.php',{'uh':hash,'action':'enter_portal','portal_type':ct},cookies=cookies,headers=post_headers)
        print('[%s] [%s] travelled to %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),ct.replace('_',' ')))
    
    if ct == 'acolyte_chamber': 
        if not ts or not rsc: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_bristle_woods.php',{'uh':hash,'action':'enter_portal'},cookies=cookies,headers=post_headers)
        target_bait, target_trinket, asd = 'runic_string_cheese', 'rift_vacuum_trinket', j['user']['quests']['QuestRiftBristleWoods']['acolyte_sand']
        uqq = j['user']['quests']['QuestRiftBristleWoods']['minigame']['acolyte_chamber']['obelisk_charge'] < 100
        if j['user']['quests']['QuestRiftBristleWoods']['minigame']['acolyte_chamber']['obelisk_charge'] < 100: 
            rep = 'CHARGING: %s, sand: %s - %s'%(j['user']['quests']['QuestRiftBristleWoods']['minigame']['acolyte_chamber']['obelisk_charge'],ts,asd)
        elif asd:  rep = 'DRAINING. sand: %s - %s'%(ts,asd)
        else: rep = 'RTC. sand: %s'%ts
    else: 
        target_trinket = 'rift_vacuum_trinket' if ct in ['icy_chamber','basic_chamber','magic_chamber','stalker_chamber','silence_chamber','guard_chamber','ingress_chamber','icebreak_chamber'] else None
        rep = 'fresh run' if j['user']['quests']['QuestRiftBristleWoods']['chamber_status'] == 'open' else 'loot: %s/%s. sand: %s/%s'%(j['user']['quests']['QuestRiftBristleWoods']['progress_remaining'],j['user']['quests']['QuestRiftBristleWoods']['progress_goal'],ts,tsn)
        
        if ct == 'magic_chamber': target_bait = 'ancient_string_cheese' if asc and rsc < tsn else 'brie_string_cheese'
        elif ct == 'timewarp_chamber': target_bait = 'runic_string_cheese' if rsc else 'brie_string_cheese'
        else: target_bait = 'brie_string_cheese'
                
        if ct in ['lucky_chamber','hidden_treasury']: uqq = j['user']['quests']['QuestRiftBristleWoods']['progress_remaining'] <= 7
        else: uqq = ct in ['lucky_chamber','hidden_treasury','guard_chamber','icy_chamber','ingress_chamber'] and 'q' in args.z
    
    uqq = uqq and 'rift_quantum_quartz_stat_item' in stats
    if uqq != (j['user']['quests']['QuestRiftBristleWoods']['items']['rift_quantum_quartz_stat_item']['status']=='selected'): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_bristle_woods.php',{'uh':hash,'action':'toggle_loot_boost'},cookies=cookies,headers=post_headers)
    
    print('[%s] [%s] room: %s. QQ: %s, %s left. %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),ct.replace('_',' '),'ON' if uqq else 'off',qq,rep))
    
    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
        if current_trinket != target_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        
def vrift():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'Rift' not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if 'rift_valour' not in allowed_regions: return print('[%s] [%s] no access to valour rift. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'rift_valour':
        travel('rift_valour')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if current_weapon != best_weapons['Rift']: arm_weapon(best_weapons['Rift'])
    best_base = 'valour_rift_prestige_base' if 'valour_rift_prestige_base' in bases else max([c for c in j['components'] if c['classification']=='base' and 'tag_types' in c and 'rift' in c['tag_types']],key=lambda x:x['power'] if 'power' in x else 0)['type']
    if current_base != best_base: arm_base(best_base)
    
    if j['user']['quests']['QuestRiftValour']['state']=='farming': 
        target_bait = 'brie_string_cheese'
        if current_trinket != 'rift_vacuum_trinket' and 'rift_vacuum_trinket' in trinkets: arm_charm('rift_vacuum_trinket')
        print('[%s] [%s] farming. gauntlet potions: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),stats['gauntlet_elixir_stat_item'] if 'gauntlet_elixir_stat_item' in stats else 0))
    else:
        def gs(n): return 20+((n-1)//8)*10 if n%8 else 1
        def gf(n): 
            i,s = 1,0
            while s <= n: s+=gs(i);i+=1
            return i-1,s
        def vsim(st,sp,si,n,hl,bm,cf,uu=False):
            r = 0
            for i in range(n):
                s,h = st,hl
                while h:
                    g,h = gf(s),h-1
                    if g[0]%8: 
                        cr = (.78 if g[0] < 8 else .66 if g[0] < 16 else .61 if g[0] < 24 else .55) if uu else (.92 if g[0] < 8 else .75 if g[0] < 16 else .7 if g[0] < 24 else .63)
                        bfr = (.078 if g[0] < 8 else .1165 if g[0] < 16 else .1209 if g[0] < 24 else .1245) if uu else 0
                        tar = (.1826 if g[0] < 8 else .1103 if g[0] < 16 else .1002 if g[0] < 24 else .0818) if uu else (.2253 if g[0] < 8 else .1352 if g[0] < 16 else .1246 if g[0] < 24 else .106)
                        ad = 2*sp+cf if random.random() < tar else -10 if random.random() < bfr else sp+cf if random.random() < cr else 0
                    else: ad = sp+1; h += si
                    if ad: 
                        if gf(s+ad)[0]//8 > gf(s)[0]//8: s = sum(gs(j) for j in range(1,gf(s+ad)[0]//8*8))
                        elif gf(s+ad)[0] < gf(s)[0]: s = sum(gs(j) for j in range(1,gf(s)[0]))
                        else: s += ad
                if gf(s)[0] > bm: r+=1
            return round(r/n*100,2)
        sp,cf,cs = j['user']['quests']['QuestRiftValour']['power_up_data']['long_stride']['current_value'],j['user']['quests']['QuestRiftValour']['floor'],j['user']['quests']['QuestRiftValour']['current_step']
        nf,ne = sum(gs(i) for i in range(cf+1))-1,sum(gs(i) for i in range(cf+(-cf%8)))-1
        fo = j['user']['quests']['QuestRiftValour']['is_at_eclipse'] or ('f' in args.z and (ne-cs-1)%sp<(ne-cs-1)//sp)
        
        target_bait = 'brie_string_cheese' if j['user']['quests']['QuestRiftValour']['is_at_eclipse'] or ne-cs<=sp+fo else 'gauntlet_string_cheese'    
        if fo != j['user']['quests']['QuestRiftValour']['is_fuel_enabled']: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/rift_valour.php',{'uh':hash,'action':'toggle_fuel'},cookies=cookies,headers=post_headers)
        bm = ''.join(c for c in args.z if c in '0987654321')
        print('[%s] [%s] floor: %s. step: %s/%s (%s to lvl, %s to ecl%s). hunts left: %s. bait: %s, cf: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),cf,cs,nf,nf-cs,ne-cs,', %s%% of passing'%vsim(cs,6,20,1000,int(j['user']['quests']['QuestRiftValour']['hunts_remaining']),int(bm) if bm else cf+(-cf%8)+1,'f' in args.z,j['user']['quests']['QuestRiftValour']['is_eclipse_mode']) if 's' in args.z else '',j['user']['quests']['QuestRiftValour']['hunts_remaining'],target_bait.replace('_string_cheese',''),'ON' if fo else 'off'))
    
    if current_bait != target_bait: arm_bait(target_bait)
        
def queso(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'queso_river' not in allowed_regions: return print('[%s] [%s] no access to queso canyon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Law','Arcane','Shadow']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    
    if not args.z or args.z[-1] != '!':
        if all(c not in args.z for c in 'kqp') and 'queso_geyser' in allowed_regions and 'Draconic' in best_weapons:
            if current_location != 'queso_geyser':
                travel('queso_geyser')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            args.z = [args.z,j['user']['quests']['QuestQuesoGeyser']['state'],j['user']['quests']['QuestQuesoGeyser']['state_name'][0].lower() if j['user']['quests']['QuestQuesoGeyser']['state_name'] else '','!']
            if j['user']['quests']['QuestQuesoGeyser']['state'] == 'claim': 
                requests.post('https://www.mousehuntgame.com/managers/ajax/environment/queso_geyser.php',{'uh':hash,'action':'claim'},cookies=cookies,headers=post_headers) 
                args.z[1] = 'collecting'
        else: args.z = [args.z,'!']
    
    if len(args.z) == 2 and current_location not in ['queso_river','queso_plains','queso_quarry']:
        travel('queso_river')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_location in ['queso_river','queso_plains','queso_quarry']:
        pump_level,nachores,pc = j['user']['quests']['QuestQuesoCanyon']['pump_level'],stats['nachore_stat_item'] if 'nachore_stat_item' in stats else 0,j['user']['quests']['QuestQuesoCanyon']['next_pump_cost']
        if 'u' in args.z[0] and pump_level < 10 and nachores >= pc: 
            pump_level += 1
            nachores -= j['user']['quests']['QuestQuesoCanyon']['next_pump_cost']
            j['user']['quests']['QuestQuesoCanyon']['next_pump_cost'] = j['user']['quests']['QuestQuesoCanyon']['pump_costs'][str(pump_level+1)] if pump_level < 10 else 0
            requests.post('https://www.mousehuntgame.com/managers/ajax/environment/queso_canyon.php',{'uh':hash,'action':'upgrade_pump'},cookies=cookies,headers=post_headers) 
    if len(args.z) == 4:
        if current_location == 'queso_geyser': args.z[1],args.z[2] = j['user']['quests']['QuestQuesoGeyser']['state'],j['user']['quests']['QuestQuesoGeyser']['state_name'][0].lower() if j['user']['quests']['QuestQuesoGeyser']['state_name'] else ''
        if args.z[1] == 'collecting':
            if 'tungsten_crafting_item' in crafts and crafts['tungsten_crafting_item'] >= 60 and 'cork_bark_crafting_item' in crafts and crafts['cork_bark_crafting_item'] >= 180: args.z[1],args.z[2] = 'corked','e'
            elif 'tungsten_crafting_item' in crafts and crafts['tungsten_crafting_item'] >= 60: pass
            elif 'geyserite_crafting_item' in crafts and crafts['geyserite_crafting_item'] >= 30 and 'cork_bark_crafting_item' in crafts and crafts['cork_bark_crafting_item'] >= 90: args.z[1],args.z[2] = 'corked','b'
            elif 'geyserite_crafting_item' in crafts and crafts['geyserite_crafting_item'] >= 30: pass
            elif 'rubber_crafting_item' in crafts and crafts['rubber_crafting_item'] >= 15 and 'cork_bark_crafting_item' in crafts and crafts['cork_bark_crafting_item'] >= 30: args.z[1],args.z[2] = 'corked','m'
            elif 'rubber_crafting_item' in crafts and crafts['rubber_crafting_item'] >= 15: pass
            elif 'cork_bark_crafting_item' in crafts and crafts['cork_bark_crafting_item'] >= 10: args.z[1],args.z[2] = 'corked','s'           
            if args.z[1] == 'corked': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/queso_geyser.php',{'uh':hash,'action':'build_cork','cork':'cork_basic' if args.z[2] == 's' else 'cork_improved' if args.z[2] == 'm' else 'cork_heavy' if args.z[2] == 'b' else 'cork_sticky'},cookies=cookies,headers=post_headers)
            
    target_weapon,target_trinket = '',''
    
    if not all(c not in args.z[0] for c in 'bmehf'): t = [c for c in 'bmehf' if c in args.z[0]][-1]
    elif len(args.z) == 2: t = 'f' if pump_level >= 9 else 'h' if pump_level >= 6 else 'e' if pump_level >= 3 else 'm' if pump_level >= 2 else 'b'
    elif args.z[1] == 'collecting': t = 'm'
    elif args.z[1] == 'corked': t = 'm' if args.z[2] == 's' else 'e' if args.z[2] == 'm' else 'h'
    else: t = 'm' if args.z[2] in ['t','s'] else 'e' if args.z[2] == 'm' else 'h'
    d = {'b':('bland',1,'m'),'m':('mild',10,'e'),'e':('medium',100,'h'),'h':('hot',1000,'f'),'f':('flaming',10000,'f')}
    tq = d[t][0]+'_queso_cheese'
        
    if tq in baits and 'k' not in args.z[0]:
        if len(args.z) == 4:
            target_location,target_weapon,target_bait = 'queso_geyser',best_weapons['Draconic'],tq
            target_trinket = 'festive_ultimate_luck_power_trinket' if t == 'f' else 'festive_ultimate_luck_power_trinket' if t == 'h' else 'festive_ultimate_luck_trinket' if t == 'e' else None
            if current_location != 'queso_geyser':
                travel('queso_geyser')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
                args.z[1] = j['user']['quests']['QuestQuesoGeyser']['state']
            if args.z[1] == 'corked': rep = '%s. pressure: %s/%s (%s hunts remaining)'%(j['user']['quests']['QuestQuesoGeyser']['state_name'].upper(),j['user']['quests']['QuestQuesoGeyser']['pressure'],j['user']['quests']['QuestQuesoGeyser']['max_pressure'],j['user']['quests']['QuestQuesoGeyser']['hunts_remaining']) if 'max_pressure' in j['user']['quests']['QuestQuesoGeyser'] else 'built %s cork'%args.z[2]
            elif args.z[1] == 'eruption': rep = '%s. eggs: %s (%s hunts remaining)'%(j['user']['quests']['QuestQuesoGeyser']['state_name'].upper(),j['user']['quests']['QuestQuesoGeyser']['nest_loot'],j['user']['quests']['QuestQuesoGeyser']['hunts_remaining'])
            else: rep = 'COLLECTING. cork bark: %s'%(crafts['cork_bark_crafting_item'] if 'cork_bark_crafting_item' in crafts else 0)
            print('[%s] [%s] using %s at geyser. %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),d[t][0],rep))
        elif 'p' in args.z[0]:
            target_location,target_weapon,target_bait = 'queso_plains',best_weapons['Arcane'],tq
            print('[%s] [%s] using %s at plains. bait left: %s, %s leaves: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),d[t][0],baits[target_bait],d[d[t][2]][0],crafts[d[d[t][2]][0]+'_spice_crafting_item'] if d[d[t][2]][0]+'_spice_crafting_item' in crafts else 0))
        else: 
            target_location,target_weapon,target_bait = 'queso_quarry',best_weapons['Shadow'],tq
            print('[%s] [%s] using %s at quarry. nachores: %s/%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),d[t][0],nachores,pc))
    else: 
        for q in 'bmehfw'[:'bmehfw'.index(t)+1][::-1]:
            rep = '' if len(args.z) == 2 else '. geyser state: %s%s'%('' if args.z[1] == 'collecting' else args.z[2]+' ',args.z[1])
            if q != t and d[q][0]+'_queso_cheese' in baits: 
                target_location,target_weapon,target_bait = 'queso_plains',best_weapons['Arcane'],d[q][0]+'_queso_cheese'
                print('[%s] [%s] using %s at plains. bait left: %s, %s leaves: %s%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),d[q][0],baits[target_bait],d[d[q][2]][0],crafts[d[d[q][2]][0]+'_spice_crafting_item'] if d[d[q][2]][0]+'_spice_crafting_item' in crafts else 0,rep))
            elif d[q][0]+'_spice_crafting_item' in crafts and crafts[d[q][0]+'_spice_crafting_item'] >= 10 and 'bland_queso_cheese' in baits and baits['bland_queso_cheese'] >= d[q][1]:
                n = min(crafts[d[q][0]+'_spice_crafting_item']//10,baits['bland_queso_cheese']//d[q][1])
                craft({d[q][0]+'_spice_crafting_item':10,'bland_queso_cheese':d[q][1]},n)
            elif q == 'b' or (d[q][0]+'_spice_crafting_item' in crafts and crafts[d[q][0]+'_spice_crafting_item'] >= 10): 
                best_base,target_location,target_weapon,target_bait = 'queso_canyon_base','queso_river',best_weapons['Law'],'gouda_cheese'
                print('[%s] [%s] pumping bland queso: %s/%s%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['bland_queso_cheese'] if 'bland_queso_cheese' in baits else 0,d[q][1],rep))
            else: continue
            break
    
    best_base = 'queso_cannonstorm_base' if 'queso_cannonstorm_base' in bases else 'queso_canyon_base' if 'queso_canyon_base' in bases else best_base
    if current_base != best_base: arm_base(best_base)
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 100: buy('gouda_cheese',100)
    
    if target_weapon:
        if current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_bait != target_bait: arm_bait(target_bait)
        if current_location != target_location: travel(target_location)
        if current_trinket != target_trinket : arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: queso(loop_counter+1)

def mp():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'moussu_picchu' not in allowed_regions: return print('[%s] [%s] no access to moussu picchu. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Draconic','Arcane','Shadow']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if current_location != 'moussu_picchu': 
        travel('moussu_picchu')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    rl = j['user']['quests']['QuestMoussuPicchu']['elements']['rain']['percent']
    wl = j['user']['quests']['QuestMoussuPicchu']['elements']['wind']['percent']
    rp = potions['rain_cheese_potion'] if 'rain_cheese_potion' in potions else 0
    wp = potions['wind_cheese_potion'] if 'wind_cheese_potion' in potions else 0
    rc = baits['rain_cheese'] if 'rain_cheese' in baits else 0
    wc = baits['wind_cheese'] if 'wind_cheese' in baits else 0
    dc = baits['dragonvine_cheese'] if 'dragonvine_cheese' in baits else 0
    av = crafts['arcanevine_crafting_item'] if 'arcanevine_crafting_item' in crafts else 0
    sv = crafts['shadowvine_crafting_item'] if 'shadowvine_crafting_item' in crafts else 0
    
    target_trinket = ''
    best_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['luck'] if 'luck' in x else 0)['type']
    ms = [c for c in args.z if c in 'wrd']
    for m in ms:
        if m == 'w' and (wc or wp): 
            if wp:
                buy('gouda_cheese',wp*2)
                potion('wind_cheese_potion',0,wp)
                wp,wc = 0,wc+wp
            phase, target_weapon, target_bait = 'wind', best_weapons['Arcane'], 'wind_cheese'
        elif m == 'r' and (rc or rp): 
            if rp:
                buy('gouda_cheese',rp*2)
                potion('rain_cheese_potion',0,rp)
                rp,rc = 0,rc+rp
            phase, target_weapon, target_bait = 'rain', best_weapons['Shadow'], 'rain_cheese'
        elif m == 'd' and (dc or (av > 5 and sv > 5)): 
            if av > 5 and sv > 5:
                n = min(av//6,sv//6)
                if 's' in args.z: n = min(n,((baits['super_brie_cheese'] if 'super_brie_cheese' in baits else 0)+(crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts else 0))//2)
                if (crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0) < 25*n: buy('curds_and_whey_craft_item',25*n-(crafts['curds_and_whey_craft_item'] if 'curds_and_whey_craft_item' in crafts else 0))
                if (crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0) < 10*n: buy('ionized_salt_craft_item',10*n-(crafts['ionized_salt_craft_item'] if 'ionized_salt_craft_item' in crafts else 0))
                d = {'arcanevine_crafting_item':6,'shadowvine_crafting_item':6,'curds_and_whey_craft_item':25,'ionized_salt_craft_item':10}
                if 's' in args.z:
                    if (crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts else 0) < n*2: hammer('super_brie_cheese',n*2-(crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts else 0))
                    d['magic_essence_craft_item'] = 2
                craft(d,n)
                av,sv,dc = 0,0,dc+n*(5 if 's' in args.z else 3)
            if 'f' in args.z and j['user']['quests']['QuestMoussuPicchu']['is_torch_active'] != min(wl,rl) < 100: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/moussu_picchu.php',{'sn':'Hitgrab','hg_is_ajax':1,'action':'toggle_torch','uh':hash},cookies=cookies,headers=post_headers)
            best_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['power'] if 'power' in x else 0)['type']
            phase, target_weapon, target_bait = 'storm', best_weapons['Draconic'], 'dragonvine_cheese'
        else: continue
        print('[%s] [%s] phase: %s. wind/rain lvl: %s/%s. avine/dvine/svine: %s/%s/%s. %s %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),phase.upper(),wl,rl,av,dc,sv,baits[target_bait] if target_bait in baits else 0,target_bait.replace('_',' ')))
        break
    else: 
        target_weapon, target_trinket, target_bait = best_weapons['Arcane'], 'd', 'glowing_gruyere_cheese' if 'glowing_gruyere_cheese' in baits and 'g' in args.z else 'gouda_cheese'
        print('[%s] [%s] phase: BASIC. wind pot: %s, wind bait: %s, rain bait: %s, rain pot: %s. %s %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),wp,wc,rc,rp,baits[target_bait] if target_bait in baits else 0,target_bait.replace('_',' ')))
    
    if current_base != best_base: arm_base(best_base)
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 100: buy('gouda_cheese',100)
    if current_bait != target_bait: arm_bait(target_bait)
    if target_trinket and current_trinket != target_trinket : arm_charm(target_trinket if target_trinket != 'd' else 'disarm')
    
def bb():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'bountiful_beanstalk' not in allowed_regions: return print('[%s] [%s] no access to bountiful beanstalk. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Physical' not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    if current_location != 'bountiful_beanstalk': 
        travel('bountiful_beanstalk')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if current_base != best_base: arm_base(best_base)
    if current_weapon != best_weapons['Physical']: arm_weapon(best_weapons['Physical'])
    target_bait = 'gouda_cheese'
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 100: buy('gouda_cheese',100)
    
    if not j['user']['quests']['QuestBountifulBeanstalk']['in_castle'] and 'g' not in args.z:
        ff = stats['fabled_fertilizer_stat_item'] if 'fabled_fertilizer_stat_item' in stats else 0
        if ff:
            requests.post('https://www.mousehuntgame.com/managers/ajax/environment/bountiful_beanstalk.php',{'sn':'Hitgrab','hg_is_ajax':'1','action':'plant_vine','type':'medium_vine' if ff >= 12 and 'l' not in args.z else 'short_vine','bait_disarm_preference':'standardBait','uh':hash},cookies=cookies,headers=post_headers)
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if j['user']['quests']['QuestBountifulBeanstalk']['in_castle']:
        rm = j['user']['quests']['QuestBountifulBeanstalk']['castle']['current_room']['loot_multiplier']
        rt = j['user']['quests']['QuestBountifulBeanstalk']['castle']['current_room']['type'].replace('_room','').replace('_',' ')
        hr = j['user']['quests']['QuestBountifulBeanstalk']['castle']['hunts_remaining']
        if j['user']['quests']['QuestBountifulBeanstalk']['castle']['is_boss_chase']: 
            rm *= 2
            if 'egg' in rt: target_bait = 'royal_beanster_cheese'
            elif rm >= 8: target_bait = 'beanster_cheese'
            print('[%s] [%s] room: %s. boss chase: %s hunts left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),rt,hr))
        else: 
            r1r = False
            if 'r' in args.z and 'egg' not in rt:
                if 'leaping_lavish_beanster_cheese' in baits and baits['leaping_lavish_beanster_cheese'] >= hr//5: r1r = True
                else: print('[%s] [%s] not enough leaping for r1r'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
            if r1r:
                target_bait = 'leaping_lavish_beanster_cheese'
                cn,mn,st,rp = j['user']['quests']['QuestBountifulBeanstalk']['castle']['noise_level'], j['user']['quests']['QuestBountifulBeanstalk']['castle']['max_noise_level'], j['user']['quests']['QuestBountifulBeanstalk']['castle']['current_room']['loot_multiplier']*4,j['user']['quests']['QuestBountifulBeanstalk']['castle']['room_position']
                if mn-cn-(21-rp)//5*st > 0: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/bountiful_beanstalk.php',{'sn':'Hitgrab','hg_is_ajax':'1','action':'use_harp_strings','quantity':str(mn-cn-(21-rp)//5*st),'increase_noise':'true','uh':hash},cookies=cookies,headers=post_headers);cn+=mn-cn-(21-rp)//5*st
                print('[%s] [%s] room: %s, step %s. noise: %s/%s (+%s)'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),rt,rp,cn,mn,st))
            else:
                if 'egg' in rt: target_bait = 'royal_beanster_cheese' if rm == 8 else 'leaping_lavish_beanster_cheese'
                elif rm >= 8: target_bait = 'beanster_cheese'
                print('[%s] [%s] room: %s, %s hunts left. noise: %s/%s (+%s-%s). next: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),rt,hr,j['user']['quests']['QuestBountifulBeanstalk']['castle']['noise_level'],j['user']['quests']['QuestBountifulBeanstalk']['castle']['max_noise_level'],j['user']['quests']['QuestBountifulBeanstalk']['castle']['projected_noise']['actual_min'],j['user']['quests']['QuestBountifulBeanstalk']['castle']['projected_noise']['actual_max'],j['user']['quests']['QuestBountifulBeanstalk']['castle']['next_room']['type']))
            
    else: print('[%s] [%s] vine. loot x%s, %s hunts left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestBountifulBeanstalk']['beanstalk']['current_zone']['loot_multiplier'],j['user']['quests']['QuestBountifulBeanstalk']['beanstalk']['hunts_remaining']))
        
    if target_bait not in baits: target_bait = 'gouda_cheese'
    if current_bait != target_bait: arm_bait(target_bait)
     
def halloween(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        
    if 'halloween_event_location' not in allowed_regions: return print('[%s] [%s] no access to halloween location. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'alchemists_cookbook_base' in bases: best_base = 'alchemists_cookbook_base'
    target_weapon = 'boiling_cauldron_weapon' if 'boiling_cauldron_weapon' in weapons else best_weapon
    target_bait,target_trinket = '',''
    if current_location != 'halloween_event_location':
        travel('halloween_event_location')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    r = j['user']['quests']['QuestHalloweenBoilingCauldron']
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 15: buy('brie_cheese',15)
    
    cauldron_0_queue_len = len([c for c in r['cauldrons'][0]['queue'] if c['type']])
    cauldron_0_time = r['cauldrons'][0]['brew_time'] if r['cauldrons'][0]['brew_time'] else 0
    cauldron_1_queue_len = len([c for c in r['cauldrons'][1]['queue'] if c['type']])
    cauldron_1_time = r['cauldrons'][1]['brew_time'] if r['cauldrons'][1]['brew_time'] else 0
    caldron_priority = sorted([(0,cauldron_0_time!=0,cauldron_0_queue_len,cauldron_0_time),(1,cauldron_1_time!=0,cauldron_1_queue_len,cauldron_1_time)],key=lambda x:(x[1],x[2],x[3],x[0]))
    event_items = {k:r['items'][k]['quantity'] for k in r['items'] if 'cauldron_tier_' in k}
    brewable = ['cauldron_tier_%s_recipe'%i for i in range(1,5) for _ in range(event_items['cauldron_tier_%s_ingredient_stat_item'%i]//15)]
    num_root = r['items']['cauldron_potion_ingredient_stat_item']['quantity']
    if num_root >= 15 and 'r' not in args.z: 
        for _ in range(num_root//15): brewable = ['halloween_extract_cauldron_recipe'] + brewable
    
    for i in range(2):
        if caldron_priority[i][2] <= 1 and brewable: requests.post('https://www.mousehuntgame.com/managers/ajax/events/halloween_boiling_cauldron.php',{'uh':hash,'action':'brew_recipe','slot':caldron_priority[i][0],'recipe_type':brewable.pop()},cookies=cookies,headers=post_headers)
    
    if r['reward_track']['can_claim']:
        d = {'uh':hash,'action':'claim_reward'}
        requests.post('https://www.mousehuntgame.com/managers/ajax/events/halloween_boiling_cauldron.php',d,cookies=cookies,headers=post_headers)
    
    event_trinkets = ['spooky_trinket','extra_spooky_trinket','extreme_spooky_trinket','ultimate_spooky_trinket']
    event_trinkets = [c for c in event_trinkets if c in trinkets]
    for i in range(4,0,-1):
        if event_items['cauldron_tier_%s_cheese'%i]:
            if i == 2 and 'b' in args.z: continue
            target_bait,target_base = 'cauldron_tier_%s_cheese'%i,best_base
            if i == 3 and event_trinkets: target_trinket = event_trinkets[0]
            elif i == 4 and event_trinkets: target_trinket = event_trinkets[-1]
            else: target_trinket = ''
            break
    else: target_bait,target_base,target_trinket = 'brie_cheese',best_base,''
    
    if target_bait:
        if target_base and current_base != target_base: arm_base(target_base)
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        level = 1 if target_bait == 'brie_cheese' else int(target_bait.split('_')[2])+1
        print('[%s] [%s] %s x level %s bait left%s. roots: %s. %s%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits[target_bait],level-1,'; obtained %s x tier %s ingredient'%(event_items['cauldron_tier_%s_ingredient_stat_item'%level],level) if level <= 4 else '',num_root,'cauldron 0: time %s, queue %s. '%(cauldron_0_time,cauldron_0_queue_len) if cauldron_0_time else '','cauldron 1: time %s, queue %s. '%(cauldron_1_time,cauldron_1_queue_len) if cauldron_1_time else ''))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: halloween(loop_counter+1)
    
def lny():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'QuestLunarNewYearLantern' not in j['user']['quests']: return print('[%s] [%s] lny event not on. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    wc = stats['lny_unlit_lantern_stat_item'] if 'lny_unlit_lantern_stat_item' in stats else 0
    rc = stats['lny_unlit_lantern_2018_stat_item'] if 'lny_unlit_lantern_2018_stat_item' in stats else 0
    wd = baits['lunar_new_year_2017_cheese'] if 'lunar_new_year_2017_cheese' in baits else 0
    rd = baits['lunar_new_year_2018_cheese'] if 'lunar_new_year_2018_cheese' in baits else 0
    
    if rd or wd:
        target_bait = 'lunar_new_year_2018_cheese' if rd else 'lunar_new_year_2017_cheese'
        print('[%s] [%s] GETTING CANDLES. white: %s, red: %s. dumpling: %s, ngd: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),wc,rc,wd,rd))
    else: 
        target_bait = 'gouda_cheese'
        if target_bait not in baits or baits[target_bait] < 100: buy(target_bait,100) 
        print('[%s] [%s] GETTING DUMPLINGS. white: %s, red: %s. dumpling: %s, ngd: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),wc,rc,wd,rd))
    
    if current_bait != target_bait: arm_bait(target_bait)
      
def bday(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'super_brie_factory' not in allowed_regions: return print('[%s] [%s] no access to birthday location. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'super_brie_factory':
        travel('super_brie_factory')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if j['user']['quests']['QuestSuperBrieFactory']['factory_atts']['can_claim']: c=0; requests.post('https://www.mousehuntgame.com/managers/ajax/events/birthday_factory.php',{'action':'claim_reward','uh':hash},cookies=cookies,headers=post_headers)    
    r,c,f,h = j['user']['quests']['QuestSuperBrieFactory']['factory_atts']['current_room'],j['user']['quests']['QuestSuperBrieFactory']['factory_atts']['current_progress'],j['user']['quests']['QuestSuperBrieFactory']['factory_atts']['max_pipe_progress'],j['user']['quests']['QuestSuperBrieFactory']['factory_atts']['hunts_remaining']
    
    if 't' in args.z and 'QuestRelicHunter' in j['user']['quests'] and 'maps' in j['user']['quests']['QuestRelicHunter'] and [m for m in j['user']['quests']['QuestRelicHunter']['maps'] if m['map_class']=='event']:
        mid = [m for m in j['user']['quests']['QuestRelicHunter']['maps'] if m['map_class']=='event'][0]['map_id']
        mts = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/treasuremap.php',{'action':'map_info','uh':hash,'map_id':mid},cookies=cookies,headers=post_headers).text)['treasure_map']
        mts = [m['type'] for m in mts['goals']['mouse'] if m['unique_id'] not in [m for p in mts['hunters'] for m in p['completed_goal_ids']['mouse']]]
        if mts:
            d = {'p':['time_punk','time_tailor','time_thief','reality_restitch','time_plumber'],'m':['force_fighter_green','force_fighter_red','force_fighter_pink','force_fighter_blue','force_fighter_yellow','super_fighterbot_megasupreme'],'b':['para_para_dancer','breakdancer','dance_boss','dance_party','fromager_mouse'],'q':['cupcake_camo','cupcake_candle_thief','cupcake_runner','cupcake_cutie','sprinkley_sweet']}
            if not h and 'vincent_the_magnificent' in mts: cts = ['vincent_the_magnificent']
            elif not h: cts = []
            else:
                for b in args.z+'pmbq':
                    if b not in d: continue
                    cts = [m for m in d[b] if m in mts]
                    if cts: args.z = ''.join(c for c in args.z if c not in 'pmbq')+b; break
                else:
                    args.z = ''.join(c for c in args.z if c not in 'pmbq')+('h' if 'cheesy_party' in mts else 'g')
                    cts = mts
                if 'factory_technician' in mts and 'c' in args.z and 'factory_technician' not in cts: cts.append('factory_technician')
        
            print('[%s] [%s] MAP. targets: %s. rest: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),cts,[m for m in mts if m not in cts]))
    
    for b in ['pumping_room','break_room','mixing_room','quality_assurance_room']:
        if b[0] in args.z: 
            if b == r: break
            else: r = b; requests.post('https://www.mousehuntgame.com/managers/ajax/events/birthday_factory.php',{'action':'pick_room','uh':hash,'room':r},cookies=cookies,headers=post_headers)
    
    if current_weapon != best_weapon: arm_weapon(best_weapon)
    if 'seasonal_gift_of_the_day_base' in bases: best_base = 'seasonal_gift_of_the_day_base'
    if current_base != best_base: arm_base(best_base)    

    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 15: buy('gouda_cheese',15)
    
    if 'g' in args.z or not h: target_bait = 'gouda_cheese'
    elif 'h' in args.z: target_bait = 'super_brie_cheese'
    elif 'speed_coggy_colby_cheese' in baits and 's' in args.z: target_bait = 'speed_coggy_colby_cheese'
    elif 'coggy_colby_cheese' in baits: target_bait = 'coggy_colby_cheese'
    else: target_bait = 'gouda_cheese'
    if current_bait != target_bait: arm_bait(target_bait)    

    target_trinket = ''
    if 'c' in args.z and 'birthday_factory_trinket' in trinkets and target_bait in ['gouda_cheese','super_brie_cheese'] and h: target_trinket = 'birthday_factory_trinket'
    if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        
    print('[%s] [%s] pump: %s/%s (%s). BAITS: %s. %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),c,f,'%s hunts left'%h if h else 'vincent',', '.join('%s%s: %s'%(b[0],'*' if target_bait == b else '',baits[b] if b in baits else 0) for b in ['coggy_colby_cheese','speed_coggy_colby_cheese']),'STATS: %s'%', '.join('%s%s: %s'%(c.replace('birthday_factory_','')[0],'*' if c.replace('birthday_factory_','')[0] == r[0] else '',stats[c] if c in stats else 0) for c in ['birthday_factory_break_room_stat_item','birthday_factory_mixing_room_stat_item','birthday_factory_pumping_room_stat_item','birthday_factory_quality_assurance_room_stat_item'])))
    
##### HORN #####
def status_check():
    global hash,allowed_regions,antibot_triggered,lpt,user_id,lrje
    if antibot_triggered or args.a:
        d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.170.0','login_token':cookie}
        r = requests.post('https://www.mousehuntgame.com/api/action/passiveturn',d,headers=api_headers)
        if r.status_code != 200:
            print('[%s] session expired. logging in again'%(datetime.datetime.now().replace(microsecond=0)))
            login()
            d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.170.0','login_token':cookie}
            r = requests.post('https://www.mousehuntgame.com/api/action/passiveturn',d,headers=api_headers)
        j = json.loads(r.text)
        hash,user_id,lpt,next_horn,have_bait,s = j['user']['uh'],j['user']['user_id'],j['user']['last_passiveturn_timestamp'],j['user']['next_activeturn_seconds'],j['user']['trap']['bait_id'],time.time()
    else:
        try: 
            assert hash and lrje
            j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'sn':'Hitgrab','hg_is_ajax':1,'page_class':'Camp','last_read_journal_entry_id':lrje,'uh':hash},cookies=cookies,headers=post_headers).text)
            hash,user_id,next_horn,have_bait,antibot_triggered,s = j['user']['unique_hash'],j['user']['user_id'],j['user']['next_activeturn_seconds'],j['user']['bait_item_id'],int(time.time()*1000) if j['user']['has_puzzle'] else 0,time.time()
        except: 
            r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers)
            if r.url == 'https://www.mousehuntgame.com/login.php':
                print('[%s] session expired. logging in again'%(datetime.datetime.now().replace(microsecond=0)))
                hash = ''
                login()
                r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers)
            r = r.text
            hash,user_id,lrje,next_horn,have_bait,s = re.findall(r'"unique_hash":"([^"]*)"',r)[0],re.findall(r'"user_id":([^,]*)',r)[0],int(re.findall(r'lastReadJournalEntryId = ([^;]*);',r)[0]),int(re.findall(r'"next_activeturn_seconds":(\d*)',r)[0]),'"bait_quantity":0' not in r,time.time()
            if '"has_puzzle":true' in r: antibot_triggered = int(time.time()*1000)
        if antibot_triggered:
            print('[%s] antibot triggered'%(datetime.datetime.now().replace(microsecond=0)))
            if not antibot_mode == 'bypass': antibot(); antibot_triggered = 0
            else: return status_check()
    if not horns and cycle: allowed_regions = regions()
    if not have_bait and not cycle: change_bait()
    return max(0,next_horn-time.time()+s)

def wait(delay_mins,norandom=False):
    next_wait = delay_mins*60 + random.random()*randomness
    if norandom: next_wait = delay_mins*60
    m,s,ms = int(next_wait//60),int(next_wait%60),int((next_wait*1000)%1000)
    n = ('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(minutes=m,seconds=s))).split(' ')[1]
    print('[%s] next horn in %s mins %s secs at %s'%(datetime.datetime.now().replace(microsecond=0),m,s,n))
    time.sleep(next_wait)
    
def print_entry(t):
    try: 
        for m in re.findall(r'<[^>]*>',t): t = t.replace(m,'')
        for m in re.findall(r'&\w{4};',t): t = t.replace(m,' ')
        s = t.index('!',20) if '!' in t[20:-2] else t.index('.',(t.index('oz.')+3) if 'oz.' in t else 0)
        if t[:s+1]: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t[:s+1].lstrip()))
        if t[s+1:]: print_entry(t[s+1:])
    except: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t.lstrip()))    

def horn():
    global lpt,lrje,hash,user_id,antibot_triggered
    fail,atr = 0,antibot_triggered
    try: assert lpt
    except: lpt = int(time.time()) - 15*60
    while 1:
        if not args.a: 
            wait_time = status_check()
            while wait_time: 
                print('[%s] horn not ready'%(datetime.datetime.now().replace(microsecond=0)))
                wait(float((wait_time+2)/60),norandom=True)
                wait_time = status_check()
            horn_time = int(time.time())
            if cycle: choose_cycle()
        latency_start = time.time()
        wait_time = 0
        try:
            if antibot_triggered or args.a:
                d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.170.0','last_passiveturn_timestamp':lpt,'login_token':cookie}
                r = requests.post('https://www.mousehuntgame.com/api/action/turn/me',d,headers=api_headers).text
                print(r);quit()
                j = json.loads(requests.post('https://www.mousehuntgame.com/api/action/turn/me',d,headers=api_headers).text)
                hash,user_id,success,wait_time,lpt,gold,have_bait = j['user']['uh'],j['user']['user_id'],j['success'],j['user']['next_activeturn_seconds'],j['user']['last_passiveturn_timestamp'],j['user']['gold'],j['user']['trap']['bait_id']
            else:
                d = {"uh":hash,"last_read_journal_entry_id":lrje,"hg_is_ajax":1,"sn":"Hitgrab"}
                j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/turns/activeturn.php',d,cookies=cookies,headers=post_headers).text)
                hash,user_id,success,wait_time,gold,have_bait,antibot_triggered = j['user']['unique_hash'],j['user']['user_id'],j['success'] and not j['user']['has_puzzle'],j['user']['next_activeturn_seconds'],j['user']['gold'],j['user']['bait_item_id'],int(time.time()*1000) if j['user']['has_puzzle'] else 0
        except: success = 0
        if success:
            print('[%s] horn success. latency: %s, gold: %s, horns: %s%s'%(datetime.datetime.now().replace(microsecond=0),round(time.time()-latency_start,3),gold,horns+1,', antibot: %s'%('TRIGGERED' if antibot_triggered else 'inactive') if antibot_mode == 'bypass' and not args.a else ''))
            if args.a: return 1
            elif antibot_triggered:
                d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.170.0','offset':0,'limit':72,'return_user':'true','login_token':cookie}        
                r = json.loads(requests.post('https://www.mousehuntgame.com/api/get/journalentries/me',d,headers=api_headers).text)
                for entry in r['entries']:
                    if entry['timestamp'] < horn_time: break
                    print_entry(entry['text'])
            else:
                p = False
                for entry in j['journal_markup']:
                    if entry['render_data']['entry_timestamp'] < horn_time-1 and p: break
                    if entry['render_data']['entry_id'] > lrje: lrje = entry['render_data']['entry_id']
                    print_entry(entry['render_data']['text']); p = True
            if not have_bait:
                if cycle: choose_cycle()
                else: change_bait()
            return 1
        else:
            fail += 1
            if fail >= max_fail:
                print('[%s] %s consecutive horn failures. aborting'%(datetime.datetime.now().replace(microsecond=0),fail))
                quit()
            if wait_time: 
                print('[%s] horn not ready'%(datetime.datetime.now().replace(microsecond=0)))
                wait(float((wait_time+2)/60),norandom=True)
            elif antibot_triggered and antibot_triggered != atr:
                print('[%s] antibot triggered'%(datetime.datetime.now().replace(microsecond=0)))
                if not antibot_mode == 'bypass': antibot()
            else: 
                print('[%s] failed to sound the horn. trying again in 3 secs...'%(datetime.datetime.now().replace(microsecond=0)))
                time.sleep(3)

def change_bait():
    print('[%s] out of bait. checking availability...'%(datetime.datetime.now().replace(microsecond=0)))
    r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers)
    j = json.loads(r.text)['components']
    d = {l['type']:l['quantity'] for l in j if l['classification']=='bait' and 'quantity' in l.keys()}
    if not d: print('[%s] no bait in inventory. aborting'%(datetime.datetime.now().replace(microsecond=0))); quit()
    for t in ['gouda_cheese','brie_cheese','marble_cheese','swiss_cheese']:
        if t in d:
            arm_bait(t)
            return print('[%s] armed %s'%(datetime.datetime.now().replace(microsecond=0),t.replace('_',' ')))
    
def regions():
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Travel'},cookies=cookies).text)
    return [s['type'] for r in j['page']['tabs'][0]['regions'] for s in r['environments'] if s['description'] != "You haven't unlocked this environment yet!"]

def antibot():
    global antibot_triggered
    ocr = antibot_mode != 'auto-solve'
    while 1:
        url = 'https://www.mousehuntgame.com/images/puzzleimage.php?t=%s&user_id=%s'%(antibot_triggered,user_id)
        r = requests.get(url).content
        if not ocr:
            try:
                f = json.loads(requests.post('https://api.ocr.space/parse/image',data={'apikey':args.o,'language':'eng','base64Image':'data:image/jpg;base64,%s'%(base64.b64encode(r).decode())}).text)
                v = ''.join(c for c in f['ParsedResults'][0]['ParsedText'].lower().strip() if c in '0987654321poiuytrewqlkjhgfdsamnbvcxzPOIUYTREWQLKJHGFDSAMNBVCXZ')
                print('[%s] auto-solve result: %s'%(datetime.datetime.now().replace(microsecond=0),v))
                assert len(v)==5 and v.isalnum()
            except: ocr = True; print('[%s] auto-solve failed. fallback to manual'%(datetime.datetime.now().replace(microsecond=0)))
        if ocr:
            with open('kingsreward.png','wb') as f: f.write(r)
            if antibot_mode != 'silent': subprocess.run(['kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
            while 1:
                v = input('[%s] enter captcha value, type \'url\' to see image url, or press ENTER to view image...'%(datetime.datetime.now().replace(microsecond=0)))
                if v.lower() == 'url': print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),url))
                elif v == '': 
                    subprocess.run(['kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
                    print("\033[F",end='')
                elif len(v)==5 and v.isalnum(): break
                else: print('[%s] captcha code must be 5 alphanumeric characters'%(datetime.datetime.now().replace(microsecond=0)))
            j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'sn':'Hitgrab','hg_is_ajax':1,'page_class':'Camp','last_read_journal_entry_id':lrje,'uh':hash},cookies=cookies,headers=post_headers).text)
            if not j['user']['has_puzzle']: return print('[%s] already solved'%(datetime.datetime.now().replace(microsecond=0)))
            subprocess.run(['del','kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
        ocr = True
        d = {'code':v,'uh':hash,'action':'solve','sn':'Hitgrab','hg_is_ajax':1}
        try:
            j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/puzzle.php',d,cookies=cookies,headers=post_headers).text)
            if j['success']: antibot_triggered = 0; return print('[%s] code correct'%(datetime.datetime.now().replace(microsecond=0)))
            elif j['user']['has_puzzle']: print('[%s] incorrect code. code is now different'%(datetime.datetime.now().replace(microsecond=0))); antibot_triggered = int(time.time()*1000)
            else: raise Exception
        except: print('[%s] something went wrong. check if code might have changed'%(datetime.datetime.now().replace(microsecond=0)))

initial_wait = 0 if args.a else status_check()
if initial_wait > 60: choose_cycle()
wait(max(float((initial_wait+1)/60),float(args.w if args.w else 0)/60),norandom=True)
while 1:
    if random.random() >= miss_chance or horns==0: 
        try: horns += horn()
        except Exception as e: print('[%s] error: %s'%(datetime.datetime.now().replace(microsecond=0),e));continue
        wait(interval)
    else: 
        print('[%s] giving this one a miss'%(datetime.datetime.now().replace(microsecond=0)))
        wait(random.random()*interval)
        
