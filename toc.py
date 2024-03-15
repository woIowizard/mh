import argparse
p = argparse.ArgumentParser()
p.add_argument('-m',help='MW CR (default .2165)')
p.add_argument('-b',help='BG CR (default .3761)')
p.add_argument('-w',help='target words (0 to calculate expected vols)')
p.add_argument('-l',help='hunts left (0 to calculate expected hunts)')
p.add_argument('-C',action='store_true',help='condensed creativity')
p.add_argument('-S',action='store_true',help='silver quill')
p.add_argument('-G',action='store_true',help='golden quill')
args = p.parse_args()

try: w = int(args.w); assert w >= 0
except: w = 0
try: h = int(args.l); assert h >= 0
except: h = 0
try: assert w+h
except: print('ERROR: at least one of w and l must be positive'); quit()
try: m_prob = float(args.m); assert m_prob >= 0 and m_prob <= 1
except: m_prob = .2165
try: b_prob = float(args.b); assert b_prob >= 0 and b_prob <= 1
except: b_prob = .3761
if m_prob + b_prob > 1: print('ERROR: sum of CR > 1'); quit()

augs = []
if args.C: augs.append('condensed creativity')
if args.S: augs.append('silver quill')
if args.G: augs.append('golden quill')

print('\n========== PARAMETERS ==========')
print('MW CR: %s'%m_prob)
print('BG CR: %s'%b_prob)
print('augments: %s'%(', '.join(augs) if augs else None))

cache = {}
def c(w,h): 
	global cache
	if (w,h) in cache: return cache[(w,h)]
	if w <= 0: return 1  
	if not h: return 0 
	a = m_prob*c(w-1000*(1+args.C)*(1+.5*args.G)*(1+.25*args.S),h+1) + b_prob*c(w-250*(1+args.C)*(1+.5*args.G)*(1+.25*args.S),h-1) + (1-m_prob-b_prob)*c(w,h-1)
	cache[(w,h)] = a
	return a

if not w: 
	print('\n========== VOLS IN %s HUNTS =========='%h)
	i,p,e = 1,c(4000,h),0
	while p > .0001: 
		print('%s:\t%s'%(i,p))
		e,i = e+p,i+1
		p = c(4000*i,h)
	print('\nexpected vols: %s\n'%e)
elif not h:
	print('\n========== HUNTS FOR %s WORDS =========='%w)
	i,p,e = 1,c(w,1),0
	while p < .99: 
		print('%s:\t%s'%(i,p))
		e,i = e+1-p,i+1
		p = c(w,i)
	print('\nexpected hunts: %s\n'%e)
else: print('\nprob of %s words in %s hunts: %s\n'%(w,h,c(w,h)))
	
	