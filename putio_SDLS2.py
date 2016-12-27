import logging
import sys
# add filemode="w" to overwrite
logging.basicConfig(format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S",level=logging.INFO,stream=sys.stdout)


import putio
from DownloadStationAPI import DownloadStationAPI
import config
import time
from datetime import datetime, timedelta
import re
import redis
import json

logging.info('Put.io <> Synology Download Station Sync')
logging.info('---------------------------------')

client = putio.Client(config.OAUTH_TOKEN)
d = DownloadStationAPI(host=config.SYNOLOGY_URL, username=config.SYNOLOGY_USERNAME, password=config.SYNOLOGY_PASSWORD)

# list files
files = client.File.list(config.DOWNLOAD_DIR_ID)
current_downloads = d.get_status()
#parsed = json.loads(current_downloads)
logging.info( json.dumps(current_downloads, indent=4, sort_keys=True))
logging.info("Currently downloading: " + str(current_downloads['data']['total']))
p = re.compile('^.*file_ids=(?P<id>[0-9]+)$')
zipIdPattern  = re.compile('.*zipstream/(?P<zid>[0-9]+)\.zip.*$')
putioUrl = re.compile('.*put\.io/v2/files/(?P<fileid>[0-9]+)/download.*')
# delete file on put.io if transfered
for download in current_downloads['data']['tasks']:
       if download['status'] == 'finished':
       # if zip file
           isZip = re.match(zipIdPattern,download['additional']['detail']['uri'])
           isPutio = re.match(putioUrl,download['additional']['detail']['uri'])
           if isZip:
               zip_id = isZip.group(1)
               logging.info("ZIp id {}".format(zip_id))
               zip_info= {}
               zip_info = client.File.zipInfo(int(zip_id))
               logging.info( zip_info)
               for zipped_file in zip_info['missing_files']:
                   try: 
                       Client.File.get(int(zipped_file['id'])).delete()
                   except Exception:
                       logging.error('Error while deleting file in put.io %s' % zipped_file['id'])
                   d.delete(download['id'])
           #TODO manage no put.io file
           #elif isPutio:
            

#check put.io side now           
if not files:
    logging.info("No files to download!")
for f in files:
    download_status = True
    zip_url = client.File.createZip(f.id)
    for download in current_downloads['data']['tasks']:
        # if zip file
        if download['status'] != 'finished':
            isZip = re.match(zipIdPattern,download['additional']['detail']['uri'])
            if isZip:
                zip_id = isZip.group(1)
                logging.info("ZIp id {}".format(zip_id))
                zip_info = client.File.zipInfo(int(zip_id))
                logging.info( zip_info)
                for zipped_file in zip_info['missing_files']:
                    if zipped_file['id'] == f.id:
                        download_status = False
                        break

#        if zip_url == download['additional']['detail']['uri']:
#            logging.info(download['status'] + ": " + download['title'])
#            logging.info("Transfert found on Synology: no download " ) 
#            download_status = False
#            if download['status'] == 'finished':
#                logging.info("Finished downloading: " + download['title'])
#                logging.info("Deleting from put.io file id: " + str(f.id))
#                f.delete()
    if download_status:
        logging.info("Adding file id: " + str(f.id))
        d.add_uri(zip_url)
