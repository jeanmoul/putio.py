import logging
import sys
# add filemode="w" to overwrite
logging.basicConfig(format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S",level=logging.DEBUG,stream=sys.stdout)


import putio
from DownloadStationAPI import DownloadStationAPI
import config
import time
from datetime import datetime, timedelta
import re
import redis

logging.info('Put.io <> Synology Download Station Sync')
logging.info('---------------------------------')

client = putio.Client(config.OAUTH_TOKEN)
d = DownloadStationAPI(host=config.SYNOLOGY_URL, username=config.SYNOLOGY_USERNAME, password=config.SYNOLOGY_PASSWORD)

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# list files
files = client.File.list(config.DOWNLOAD_DIR_ID)
current_downloads = d.get_status()
logging.info("Currently downloading: " + str(current_downloads['data']['total']))
p = re.compile('^.*file_ids=(?P<id>[0-9]+)$')
zipIdPattern  = re.compile('.*zipstream/(?P<zid>[0-9]+)\.zip.*$')

if not files:
    logging.info("No files to download!")

for f in files:
    download_status = True
    sub_url = 'https://api.put.io/v2/files/' + str(f.id)+ '/subtitles/default?oauth_token=' + config.OAUTH_TOKEN
    #logging.debug('match  %s', mathzip_id.group( 'zid'))
    
    for key in r.sscan_iter():
         # TODO add one more loop for several file per zip
        if f.id == r.get(key):
            logging.info('File %s already present, no need to Download', f.name)
            download_status = False
            
            

    
    for download in current_downloads['data']['tasks']:
       # TODO check the file id instead of the whole url
       #logging.info('url: %s',  download['additional']['detail']['uri']   )
       #m =  p.match(download['additional']['detail']['uri'])
       #logging.info('m: %s', str(m))
       #id = m.group('id')
       #logging.info('match : %s == %d ', str(id),f.id)
       if f.id == int(p.match(download['additional']['detail']['uri']).group('id')):
           logging.info('File %s already present, no need to Download', f.name)
           download_status = False
           downloadTimestamp = float(download['additional']['detail']['create_time'])
           downloadDate = datetime.fromtimestamp(downloadTimestamp)
           #logging.info(str(downloadTimestamp)  + " " + str(downloadDate))
           #logging.info(str(timedelta(days=10)))
           #maxDate = downloadDate + timedelta(days=10)
           #logging.info(str(maxDate))
           if (download['status'] == 'finished') and (downloadDate  + timedelta(days=16) < datetime.utcnow()):
                logging.info("Finished downloading: " + download['title'])
                logging.info("Deleting from put.io file id: " + str(f.id))
                logging.info("download has 16")
                f.delete()
                d.delete(download['id'])
    if download_status:
        zip_url = client.File.createZip(f.id)
        zip_id=int(zipIdPattern.match(zip_url).group('zid'))
        r.sadd(zip_id,f.id)
        logging.info("Adding file id: " + str(f.id)+ " " + zip_url)
        logging.info(d.add_uri(zip_url))
