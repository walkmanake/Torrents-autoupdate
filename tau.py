# -*- coding: utf-8 -*-
'''
Autoupdate torrents
'''
import time
import urllib2
from shutil import move
from os import remove
from urllib import urlencode
from binascii import b2a_hex as bta, a2b_hex as atb

from lxml.html import document_fromstring as doc
from bencode import bdecode, bencode
from httplib2 import Http

http = Http()
username = 'username'
password = 'password'
ut_port = '12345'
ut_username = 'utusername'
ut_password = 'utpassword'
site = 'http://example.com/'
scrape_body = site + 'scrape.php?info_hash='  # URL scrape-запроса.
login_url = site + 'takelogin.php'
torrent_body = site + 'download.php?id={0}&name={0}.torrent'
announce = site + 'announce.php?'  # URL анонса трекера.
webui_url = 'http://127.0.0.1:{0}/gui/'.format(ut_port)
webui_token = webui_url + 'token.html'
swOn = 5
swOff = 2
#ut-fake headers, need for scrape request, browsers user-agent will banned
uthead = {'User-Agent':'uTorrent/2210(21304)'}
# Path to uTorrent's files folder (need to get a resume.dat)
sys_torrent_path = 'C:/Program Files/uTorrent'
# Path to folder with .torrent files
torrent_path = 'c:/torrents/'
# Path to autoload folder of uTorrent
autoload_path = 'c:/torrents/autoload'
swOn = 5
swOff = 2
sleeping = 300

def authentication(username, password):
    ''' Authorization for the site and return cookies. '''
    
    data = {'username': username, 'password': password}
    headers = {'Content-type': 'application/x-www-form-urlencoded' ,
    'User-agent':'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6'}
    resp, login = http.request(loginUrl, 'POST', headers=headers, body=urlencode(data))
    cookiekeys = ['uid', 'pass', 'PHPSESSID', 'pass_hash', 'session_id']
    split_resp = resp['set-cookie'].split(' ')
    lst = []
    for split_res in split_resp:
        if split_res.split('=')[0] in cookiekeys:
            lst.append(split_res)
    cookie = ' '.join(lst)
    return {'Cookie': cookie}

def torrentDict(torr_path):
    ''' Get a dict "name":"hash" from resume.dat. '''

    Dict = {}
    with open(u'{0}/resume.dat'.format(torr_path), 'rb') as resume:
        t = bdecode(resume.read())
    for name in t:
        if name != '.fileguard' and name != 'rec':
            for tracker in t[name]['trackers']:
                if isinstance(tracker, str) and tracker.startswith(announce):
                    Dict[name.lstrip('torrent\\')] = bta(t[name]['info'])
    return Dict


def uTWebUI(ut_name, ut_passw):
    ''' Get a uTorrent's WebUI password and token. '''
    
    passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passmgr.add_password(None, webui_token, uTname, uTpassw)
    authhandler = urllib2.HTTPBasicAuthHandler(passmgr)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    req = urllib2.Request(webui_token)
    tkp = urllib2.urlopen(req)
    page = tkp.read()
    token = doc(page).xpath('//text()')[0]

    passw = req.unredirected_hdrs['Authorization']
    return passw, token

def webuiActions(torrent_hash, action, pw, token):
    ''' uTorrent WebUI actions. '''

    head = {'Authorization': pw}
    if action == 'remove':
        action_req = '?token={0}&action=remove&hash={1}'.format(token, torrent_hash)
        r, act = http.request(webui_url+action_req, headers=head)


#main cycle
while swOn > swOff:
    print 'Cycle'
    startTime = time.time()
    main_dict = torrentDict(sys_torrent_path)
    delay = sleeping*0.8/len(main_dict)
    for key in main_dict:
        lst = []
        scrpReq = ''
        for i in range(0, len(main_dict[key]), 2):
            lst.append('%{0}'.format(main_dict[key][i:i+2].upper()))
        resp, scrp = http.request('{0}{1}'.format(scrape_body, scrpReq), 'GET', headers=uthead)
        if scrp == 'd5:filesdee':
            print 'File {0} not register on the tracker'.format(key.rstrip('.torrent'))
            try:
                with open('{0}/{1}'.format(torrent_path, key), 'rb') as torrent_file:
                    torrent = bdecode(trrFile.read())
                    t_id = t['comment'][36:]
                brhead = authentication(username, password)
                resp, torrent = http.request(torrBody.format(t_id), 'GET', headers=brhead)
                with open('{0}.torrent'.format(t_id),'wb') as torrent_file:
                    torrent_file.write(torrent)
                # Remove the old file and move new file to a autoload folder
                remove('{0}/{1}'.format(torrent_path, key))
                move('{0}.torrent'.format(t_id), '{0}/{1}.torrent'.format(autoload_path,t_id))
                print 'Torrent was updated'
            except IOError:
                pass
            try:
                # if WebUI is on
                authkey, token = uTWebUI(ut_username, ut_password)
                webuiActions(main_dict[key], 'remove', authkey, token)
            except:
                pass
    time.sleep(delay)
    print 'Total: {0}'.format(time.time() - startTime)
    time.sleep(sleeping*0.2)