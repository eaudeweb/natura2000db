HTTP_PROXIED = True
HTTP_CHERRYPY = True

import logging.handlers
error_log = logging.handlers.WatchedFileHandler('%(instance_var)s/error.log')
error_log.setLevel(logging.WARN)
logging.getLogger().addHandler(error_log)
