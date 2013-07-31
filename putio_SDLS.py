import putio
from DownloadStationAPI import DownloadStationAPI
import config
import logging

# add filemode="w" to overwrite
logging.basicConfig(level=logging.INFO)

logging.info('Put.io <> Synology Download Station Sync')
logging.info('---------------------------------')

client = putio.Client(config.OAUTH_TOKEN)
d = DownloadStationAPI(host=config.SYNOLOGY_URL, username=config.SYNOLOGY_USERNAME, password=config.SYNOLOGY_PASSWORD)

# list files
files = client.File.list(config.DOWNLOAD_DIR_ID)
current_downloads = d.get_status()
logging.info("Currently downloading: " + str(current_downloads['data']['total']))

if not files:
    logging.warning("No files to download!")

for f in files:
    download_status = True

    zip_url = 'https://api.put.io/v2/files/zip?oauth_token=' + config.OAUTH_TOKEN + '&file_ids=' + str(f.id)
    for download in current_downloads['data']['tasks']:
        if zip_url == download['additional']['detail']['uri']:
            logging.info(download['status'] + ": " + download['title'])
            download_status = False
            if download['status'] == 'finished':
                logging.info("Finished downloading: " + download['title'])
                logging.info("Deleting from put.io file id: " + str(f.id))
                f.delete()
    if download_status:
        logging.info("Adding file id: " + str(f.id))
        d.add_uri(zip_url)
