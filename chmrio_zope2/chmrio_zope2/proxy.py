import urllib, urllib2
from Products.Five.browser import BrowserView
from App.config import getConfiguration


_env = getConfiguration().environment
BACKEND_URL = _env.get('CHMRIO_BACKEND_URL').rstrip('/')


def get_backend_page(ctx, name, **kwargs):
    url = BACKEND_URL + name
    if kwargs:
        url += '?' + urllib.urlencode(kwargs.iteritems())

    my_relative_url = ctx.absolute_url(1)
    my_server_url = ctx.absolute_url()[:-len(my_relative_url)]

    request = urllib2.Request(url, headers={
        'X-Forwarded-For': my_server_url,
        'X-Scheme': 'http',
        'X-Script-Name': '/' + my_relative_url,
    })

    f = urllib2.urlopen(request)
    try:
        return f.read()
    finally:
        f.close()


class ChmRioFormsProxy(BrowserView):

    def __call__(self):
        # TODO view is not protected by ViewManagementScreens permission :(
        return get_backend_page(self.aq_parent, '/')
