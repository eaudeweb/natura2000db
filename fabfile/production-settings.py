HTTP_PROXIED = True
HTTP_CHERRYPY = True
ZOPE_TEMPLATE_PATH = 'http://biodiversitate.mmediu.ro/rio/natura2000_templates/frame.html'

import logging.handlers
error_log = logging.handlers.WatchedFileHandler('%(instance_var)s/error.log')
error_log.setLevel(logging.WARN)
logging.getLogger().addHandler(error_log)
