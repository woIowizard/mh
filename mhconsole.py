# login
username = ''
password = ''
cookie = ''

########## CODE ##########

banner = '''
MM   MM  H    H   CCCC   OOOO   NN    N   SSSSS   OOOO   L      EEEEE
M M M M  H    H  C      O    O  N N   N  S       O    O  L      E
M  M  M  HHHHHH  C      O    O  N  N  N  SSSSS   O    O  L      EEEEE
M     M  H    H  C      O    O  N   N N       S  O    O  L      E
M     M  H    H   CCCC   OOOO   N    NN  SSSSS    OOOO   LLLLL  EEEEE
'''
print(banner)
print('[=] loading imports and function definitions')

import requests,json,re,subprocess,sys,time,datetime


########## LOGIN RELATED FUNCTIONS ##########
def login_creds():
    global cookie,hash,password,user,sn_user_id,cookies
    r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',{'action':'loginHitGrab','username':username,'password':password},headers=post_headers)
    try: cookie,cookies,hash,user,sn_user_id = r.cookies['HG_TOKEN'],{'HG_TOKEN':r.cookies['HG_TOKEN']}, json.loads(r.text)['user']['unique_hash'], json.loads(r.text)['user']['username'], json.loads(r.text)['user']['sn_user_id']
    except: password = print('[-] login failed')
       
def login_cookie():
    global hash,cookie,user,sn_user_id,cookies
    r = requests.post('https://www.mousehuntgame.com/api/action/passiveturn',{'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','login_token':cookie},headers=api_headers)
    if r.status_code == 200:
        j = json.loads(r.text)['user']
        cookies, hash,user,sn_user_id = {'HG_TOKEN':cookie}, j['uh'], j['name'], j['sn_user_id']
        return json.loads(r.text)
    else: cookie = print('[-] cookie expired'); return None

def try_login():
    global cookie
    if cookie: print('[=] testing provided cookie value'); login_cookie()
    if not hash and username and password: print('[=] attempting to login with provided credentials'); login_creds()
    if hash: print('[+] authentication successful. session cookie: %s'%cookie)
     
     
########## PRE-AUTH FUNCTION ##########
def preauth():
    global username,password,cookie
    help_msg = '''
AVAILABLE COMMANDS:
user [username]\t\tenter username
pass [password]\t\tenter password
cookie [cookie]\t\tenter cookie
show\t\t\tshow credentials entered
login\t\t\tattempt to login with provided credentials
exit\t\t\texit mhconsole'''
    
    cmd = input('\nmh [not logged in] > ')
    cmd,args = cmd.split(' ')[0],' '.join(cmd.split(' ')[1:])
    
    if cmd == 'help': print(help_msg)
    elif not cmd: return 0
    elif cmd == 'user' or cmd == 'username':
        if args: username = args; print('username => %s'%username)
        else: print('command syntax: user [username]')
    elif cmd == 'pass' or cmd == 'password':
        if args: password = args; print('password => %s'%password)
        else: print('command syntax: pass [password]')
    elif cmd == 'cookie':
        if args: cookie = args; print('cookie => %s'%cookie)
        else: print('command syntax: cookie [value]')
    elif cmd == 'show': print('''username:\t%s\npassword:\t%s\ncookie:\t\t%s'''%(username,password,cookie))
    elif cmd == 'login' or cmd == 'run':
        if not cookie and not (username and password): print('[-] provide either cookie value or username + password')
        else: try_login()
    elif cmd == 'exit' or cmd == 'quit': exit_mhconsole()
    else: huh()

def huh(): print('command not recognised. type \'help\' to see available commands')    
def exit_mhconsole(): print('[+] bye!\n'); quit()


########## POST-AUTH FUNCTIONS ##########
def postauth():
    help_msg = '''
========== GENERAL COMMANDS ==========
horn\t\t\tsound the horn
sleep\t\t\tsuspend mhconsole until horn is ready
info\t\t\tshow account and trap info
unauth\t\t\tgo to preauth console without expiring session
logout\t\t\texpire the current session
exit\t\t\texit mhconsole

========== TRAVELLING ==========
move\t\t\tenumerate possible travel locations
move all\t\tenumerate all travel locations
move [name]\t\ttravel to location by name or s/n

========== TRAP ==========
arm\t\t\tshow available trap components
arm [class]\t\tshow subset of available items. classes: bait, base, weapon, charm
arm [type]\t\tarm strongest weapon of type (physical, tactical, ...)
arm [name]\t\tarm item by name or s/n
arm best\t\tlist best traps of each type
arm decharm\t\tremove charm

========== SHOP ==========
buy\t\t\tshow general store items
buy [shop]\t\tshow items in other shops. shops: cheese, trap, charm, all
buy [item] [qty]\tbuy an item by name or s/n

========== CRAFTING ==========
list [keyword]\t\tshow crafting items, filter by keyword 
stat [keyword]\t\tshow crafting and stat items, filter by keyword 
show\t\t\tshow items on crafting table
add [item] [qty]\tadd item to crafting table by name or s/n
del [item]\t\tremove item from crafting table by name or s/n
reset\t\t\tclear crafting table
run [#]\t\t\tcraft using table items # times, default 1
hammer\t\t\tlist items that can be hammered
hammer # [qty]\t\tuse hammer on item by s/n, qty times (default 1, 0 for max)
chest\t\t\tlist chests
chest _\t\t\topen all chests
chest # [qty]\t\topen chest by s/n, qty times (default 1, 0 for max)

========== POTIONS ==========
pot\t\t\tshow all potions
pot #\t\t\tshow recipes for potion by s/n
pot # [rec] [qty]\tuse recipe [rec], [qty] times, for potion # (default 1 for qty, 0 for max)

========== MARKETPLACE ==========
mp\t\t\tshow status of marketplace listings 
mp d id\t\t\tdelete listing
mp c id\t\t\tclaim listing, _ to claim all
mp u id price qty\tupdate listing
mp item\t\t\tshow orders of an item
mp e id \t\texamine orders of an item
mp w item interval\tpoll market values at regular intervals
mp s item price qty\tcreate sell order for an item, price 0 for min-1
mp b item price qty\tcreate buy order for an item, price 0 for max+1

========== ANTIBOT ==========
kr\t\t\tcheck antibot status
kr url\t\t\tdisplay captcha url
kr show\t\t\tdownload and show captcha image
kr [code]\t\tsolve captcha
'''

    def proc(cmd):
        global hash,user,password,cookie
        if all(c in '1234567890.-+*/%() ' for c in cmd): 
            try: return print(eval(cmd.replace(' ','')))
            except: pass
        cmd,args = cmd.split(' ')[0],cmd.split(' ')[1:]
        if cmd == 'help': return print(help_msg)
        elif not cmd: return 0
        elif cmd == 'logout': return logout()
        elif cmd == 'unauth': 
            hash,user,password,cookie = '','','',''
            return print('[+] cookie removed from current console session')
        elif cmd == 'exit' or cmd == 'quit': exit_mhconsole()
        elif cmd in ['horn','info','sleep','arm','move','buy','list','stat','add','del','reset','show','run','hammer','chest','pot','kr','mp']: pass
        else: return huh()
        
        content = login_cookie()
        while not content: 
            hash,user = '',''
            try_login()
            if not hash: return print('[-] will have to login manually')
            content = login_cookie()
            print('')
            
        if cmd == 'horn': horn(content)
        elif cmd == 'sleep': wait(content)
        elif cmd == 'info': info()
        elif cmd == 'move': move(args)
        elif cmd == 'arm': arm(args)
        elif cmd == 'buy': buy(args)
        elif cmd == 'stat': 
            stats = get_stat()
            print('STAT ITEMS')
            list_craft(stats,args if args else '')
        elif cmd in ['list','add','del','reset','show','run']: craft(cmd,args)
        elif cmd == 'hammer': hammer(args)
        elif cmd == 'chest': chest(args)
        elif cmd == 'pot': pot(args)
        elif cmd == 'kr': kr(args)
        elif cmd == 'mp': market(args)
        else: return huh()
    
    cmd = input('\nmh [%s] %s> '%(user,'(!)' if antibot else '')).strip().lstrip()
    while '  ' in cmd: cmd = cmd.replace('  ',' ')
    if ';' not in cmd: proc(cmd)
    else: 
        for c in cmd.split(';'): print(('\nmh [%s] %s> %s'%(user,'(!)' if antibot else '',c.strip().lstrip()))); proc(c.strip().lstrip())        

def print_entry(t):
    try: 
        for m in re.findall('<[^>]*>',t): t = t.replace(m,'')
        s = t.index('!',20) if '!' in t[20:-2] else t.index('.',(t.index('oz.')+3) if 'oz.' in t else 0)
        if t[:s+1]: print('\t%s'%(t[:s+1].lstrip()))
        if t[s+1:]: print_entry(t[s+1:])
    except: print('\t%s'%(t.lstrip()))
       
def wait(content): 
    m = content['user']['next_activeturn_seconds']
    if m: print('[=] sleeping for %s:%s till %s...'%(m//60,m%60,('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=m))).split(' ')[1]));time.sleep(m)
    return print('[+] horn ready')
    
def horn(content): 
    lpt = content['user']['last_passiveturn_timestamp']
    m = content['user']['next_activeturn_seconds']
    if m: return print('[-] too soon to sound. next horn in %s:%s at %s'%(m//60,m%60,('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=m))).split(' ')[1]))
    else:
        horn_time = int(time.time())   
        r = json.loads(requests.post('https://www.mousehuntgame.com/api/action/turn/me',{'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','last_passiveturn_timestamp':lpt,'login_token':cookie},headers=api_headers).text)
        if r['success']: 
            print('[+] successfully sounded the horn. response:\n\t[%s]'%(datetime.datetime.now().replace(microsecond=0)))
            r = json.loads(requests.post('https://www.mousehuntgame.com/api/get/journalentries/me',{'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','offset':0,'limit':72,'return_user':'true','login_token':cookie},headers=api_headers).text)
            for entry in r['entries']:
                if entry['timestamp'] < horn_time: return print('\n\tnext horn: %s'%('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=900))).split(' ')[1])
                print_entry(entry['text'])
        else: print('[-] failed to sound the horn')
    
def info():     
    global antibot
    content = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers).text
    antibot = '"has_puzzle":true' in content
    
    m = int(re.findall('"next_activeturn_seconds":(\d*)',content)[0])
    next_horn = '%s:%s'%(m//60,m%60) if m else 'READY'
    url = 'https://www.mousehuntgame.com/images/puzzleimage.php?snuid=%s&hash=%s'%(sn_user_id,hash)
    print('HORN INFO\nnext horn:\t%s at %s\nantibot:\t%s\n%s'%(next_horn,('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=m))).split(' ')[1],'ACTIVE' if antibot else 'inactive','KR url:\t\t%s\n'%url if antibot else ''))
    
    gold = re.findall('"gold":(\d*)',content)[0]
    points = re.findall('"points":(\d*)',content)[0]
    print('WEALTH INFO\ngold:\t\t%s\npoints:\t\t%s\n'%(gold,points))

    base = re.findall('"base_name":"([^"]*)"',content)[0]
    weapon = re.findall('"weapon_name":"([^"]*)"',content)[0]
    type = re.findall('"trap_power_type_name":"([^"]*)"',content)[0]
    bait = re.findall('"bait_name":"([^"]*)"',content)
    bait = bait[0] if bait else 'out of bait'
    baitq = re.findall('"bait_quantity":(\d*)',content)[0]
    power = re.findall('"trap_power":(\d*)',content)[0]
    luck = re.findall('"trap_luck":(\d*)',content)[0]
    freshness = re.findall('"trap_cheese_effect":"([^"]*)"',content)[0]
    print('TRAP INFO\nbase:\t\t%s\nweapon:\t\t%s\ntype:\t\t%s\nbait:\t\t%s\nquantity:\t%s\npower:\t\t%s\nluck:\t\t%s\nfreshness:\t%s'%(base,weapon,type,bait,baitq,power,luck,freshness),end='')
    try: 
        charm = re.findall('"trinket_name":"([^"]*)"',content)[0]
        charmq = re.findall('"trinket_quantity":(\d*)',content)[0]
        print('\ncharm:\t\t%s\ncharm quantity:\t%s\n'%(charm,charmq))
    except: print('\n')
    
    print('LOGIN INFO\ncookie:\t\t%s\nhash:\t\t%s\n'%(cookie,hash))

    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/getmiceeffectiveness.php',{'uh':hash},cookies=cookies,headers=post_headers).text)
    print('LOCATION INFO\nlocation:\t%s'%(j['location']))
    for k in j['effectiveness']: print('{0:<12}\t{1}'.format(j['effectiveness'][k]['difficulty']+':',', '.join([m['name'] for m in j['effectiveness'][k]['mice']])))
    
def move(args): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Travel'},cookies=cookies,headers=post_headers).text)['page']['tabs'][0]['regions']
    col,act = {v['name']:[] for v in j},{}
    i = 1
    for v in j:
        for e in v['environments']: 
            active = e['description'] != 'You haven\'t unlocked this environment yet!'
            col[v['name']].append((i,e['type'],e['name'],active))
            if active and v['name'] not in act: act[v['name']] = []
            if active: act[v['name']].append((i,e['type'],e['name']))
            i += 1
    if not args:
        for n in act:
            print('========== %s ==========\nNO.\tMH NAME\t\t\t\tCOMMON NAME'%n)
            for e in act[n]: print('{0:<3}\t{1:<30}\t{2:<25}'.format(e[0],e[1],e[2]))
            print('')
    elif args[0]=='all':
        for n in col:
            print('========== %s ==========\nNO.\tMH NAME\t\t\t\tCOMMON NAME\t\t\tACTIVE'%n)
            for e in col[n]: print('{0:<3}\t{1:<30}\t{2:<25}\t{3}'.format(e[0],e[1],e[2],e[3]))
            print('')
    else:
        for e in [x for n in col for x in col[n]]:
            if '_'.join(args).lower() in [str(e[0]),e[1]]: 
                if e[3]: 
                    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':hash,'destination':e[1]},headers=post_headers,cookies=cookies).text)
                    if j['success']: print('[+] travelled to %s'%(e[2].lower()))
                    else: print('[-] %s'%(j['result']))
                else: print('[-] no access to that location')
                return
        print('[-] unrecognised location')

def arm(args):
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)['components']
    items,best_weapons = {},{}
    i = 0
    for c in ['base','weapon','bait','trinket']:
        items[c] = []
        subitems = [i for i in j if i['classification']==c]
        subitems.sort(key=lambda x:x['type'])
        for item in subitems: 
            if c == 'base': items[c].append((i,item['type'],item['name'],item['power'],item['cheese_effect']))
            elif c == 'weapon': 
                items[c].append((i,item['type'],item['name'],item['power_type_name'],item['power'],item['luck'] if 'luck' in item else '0',item['cheese_effect']))
                if item['power_type_name'].lower() not in best_weapons or best_weapons[item['power_type_name'].lower()][1] <= item['power']: best_weapons[item['power_type_name'].lower()] = (item['type'],item['power'],item['name'])
            elif c == 'bait': items[c].append((i,item['type'],item['name'],item['quantity'] if 'quantity' in item else 0))
            elif c == 'trinket': items[c].append((i,item['type'],item['name'],item['quantity'] if 'quantity' in item else 0))
            i += 1
            
    cmd = '_'.join(args) if args else 'all'
    if cmd == 'help': return print(help_msg)
    if cmd == 'best':
        print('TYPE\t\tTRAP')
        for t in best_weapons: print('{0:<10}\t{1}'.format(t,best_weapons[t][2]))
    if cmd == 'all' or cmd == 'base':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tPOWER\t\tEFFECT')
        for n in items['base']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        print('')
    if cmd == 'all' or cmd == 'weapon' or cmd == 'trap':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tTYPE\t\tPOWER\t\tLUCK\t\tEFFECT')
        for n in items['weapon']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3:<8}\t{4:<8}\t{5:<8}\t{6}'.format(n[0],n[1],n[2]
,n[3],n[4],n[5],n[6]))
        print('')
    if cmd == 'all' or cmd == 'bait':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tQTY')
        for n in items['bait']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3}'.format(n[0],n[1],n[2],n[3]))
        print('')
    if cmd == 'all' or cmd == 'charm':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tQTY')
        for n in items['trinket']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3}'.format(n[0],n[1],n[2],n[3]))
        print('')
    if cmd == 'decharm':
        requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'trinket':'disarm'},headers=post_headers,cookies=cookies)
        print('[+] disarmed charm')
    if cmd not in ['all','best','bait','base','weapon','charm','decharm']:
        if cmd.lower() in best_weapons: 
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'weapon':best_weapons[cmd.lower()][0]},headers=post_headers,cookies=cookies)
            return print('[+] armed %s'%(best_weapons[cmd.lower()][0]))
        for k in items:
            for n in items[k]:
                if cmd in [str(n[0]),n[1]] or cmd+'_cheese' == n[1] or cmd+'_base' == n[1] or cmd+'_weapon' == n[1] or cmd+'_trinket' == n[1]:
                    requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,k:n[1]},headers=post_headers,cookies=cookies)
                    return print('[+] armed %s'%(n[2].lower()))
        print('[-] component not recognised')
    
def buy(args): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Shops'},cookies=cookies,headers=post_headers).text)['page']['tabs']
    items,i = {c['name']:[] for c in j[:-2]},0
    for tab in j[:-2]:
        for item in tab['subtabs'][0]['items']: 
            items[tab['name']].append((i,item['item']['type'],item['shop_item_name'],item['gold_cost'],item['refund']))
            i += 1
            
    if not args:
        if 'General Store' in items:    
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['General Store']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no general store in this location')
    elif args[0]=='cheese' or args[0]=='bait': 
        if 'Cheese Shop' in items:
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['Cheese Shop']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no cheese shop in this location')
    elif args[0]=='trap': 
        if 'Trapsmith' in items:
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['Trapsmith']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no trapsmith in this location')
    elif args[0]=='charm': 
        if 'Charm Shop' in items:
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['Charm Shop']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no charm shop in this location')
    elif args[0]=='all': 
        print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
        for k in items:
            for n in items[k]: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
    elif len(args) > 1:
        target_name = '_'.join(args[:-1]).lower()
        if target_name == 'curds': target_name = 'curds_and_whey'
        if target_name == 'milk': target_name = 'coconut_milk'        
        for n in [n for k in items for n in items[k]]:
            if target_name in [str(n[0]),n[1]] or (target_name + '_craft_item' == n[1]) or (target_name + '_crafting_item') == n[1] or (target_name + '_cheese') == n[1] or (target_name + '_trinket') == n[1]: 
                target_item = n[1]
                try: quant = int(args[-1])
                except: return print('quantity must be an integer')
                j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':hash,'type':target_item,'quantity':quant,'buy':1},headers=post_headers,cookies=cookies).text)
                if j['success']: print('[+] bought %s %s'%(quant,n[2]))
                else: print('[-] %s'%j['error_message'])
                return 0
        print('item not found in stores')
    else: huh()

def craft(cmd,args): 
    global table
    items = get_craft()
            
    if cmd == 'list': 
        print('ITEMS IN INVENTORY')
        list_craft(items,args if args else '')
    elif cmd == 'show': 
        print('ITEMS ON CRAFTING TABLE')
        list_craft(table)
    elif cmd == 'add':
        if not args: return print('[-] usage: add [item] [quantity]')
        try: int(args[-1]); assert len(args) > 1
        except: args.append('1')
        try: target_item = list(items.keys())[int(args[0])]
        except:
            target_item = '_'.join(args[:-1]).lower()
            if target_item == 'curds': target_item = 'curds_and_whey'
            if target_item == 'milk': target_item = 'coconut_milk'
            if target_item in items.keys(): pass
            elif target_item + '_craft_item' in items.keys(): target_item += '_craft_item'
            elif target_item + '_crafting_item' in items.keys(): target_item += '_crafting_item'
            else: return print('[-] item not found in inventory')
        try: target_quant = int(args[-1])
        except: return print('[-] quantity must be an integer')
        if target_quant > int(items[target_item][1]): return print('[-] quantity exceeds amount in inventory')
        table[target_item] = (items[target_item][0],target_quant)
        print('[+] updated quantity of %s on crafting table to %s'%(items[target_item][0].lower(),target_quant))
    elif cmd == 'reset':
        table = {}
        print('[+] crafting table cleared')
    elif cmd == 'del':
        if not args: return print('[-] usage: del [item]')
        try: target_item = list(table.keys())[int(args[0])]
        except:            
            if args[0] in table.keys(): target_item = args[0]
            else: return print('[-] item not found on table')
        name = table[target_item][0].lower()
        table.pop(target_item)
        print('[+] %s removed from crafting table'%(name))
    elif cmd == 'run': 
        try: times = int(args[0])
        except: times = 1
        d = {'parts[%s]'%l:table[l][1] for l in table}
        d['craftQty'] = times
        d['uh'] = hash
        try: j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',d,cookies=cookies,headers=post_headers).text)
        except: return print('[-] something went wrong')
        if j['success'] == 1:
            t = j['messageData']['message_model']['messages'][0]['messageData']['content']['body']
            for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
            print('[+] %s'%t)
        else: print('[-] %s'%j['jsDialog']['tokens']['content']['value'])
    elif cmd == 'back': return 0
    elif cmd == 'exit' or cmd == 'quit': exit_mhconsole()
    else: huh()
        
def get_craft(): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)['components']
    items = sorted([c for c in j if c['classification'] == 'crafting_item'],key=lambda x:x['type'])
    return {l['type']:(l['name'],l['quantity']) for l in items}

def get_stat(): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)['components']
    items = sorted([c for c in j if c['classification'] in ['stat','trinket','crafting_item']],key=lambda x:x['type'])
    return {l['type']:(l['name'],l['quantity']) for l in items}

def list_craft(items,k=''):
    print('NO.\tQTY\tMH NAME\t\t\t\t\t\tCOMMON NAME')
    cache = {'fofo':'crop_coin_stat_item|inspiration_ink_stat_item|parable_papyrus_stat_item|pond_penny_stat_item|draft_derby_curd_stat_item|cleverness_clam_stat_item|ingenuity_grub_stat_item|condensed_creativity_stat_item','sc':'sand_dollar_stat_item|oxygen_stat_item|damaged_coral_crafting_item|barnacle_crafting_item|brined_curd_crafting_item|mouse_scale_crafting_item|water_jet_trinket|anchor_trinket|predatory_processor_crafting_item','fi':'cloud_curd_crafting_item|airship_rocket_fuel_stat_item|floating_islands_cloud_gem_stat_item|sky_scrambler_stat_item|cloudstone_bangle_stat_item|floating_islands_sky_ore_stat_item|bottled_wind_stat_item|empyrean_seal_stat_item|enchanted_wing_stat_item|sky_pirate_cheese_curd_crafting_item|sky_pirate_seal_stat_item|skysoft_silk_stat_item|sky_sprocket_stat_item','queso':'queso|spice_crafting_item|ember_root_crafting_item|ember_stone_crafting_item|wild_tonic_stat_item|magic_cork_dust_stat_item','vrift':'rift_ultimate_|rift_gauntlet_fuel_stat_item|gauntlet_elixir_stat_item','lg':'|'.join('essence_%s_crafting_item'%c for c in 'abcdefghi')+'|plumepearl_herbs_crafting_item|lunaria_petal_crafting_item'}
    if ' '.join(k) in cache: k = [cache[' '.join(k)]]
    for ind,n in enumerate(items):     
        if [c for c in ' '.join(k).split('|') if c.lower() in items[n][0].lower() or c.replace(' ','_') in n]: print('{0:<3}\t{1:<5}\t{2:<40}\t{3}'.format(ind,items[n][1],n,items[n][0]))

def market(args): 
    global mp
    if not mp or not args or args[0] not in 'sbw': 
        j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/marketplace.php',{'sn':'Hitgrab','hg_is_ajax':1,'action':'marketplace_info','uh':hash},cookies=cookies,headers=post_headers).text)
        mp['r'] = {str(l['item_id']):(l['type'],l['name']) for l in j['marketplace_items']}
        mp['me'] = {str(l['listing_id']):l for l in j['marketplace_my_listings']}
    
    if not args: 
        if not mp['me']: print('[=] no marketplace listing')
        else: 
            print('NO.\tLISTING ID\tTYPE\tITEM ID\t\tUNIT PRICE\tQTY\t\tCLAIM\t\tNAME')
            for i,l in enumerate(sorted(mp['me'].values(),key=lambda x:int(x['listing_id']))): print('{0:<3}\t{1:<8}\t{2}\t{3:<5}\t\t{4:<10}\t{5:<5}\t\t{6:<5}\t\t{7}'.format(i+1,l['listing_id'],l['listing_type'],l['item_id'],l['unit_price'],l['remaining_quantity'],'no' if (l['listing_type'] == 'buy' and not l['item_escrow']) or (l['listing_type'] == 'sell' and not l['gold_escrow']) else 'YES',mp['r'][str(l['item_id'])][1]))
        return
    
    if args[0] == 'e': 
        try: assert len(args) == 2 and int(args[1]) > 0
        except: return print('[-] usage: mp e #')
        if int(args[1]) > len(mp['me'].keys()): return print('[-] listing not found')
        args = [str(mp['me'][sorted(mp['me'].keys())[int(args[1])-1]]['item_id'])]
    
    if args[0] in ['c','d','u']: 
        if args == ['c','_']: pass        
        elif args[0] in ['c','d']: 
            try: assert len(args) == 2 and int(args[1]) > 0
            except: return print('[-] usage: mp c/d id')
        else:
            try: assert len(args) == 4 and int(args[-1]) >= 0 and (int(args[-2]) >= 10 or int(args[-2])) in [0,-1]
            except: return print('[-] usage: mp u id price qty')

        if args[1] not in mp['me'] and args[1] != '_':
            if int(args[1]) > len(mp['me'].keys()): return print('[-] listing not found')
            args[1] = sorted(mp['me'].keys())[int(args[1])-1]
            
        for l in (mp['me'] if args == ['c','_'] else [args[1]]):
        
            if args[0] == 'c' and ((mp['me'][l]['listing_type'] == 'buy' and not mp['me'][l]['item_escrow']) or (mp['me'][l]['listing_type'] == 'sell' and not mp['me'][l]['gold_escrow'])): 
                if args != ['c','_']: return print('[-] listing not ready to claim')
                else: continue
            if args[0] == 'u': t = [mp['me'][args[1]]['listing_type'][0],str(mp['me'][args[1]]['item_id']),args[-2],args[-1]]
            
            r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/marketplace.php',{'sn':'Hitgrab','hg_is_ajax':1,'action':'cancel' if args[0] in ['u','d'] else 'claim','uh':hash,'listing_id':l},cookies=cookies,headers=post_headers).text
            try: j = json.loads(r)
            except: return print('[-] %s'%r)   

            if j['success']: 
                if args[0] == 'c': print('[+] listing %s claimed: received %s %s%s'%(l,mp['me'][l]['item_escrow' if mp['me'][l]['listing_type'] == 'buy' else 'gold_escrow'],mp['r'][str(mp['me'][l]['item_id'])][1] if mp['me'][l]['listing_type'] == 'buy' else 'gold','\n' if args[1] == '_' else ''))
                elif args[0] in ['d','u']: print('[+] listing %s cancelled: received %s %s and %s gold'%(l,mp['me'][l]['item_escrow'],mp['r'][str(mp['me'][l]['item_id'])][1],mp['me'][l]['gold_escrow']))
            else: return print('[-] %s'%j['marketplace_error'])
        
        mp['me'] = {str(l['listing_id']):l for l in j['marketplace_my_listings']}

        if args[0] != 'u': return
        else: args = t
        
    if args[0] in ['s','b']:
        try: assert len(args) >= 4 and int(args[-1]) >= (0 if args[0] == 's' else 1) and (int(args[-2]) >= 10 or int(args[-2]) in [-1,0] )
        except: return print('[-] usage: mp b/s item price qty')
        ia = '_'.join(args[1:-2])
    elif args[0] == 'w':
        try: assert len(args) >= 3 and int(args[-1]) > 0
        except: return print('[-] usage: mp w item time')
        ia = '_'.join(args[1:-1])
    else: ia = '_'.join(args)
    
    cache = {'sb':[c for c in mp['r'] if mp['r'][c][0]=='super_brie_cheese'][0],'frc':'birthday_factory_trinket','scc':'speed_coggy_colby_cheese','msc':'magical_string_cheese','wt':'wild_tonic_stat_item','gg':'glowing_gruyere_cheese','asc':'ancient_string_cheese','ps':'rift_scramble_portals_stat_item','qq':'rift_quantum_quartz_stat_item','gpp':'glazed_pecan_pecorino_cheese','fs':'festive_spirit_stat_item','rr':'cauldron_instant_finish_stat_item'}
    if ia in cache: ia = cache[ia]
    
    if ia in mp['r']: iid = ia
    else:
        sr = [l for l in mp['r'] if ia in mp['r'][l][0]]
        if not sr: return print('[-] no matching item found')
        print('ITEM ID\t\tTYPE')
        for l in sr: print('{0:<5}\t\t{1}'.format(l,mp['r'][l][0]))
        if len(sr) == 1: iid = sr[0]
        else: return
    
    gold,items = get_items()
    mpl = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/marketplace.php',{'sn':'Hitgrab','hg_is_ajax':1,'action':'get_item_listings','uh':hash,'item_id':iid},cookies=cookies,headers=post_headers).text)
    try: ms = min(x['unit_price'] for x in mpl['marketplace_item_listings'][iid]['sell'])-1
    except: ms = 0
    try: mb = max(x['unit_price'] for x in mpl['marketplace_item_listings'][iid]['buy'])+1
    except: mb = 0
    
    if args[0] in ['s','b']:
        if int(args[-2]) in [-1,0]: 
            if (args[0] == 's' and not ms) or (args[0] == 'b' and not mb): return print('[-] no %s orders'%('sell' if args[0] == 's' else 'buy'))
            if not int(args[-2]): args[-2] = ms if args[0] == 's' else mb
            else: args[-2] = mb-1 if args[0] == 's' else ms+1
        if args[0] == 's':
            if mp['r'][iid][0] not in items or items[mp['r'][iid][0]] < int(args[-1]): return print('[-] insufficient %s (have %s)'%(mp['r'][iid][1],items[mp['r'][iid][0]] if mp['r'][iid][0] in items else 0))
            if not int(args[-1]): args[-1] = items[mp['r'][iid][0]] if mp['r'][iid][0] in items else 0
        elif gold < int(args[-1])*int(args[-2]): return print('[-] insufficient gold (require %s, have %s)'%(int(args[-1])*int(args[-2]),gold))
        
        if args[0] == 's' and int(args[-2]) < min(mb-1,ms): 
            confirm = None
            while confirm not in list('ny'): confirm = input('[!] sell at significant loss? N/Y to proceed: ').lower()
            if confirm != 'y': return
        
        j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/marketplace.php',{'sn':'Hitgrab','hg_is_ajax':1,'action':'create','uh':hash,'item_id':iid,'unit_price':args[-2],'quantity':args[-1],'listing_type':'buy' if args[0] == 'b' else 'sell'},cookies=cookies,headers=post_headers).text)
        if j['success']: 
            print('\n[+] listing %s created: %s %s x %s for %s each'%(j['marketplace_new_listing']['listing_id'],'selling' if args[0] == 's' else 'buying',args[-1],mp['r'][iid][1],args[-2]))
            mp['me'] = {str(l['listing_id']):l for l in j['marketplace_my_listings']}
        else: print('\n[-] %s'%j['marketplace_error'])
    
    while 1:    
        mn = int(ms/1.1-mb)
        print('\nSHOWING LISTINGS FOR: %s (inv: %s, margin: %s%s, name: %s)'%(mp['r'][iid][1],items[mp['r'][iid][0]] if mp['r'][iid][0] in items else 0, '+' if mn > 0 else '',mn,mp['r'][iid][0]))
        print('\n=================== SELL ORDERS ===================\t\t=================== BUY ORDERS ===================\nQTY\tSELL PRICE\tAFTER TAX\tBEFORE TAX\t\tQTY\tBUY PRICE\tBEFORE TAX\tAFTER TAX')
        ph = [{'quantity':0,'unit_price':0,'unit_price_without_tariff':0}]*4
        for x,y in zip(mpl['marketplace_item_listings'][iid]['sell'] if mpl['marketplace_item_listings'][iid]['sell'] else ph,mpl['marketplace_item_listings'][iid]['buy'] if mpl['marketplace_item_listings'][iid]['buy'] else ph): print('{0:<5}\t{1:<10}\t{2:<10}\t{3:<10}\t\t{4:<5}\t{5:<10}\t{6:<10}\t{7:<10}'.format(x['quantity'],x['unit_price'],x['unit_price_without_tariff'],int(x['unit_price']*1.1),y['quantity'],y['unit_price'],int(y['unit_price']*1.1),int(y['unit_price']/1.1)))
        sr = [mp['me'][l] for l in mp['me'] if str(mp['me'][l]['item_id']) == iid]
        if sr and args[0] != 'w': 
            print('\n================================================== MY LISTINGS ==================================================')
            print('NO.\tLISTING ID\tTYPE\tITEM ID\t\tUNIT PRICE\tQTY\t\tCLAIM\t\tNAME')
            for l in sorted(sr,key=lambda x:x['listing_id']): print('{0:<3}\t{1:<8}\t{2}\t{3:<5}\t\t{4:<10}\t{5:<5}\t\t{6:<3}\t\t{7}'.format(1+sorted(mp['me'].keys()).index(str(l['listing_id'])),l['listing_id'],l['listing_type'],l['item_id'],str(l['unit_price'])+('*' if (l['listing_type'] == 'sell' and l['unit_price'] > ms) or (l['listing_type'] == 'buy' and l['unit_price'] < mb)  else '(!)' if (l['listing_type'] == 'sell' and l['unit_price'] < ms) or (l['listing_type'] == 'buy' and l['unit_price'] > mb) else ''),l['remaining_quantity'],'no' if (l['listing_type'] == 'buy' and not l['item_escrow']) or (l['listing_type'] == 'sell' and not l['gold_escrow']) else 'YES',mp['r'][str(l['item_id'])][1]))
        if args[0] != 'w': return
        print('\n[=] next watch in %s secs at %s...'%(args[-1],('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=int(args[-1])))).split(' ')[1]))
        time.sleep(int(args[-1]))
        mpl = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/marketplace.php',{'sn':'Hitgrab','hg_is_ajax':1,'action':'get_item_listings','uh':hash,'item_id':iid},cookies=cookies,headers=post_headers).text)
        
def get_items(): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    return j['user']['gold'],{c['type']:c['quantity'] if 'quantity' in c else 0 for c in j['components']}

def hammer(args): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Inventory','page_arguments[tab]':'crafting','page_arguments[sub_tab]':'hammer'},cookies=cookies,headers=post_headers).text)
    hammerables = {item['type']:(item['quantity'],item['hammer_result_item_type']) for category in j['page']['tabs'][2]['subtabs'][2]['tags'] for item in category['items']}
    items = sorted(list(hammerables.keys()))
            
    if not args: 
        print('NO.\tQTY\tMH NAME\t\t\t\t\t\tHAMMER RESULT')
        for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2:<40}\t{3}'.format(ind,hammerables[n][0],n,hammerables[n][1]))
    elif len(args) > 2: print('[-] usage: hammer [s/n] [qty]')
    else:
        if len(args) == 2:
            try: qty = int(args[-1]); assert qty >= 0
            except: return print('[-] quantity must be a non-negative integer')
        else: qty = 1
        try: target_item = int(args[0]); assert target_item >= 0
        except: return print('[-] usage: s/n must be a non-negative integer')
        try: target_item = items[target_item]
        except: return print('[-] s/n not found')
        if not qty: qty = hammerables[target_item][0]
        if qty > hammerables[target_item][0]: return print('[-] quantity exceeds inventory')
        j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'uh':hash,'item_type':target_item,'item_qty':qty},headers=post_headers,cookies=cookies).text)
        if j['success'] == 1:
            t = j['messageData']['message_model']['messages'][0]['messageData']['content']['body']
            for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
            print('[+] %s'%t)
        else: print('[-] %s'%j['jsDialog']['tokens']['content']['value'])       
        
def chest(args): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    chests = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='convertible' and 'quantity' in l.keys()}
    items = sorted(list(chests.keys()))
            
    if not args: 
        print('NO.\tQTY\tMH NAME')
        for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2}'.format(ind,chests[n],n))
    elif len(args) > 2: print('[-] usage: chest [s/n] [qty]')
    elif args == ['_'] and not items: return print('[-] no chests')
    else:
        if len(args) == 2:
            try: qty = int(args[-1]); assert qty >= 0
            except: return print('[-] quantity must be a non-negative integer')
        else: qty = 1
        
        if args != ['_']:
            try: target_item = int(args[0]); assert target_item >= 0
            except: return print('[-] usage: s/n must be a non-negative integer')
            try: items = [items[target_item]]
            except: return print('[-] s/n not found')
        
        for target_item in items:
            if not qty or args == ['_']: qty = chests[target_item]
            if qty > chests[target_item]: return print('[-] quantity exceeds inventory')
            chest_time = int(time.time())
            j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'uh':hash,'item_type':target_item,'item_qty':qty},headers=post_headers,cookies=cookies).text)
            if j['success'] == 1:    
                r = json.loads(requests.post('https://www.mousehuntgame.com/api/get/journalentries/me',{'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','offset':0,'limit':72,'return_user':'true','login_token':cookie},headers=api_headers).text)
                for entry in r['entries']:
                    if entry['timestamp'] < chest_time: break
                    print(entry['text'] + ('\n' if args == ['_'] else ''))
            else: print('[-] failed')
        
def pot(args):
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    potions = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='potion' and 'quantity' in l.keys()}
    baits = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='bait' and 'quantity' in l.keys()}
    items = sorted(list(potions.keys()))
    
    if not args: 
        print('NO.\tQTY\tPOTION')
        for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2}'.format(ind,potions[n],n))
        return
    
    if len(args) > 3: return print('[-] usage: pot [s/n] [rec] [qty]')
    try: target_item = int(args[0]); assert target_item >= 0
    except: return print('[-] usage: s/n must be a non-negative integer')
    try: target_item = items[target_item]
    except: return print('[-] s/n not found')
    p = {r['recipe_index']:(r['consumed_item_name'],r['consumed_item_type'],r['consumed_item_cost'],r['produced_item_name'],r['produced_item_type'],r['produced_item_yield']) for r in [l for l in j['components'] if l['classification']=='potion' if l['type']==target_item][0]['recipe_list']}
    
    if len(args) == 1:
        print('===== RECIPES FOR %s ====='%target_item.replace('_',' ').upper())
        print('NO.\tCONSUMED ITEM\t\t\tQTY\tPRODUCED ITEM\t\t\tQTY')
        for i in range(len(p.keys())): print('{0:<3}\t{1:<30}\t{2}\t{3:<30}\t{4}'.format(i,p[i][0],p[i][2],p[i][3],p[i][5]))
        return
        
    try: rec = int(args[1]); assert rec >= 0
    except: return print('[-] recipe s/n must be a non-negative integer')
    if rec not in p: return print('[-] recipe not found')
        
    if len(args) == 3:
        try: qty = int(args[-1]); assert qty >= 0
        except: return print('[-] quantity must be a non-negative integer')
    else: qty = 1
    if not qty: qty = potions[target_item]
    if qty > potions[target_item]: return print('[-] quantity exceeds number of potions in inventory')
    if p[rec][1] not in baits or baits[p[rec][1]] < qty*p[rec][2]: return print('[-] insufficient %s: need %s, have %s'%(p[rec][0].lower(),qty*p[rec][2],baits[p[rec][1]] if p[rec][1] in baits else 0))
    
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/usepotion.php',{'potion':target_item,'num_potions':qty,'recipe_index':rec,'uh':hash},headers=post_headers,cookies=cookies).text)
    if j['success'] == 1:
        t = j['messageData']['message_model']['messages'][0]['messageData']['content']['title'] + ' ' + j['messageData']['message_model']['messages'][0]['messageData']['content']['body']
        for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
        print('[+] %s'%t)
    else: print('[-] %s'%j['messageData']['popup']['messages'][0]['messageData']['body'])
    
def kr(args):
    global antibot
    if not args or not antibot or args[0] not in ['show','url']: antibot = '"has_puzzle":true' in requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers).text
    
    if not antibot: return print('[=] antibot inactive')
    elif not args: return print('[!] antibot active')
    elif len(args) > 1: return huh()
    
    url = 'https://www.mousehuntgame.com/images/puzzleimage.php?snuid=%s&hash=%s'%(sn_user_id,hash)
    if args[0] == 'url': return print('[=] captcha url: %s'%url)
    elif args[0] == 'show':        
        with open('kingsreward.png','wb') as f: f.write(requests.get(url).content)
        subprocess.run(['kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
    elif len(args[0])!=5 or not args[0].isalnum(): return print('[-] code must be 5 alphanumeric characters')
    else:
        subprocess.run(['del','kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
        r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/solvePuzzle.php',{'puzzle_answer':args[0],'uh':hash},cookies=cookies,headers=post_headers)
        if 'Reward claimed!' in r.text: antibot = False; return print('[+] code correct')
        elif 'Incorrect claim code, please try again' in r.text: print('[-] incorrect code. code is now different')
        else: print('[-] something went wrong. check if code might have changed')

def logout(): 
    global hash,cookie
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',{'uh':hash,'action':'logout'},headers=post_headers,cookies=cookies)
    hash,user,cookie = '','',''
    print('[+] cookie expired')

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent': useragent}
get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '1', 'TE': 'trailers', 'Upgrade-Insecure-Requests': '1', 'User-Agent': useragent}
api_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'file://', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
user,hash,sn_user_id,antibot,table,cookies,mp = '','','',False,{},{},{}

try: cookie = cookie
except: cookie = ''
try: username,password = username,password
except: username,password = '',''
if cookie or (username and password): try_login()

while 1:
    try: preauth() if not hash else postauth()
    except KeyboardInterrupt as e: print('')