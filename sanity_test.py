import sys
import os
import glob


sys.dont_write_bytecode = True
os.environ['PYTHON_EGG_CACHE'] = '/tmp/'
any(sys.path.insert(0, x) for x in glob.glob('./packages/*.egg') if x not in sys.path)

import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')

import socket
import json
import urllib2
import cStringIO
import zipfile
import json


import util

UPDATESERVER_ADDRESS = os.environ.get('UPDATESERVER', '%s:80' % (socket.gethostname()))

oldbuild = ('8.0.0.56336', '13.18.1405')
newbuild = ('8.0.0.56416', '13.19.1410')

def setup_module():
    "set up test fixtures"
    util.setScriptPath(__file__)
    #prepare data
    cpCmd = 'cp -rf %s/* %s/origin' % (util.datadir(), WWW_ROOT)
    subprocess.call(['sh', '-c', cpCmd])

def test_get_apk():
    for jsonfile in glob.glob('get_apk.json'):
        logging.debug('post %r to %r', jsonfile, urlOfUpdate(UPDATESERVER_ADDRESS))
        with open(jsonfile, 'rb') as fp:
            data = fp.read()
        try:
            r = util.UpdateRequest.fromJSON(data)
            r.app_version = oldbuild[0]
            response = urllib2.urlopen(urlOfUpdate(UPDATESERVER_ADDRESS), data=r.toJSON())
        except urllib2.HTTPError as e:
            response = e
        data = response.read()
        logging.info('response.code=%r jsonfile=%r urlOfUpdate=%r', response.code, jsonfile, urlOfUpdate(UPDATESERVER_ADDRESS))
        if response.code not in (200, 403):
            raise ValueError('updateserver must return (200, 403), data=%r', data)
        if response.code == 200:
            json_data = json.loads(data)
            logging.info('reponse=%r', json.dumps(json_data, indent=2))
            f = json_data['file'][0]['url']
##            logging.info('get new apk from %r', f)
            response = urllib2.urlopen(f)
            data = response.read()
            logging.info('response.code=%r oupeng.apk length=%r url=%r', response.code, len(data), f)
            zfile = zipfile.ZipFile(cStringIO.StringIO(data), 'r')
            namelist = zfile.namelist()
            assert all(x in namelist for x in ('AndroidManifest.xml', 'classes.dex'))
            AndroidManifest = zfile.read('AndroidManifest.xml')
            assert len(AndroidManifest) > 0
            logging.info('DownloadPASS!')

def test_get_core():
    for jsonfile in glob.glob('get_core.json'):
        logging.debug('post %r to %r', jsonfile, urlOfUpdate(UPDATESERVER_ADDRESS))
        with open(jsonfile, 'rb') as fp:
            data = fp.read()
        try:
            response = urllib2.urlopen(urlOfUpdate, data=data)
        except urllib2.HTTPError as e:
            response = e
        data = response.read()
        logging.info('response.code=%r jsonfile=%r apiserver=%r', response.code, jsonfile, urlOfUpdate(UPDATESERVER_ADDRESS))
        if response.code not in (200, 403):
            raise ValueError('updateserver must return (200, 403), data=%r', data)
        if response.code == 200:
            json_data = json.loads(data)
            logging.info('reponse=%r', json.dumps(json_data, indent=2))
            f = json_data['file'][0]['url']
##            logging.info('get core file from %r', f)
            response = urllib2.urlopen(f)
            data = response.read()
            logging.info('response.code=%r core file length=%r url=%r', response.code, len(data), f)
            zfile = zipfile.ZipFile(cStringIO.StringIO(data), 'r')
            namelist = zfile.namelist()
            assert all(x in namelist for x in ('library.json', 'libopera.so', 'opera.pak'))
            library_info = json.loads(zfile.read('library.json'))
            assert 'version' in library_info
            logging.info('PASS!')

def test_get_full():
    for jsonfile in glob.glob('get_full.json'):
        logging.debug('post %r to %r', jsonfile, urlOfUpdate)
        with open(jsonfile, 'rb') as fp:
            data = fp.read()
        try:
            response = urllib2.urlopen(urlOfUpdate(UPDATESERVER_ADDRESS), data=data)
        except urllib2.HTTPError as e:
            response = e
        data = response.read()
        logging.info('response.code=%r jsonfile=%r apiserver=%r', response.code, jsonfile, urlOfUpdate(UPDATESERVER_ADDRESS))
        if response.code not in (200, 403):
            raise ValueError('updateserver must return (200, 403), data=%r', data)
        if response.code == 200:
            json_data = json.loads(data)
            logging.info('reponse=%r', json.dumps(json_data, indent=2))
            f = json_data['fullfile']
            f1 = json_data['file'][0]['name']
            f2 = json_data['file'][1]['name']
            logging.info('get full file from %r', f)
            logging.info('expected file list is from %r', [f1,f2])
            response = urllib2.urlopen(f)
            data = response.read()
            logging.info('response.code=%r full file length=%r url=%r', response.code, len(data), f)
            zfile = zipfile.ZipFile(cStringIO.StringIO(data), 'r')
            namelist = zfile.namelist()
            logging.info('namelist=%s', namelist)
            assert all(x in namelist for x in (f1, f2))
            logging.info('PASS!')

