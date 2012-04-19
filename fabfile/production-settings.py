import logging.handlers
from path import path

instance_path = path(__file__).parent


error_log = logging.handlers.WatchedFileHandler(instance_path/'error.log')
error_log.setLevel(logging.WARN)
logging.getLogger().addHandler(error_log)


secret_key_path = instance_path/'secret_key.txt'
if secret_key_path.isfile():
    SECRET_KEY = secret_key_path.text().strip()


HTTP_PROXIED = True
HTTP_CHERRYPY = True
HTTP_LISTEN_PORT = 26887
ZOPE_TEMPLATE_PATH = 'http://biodiversitate.mmediu.ro/rio/natura2000_templates/'
ZOPE_TEMPLATE_CACHE = True


STATIC_URL_MAP = {
    '/static/tiles': instance_path.parent/'data'/'tiles',
    '/static/pdf': instance_path.parent/'data'/'pdf',
}

PDF_URL = 'http://biodiversitate.mmediu.ro/rio/natura2000/static/pdf/'
TILES_URL_TEMPLATE = 'http://biodiversitate.mmediu.ro/rio/natura2000/static/tiles/%(name)s/${z}/${x}/${y}.png'


GOOGLE_MAPS = True
