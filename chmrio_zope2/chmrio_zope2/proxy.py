import urllib, urllib2
from Products.Five.browser import BrowserView
from App.config import getConfiguration


_env = getConfiguration().environment
BACKEND_URL = _env.get('CHMRIO_BACKEND_URL').rstrip('/')


def get_backend_page(ctx, relative_url):
    url = BACKEND_URL + relative_url

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
    # TODO views are not protected by ViewManagementScreens permission :(

    def __call__(self):
        name = self.request.steps[-1]
        if name == 'index_html':
            name = ''
        query_string = self.request.QUERY_STRING

        relative_url = '/' + name
        if query_string:
            relative_url += '?' + query_string

        return get_backend_page(self.aq_parent, relative_url)
