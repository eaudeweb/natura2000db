import urllib
from Products.Five.browser import BrowserView
from App.config import getConfiguration


_env = getConfiguration().environment
BACKEND_URL = _env.get('CHMRIO_BACKEND_URL').rstrip('/')


def get_backend_page(name, **kwargs):
    url = BACKEND_URL + name
    if kwargs:
        url += '?' + urllib.urlencode(kwargs.iteritems())

    f = urllib.urlopen(url)
    try:
        return f.read()
    finally:
        f.close()


class ChmRioFormsProxy(BrowserView):

    def __call__(self):
        # TODO view is not protected by ViewManagementScreens permission :(
        return get_backend_page('/')
