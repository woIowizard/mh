import argparse
p = argparse.ArgumentParser()
p.add_argument('-n',help='number of simulation rounds (default 1000)')
p.add_argument('-s',help='speed (default 1)')
p.add_argument('-y',help='sync/hunts left (default 40)')
p.add_argument('-i',help='siphon (default 5)')
p.add_argument('-t',help='starting step (default 0)')
p.add_argument('-T',action='store_true',help='turn on string stepping')
p.add_argument('-I',action='store_true',help='turn on super siphon')
p.add_argument('-U',action='store_true',help='turn on ultimate umbra')
p.add_argument('-C',action='store_true',help='use ultimate charm for non-eclipse')
p.add_argument('-F',action='store_true',help='use champion\'s fire for non-eclipse')
p.add_argument('-A',action='store_true',help='set TA attraction and n to 1')
p.add_argument('-Z',action='store_true',help='set TA attraction to 0')
p.add_argument('-b',help='target level (default 0)')
args = p.parse_args()

try: n = int(args.n); assert n
except: n = 1000
try: sp = int(args.s); assert sp
except: sp = 1
try: si = int(args.i); assert si
except: si = 5
try: hl = int(args.y); assert hl
except: hl = 40
try: st = int(args.t); assert st
except: st = 0
try: bm = int(args.b); assert bm
except: bm = 0

augs = []
if args.T: augs.append('string stepping')
if args.I: augs.append('super siphon')
if args.U: augs.append('ultimate umbra')
if args.F: augs.append('full champion\'s fire')
if args.C: augs.append('full ultimate charm')
if args.A: augs.append('full TA attraction'); n=1
elif args.Z: augs.append('no TA')

print('\n========== PARAMETERS ==========')
print('%s-round simulation of %s hunts beginning at step %s'%(n,hl if hl else sy,st))
print('speed: %s\nsiphon: %s'%(sp,si))
if augs: print('augs: %s'%', '.join(augs))

r = []
import random
def gs(n): return 20+((n-1)//8)*10 if n%8 else 1
def gf(n): 
	i,s = 1,0
	while s <= n: s+=gs(i);i+=1
	return i-1,s
	
for i in range(n):
	s,h = st,hl
	while h:
		g,h = gf(s),h-1
		if g[0]%8: 
			cr = 2 if args.C else (.78 if g[0] < 8 else .66 if g[0] < 16 else .61 if g[0] < 24 else .55) if args.U else (.92 if g[0] < 8 else .75 if g[0] < 16 else .7 if g[0] < 24 else .63)
			bfr = (.078 if g[0] < 8 else .1165 if g[0] < 16 else .1209 if g[0] < 24 else .1245) if args.U and not args.C else 0
			tar = 2 if args.A else 0 if args.Z else (.1826 if g[0] < 8 else .1103 if g[0] < 16 else .1002 if g[0] < 24 else .0818) if args.U else (.2253 if g[0] < 8 else .1352 if g[0] < 16 else .1246 if g[0] < 24 else .106)
			ad = 2*sp*(1+args.T)+args.F if random.random() < tar else -10 if random.random() < bfr else sp+args.F if random.random() < cr else 0
		else: ad = sp+1; h += si*(1+args.I)
		if ad: 
			if gf(s+ad)[0]//8 > gf(s)[0]//8: s = sum(gs(j) for j in range(1,gf(s+ad)[0]//8*8))
			elif gf(s+ad)[0] < gf(s)[0]: s = sum(gs(j) for j in range(1,gf(s)[0]))
			else: s += ad
	r.append(s)
	
print('\n========== RESULTS ==========')
l = gf(sum(r)//len(r))[0]
print('best:\t%s steps (level %s)'%(max(r),gf(max(r))[0]))
print('ave:\t%s steps (level %s)'%(sum(r)//len(r),l))
print('worst:\t%s steps (level %s)\n'%(min(r),gf(min(r))[0]))
r = list(map(lambda x:gf(x)[0],r))
d = {i:r.count(i) for i in set(r)}
if bm: e=sum(d[i] for i in d if i>=bm);print('level %s+: %s runs (%s%%)'%(bm,e,round(e/n*100,2)))
else: [print('level %s: %s runs (%s%%)'%(i,d[i],round(d[i]/n*100,2))) for i in sorted(list(d))[::-1]]
print('')