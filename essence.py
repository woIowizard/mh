import requests,json,sys

def usage():
    n = sys.argv[0].split('\\')[-1]
    msg = '''usage:
%s cookie l \t\tlist esssences in inventory
%s cookie c target\tcheck if target is viable, but don't craft
%s cookie x target\tcraft target if viable
target specification: comma-separated key=value pairs, [a-i] for max of an essence, or 'm' for max
  '''%(n,n,n)
    print(msg)
    quit()
    
if len(sys.argv) not in [3,4] or sys.argv[2] not in 'lcx' or (sys.argv[2] == 'l') != (len(sys.argv) == 3): usage()

rs = 'abcdefghi'
def ct(d): 
	a,t = [],0
	for i in range(9):
		t += d[rs[i]]*(3**i)
		a.append(t)
	return a

def translate(n): return {'a':'aleph','b':'ber','c':'cynd','d':'dol','e':'est','f':'fel','g':'gur','h':'hix','i':'icuri'}[n]
    

if len(sys.argv) == 4 and sys.argv[3] not in rs+'m':
    w = {c:0 for c in rs}
    try:
        for p in sys.argv[3].split(','):
            if p.split('=')[0] in w: w[p.split('=')[0]] = int(p.split('=')[1])
    except: print('invalid target specification. quitting!'); quit()
    w['t'] = ct(w)

cache = {
    'cookie-name':'cookie-val'
}
cookies = {'HG_TOKEN':cache[sys.argv[1]] if sys.argv[1] in cache else sys.argv[1]}
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}
try: j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
except: print('invalid cookie'); quit()
    
crafts = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='crafting_item' and 'quantity' in l.keys()}
h = {c:(crafts['essence_%s_crafting_item'%c] if 'essence_%s_crafting_item'%c in crafts else 0) for c in rs}
h['t'] = ct(h)

print('''===== ESSENCES IN INVENTORY =====\n%s\naleph equivalent: %s\n'''%('\n'.join('%s\t%s'%(translate(c),h[c]) for c in rs),h['t'][-1]))
if sys.argv[2] == 'l': quit()

if sys.argv[3] == 'm':
    w = {v:(h['t'][-1]%(3**(i+1))//(3**i)) for i,v in enumerate(rs)}
    w['i'] = h['t'][-1]//(3**8)
    w['t'] = ct(w)
elif sys.argv[3] in rs:
    w = {c:0 for c in rs}
    w[sys.argv[3]] = max(1,h['t'][-1]//(3**rs.index(sys.argv[3])))
    w['t'] = ct(w)
if w['t'][-1] > h['t'][-1]: print('not enough essences (lacking %s aleth equivalent)'%(w['t'][-1]-h['t'][-1])); quit()

hs = {c:0 for c in rs}
while not all(x <= y for x,y in zip(w['t'],h['t'])):
    i = 8
    while w['t'][i-1] <= h['t'][i-1]: i -= 1
    h[rs[i]] -= 1
    h['a'] += 3**i
    h['t'] = ct(h)
    hs[rs[i]] += 1
    
st,xsc = [],0
for i in range(8):
	xs = min(h['t'][j]-w['t'][j]-xsc for j in range(i,9))
	if (h[rs[i]]-w[rs[i]])*(3**i) <= xs:
		xsc += (h[rs[i]]-w[rs[i]])*(3**i)
		st.append(0)
	else:
		tc = (h[rs[i]]-w[rs[i]]-xs//(3**i))//3
		xsc += xs
		st.append(tc)
		h[rs[i]] -= tc*3
		h[rs[i+1]] += tc

print('===== CRAFTING STRATEGY =====')
if sum(hs[c] for c in rs): print('hammer: %s'%', '.join('%s %s times'%(translate(c),hs[c]) for c in rs if hs[c]))
if sum(st): print('craft: %s'%', '.join('%s %s times'%(translate(rs[c]),st[c]) for c in range(8) if st[c]))
print('result: %s\n'%', '.join('%s %s'%(h[c],translate(c)) for c in rs))
if sys.argv[2] == 'c': quit()

print('===== EXECUTION =====')
n = max(0,sum(st) - (crafts['essence_prism_crafting_item'] if 'essence_prism_crafting_item' in crafts else 0))
if n: 
    loc = j['user']['environment_type']
    if loc not in ['desert_oasis','lost_city','sand_dunes']: requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':j['user']['unique_hash'],'destination':'desert_oasis'},headers=post_headers,cookies=cookies)
    requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':j['user']['unique_hash'],'type':'essence_prism_crafting_item','quantity':n,'buy':1},headers=post_headers,cookies=cookies)
    print('bought %s essence prism'%n)
    if loc not in ['desert_oasis','lost_city','sand_dunes']: requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':j['user']['unique_hash'],'destination':loc},headers=post_headers,cookies=cookies)

if sum(hs[c] for c in rs): 
    for c in rs:
        if hs[c]:
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'uh':j['user']['unique_hash'],'item_type':'essence_%s_crafting_item'%c,'item_qty':hs[c]},headers=post_headers,cookies=cookies)
            print('hammered %s %s essence'%(hs[c],translate(c)))
    
if sum(st): 
    for c in range(8):
        if st[c]:
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',{'craftQty':st[c],'uh':j['user']['unique_hash'],'parts[essence_prism_crafting_item]':1,'parts[essence_%s_crafting_item]'%rs[c]:3},cookies=cookies,headers=post_headers)
            print('crafted %s %s essence'%(st[c],translate(rs[c+1])))

print('done!')