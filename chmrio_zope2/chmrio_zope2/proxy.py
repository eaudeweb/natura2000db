import urllib, urllib2
from Products.Five.browser import BrowserView
from App.config import getConfiguration


_env = getConfiguration().environment
BACKEND_URL = _env.get('CHMRIO_BACKEND_URL').rstrip('/')


def get_backend_page(ctx, relative_url, post_data=None):
    url = BACKEND_URL + relative_url

    my_relative_url = ctx.absolute_url(1)
    my_server_url = ctx.absolute_url()[:-len(my_relative_url)]

    headers = {
        'X-Forwarded-For': my_server_url,
        'X-Scheme': 'http',
        'X-Script-Name': '/' + my_relative_url,
    }

    request = urllib2.Request(url, post_data, headers)

    if post_data is not None:
        request.add_data(urllib.urlencode(post_data))

    f = urllib2.urlopen(request)
    try:
        return f.code, dict(f.headers), f.read()
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

        if self.request.REQUEST_METHOD == 'POST':
            post_data = []
            for key, value in self.request.form.iteritems():
                if key == '-C':
                    continue

                if isinstance(value, list):
                    for subvalue in value:
                        post_data.append((key, subvalue))
                else:
                    post_data.append((key, str(value)))

        else:
            post_data = None

        (status, headers, body) = get_backend_page(
            self.aq_parent, relative_url, post_data)

        response = self.request.RESPONSE
        response.setStatus(status)
        for name, value in headers.iteritems():
            response.setHeader(name, value)
        response.setBody(body)
