import logging
import sys
logging.basicConfig(format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S",level=logging.INFO,stream=sys.stdout)

from os import listdir
import os
from os.path import isfile, join
import putio
import config


logging.info('Synology Download Station Sync <> Put.io')
logging.info('---------------------------------')
client = putio.Client(config.OAUTH_TOKEN)
for f in listdir(config.INPUT_FOLDER):
    path = join(config.INPUT_FOLDER, f)
    logging.info(path)
    if isfile(path):
        # logging.info(f)
        try:
            r = client.Transfer.add_torrent(path,parent_id=config.DOWNLOAD_DIR_ID,extract=True)
            os.remove(path)
        except Exception as e:
            logging.error("Error while uploading file to put.io")
            raise
