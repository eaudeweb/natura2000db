import urllib
from Products.Five.browser import BrowserView
from App.config import getConfiguration
from webob import Request
import paste.proxy


_env = getConfiguration().environment
BACKEND_URL = _env.get('CHMRIO_BACKEND_URL').rstrip('/')
proxy = paste.proxy.Proxy(BACKEND_URL + '/')


def get_backend_page(ctx, relative_url, headers,
                     post_data=None, content_type=None):
    my_relative_url = ctx.absolute_url(1)
    my_server_url = ctx.absolute_url()[:-len(my_relative_url)]

    headers.update({
        'X-Forwarded-For': my_server_url,
        'X-Scheme': 'http',
        'X-Script-Name': '/' + my_relative_url,
    })

    request = Request.blank(relative_url)
    for key, value in headers.iteritems():
        request.headers[key] = value

    if post_data is not None:
        request.method = 'POST'
        request.body = urllib.urlencode(post_data)

    if content_type is not None:
        request.content_type = content_type

    response = request.get_response(proxy)
    return response.status_int, dict(response.headerlist), response.body


class ChmRioFormsProxy(BrowserView):
    # TODO views are not protected by ViewManagementScreens permission :(

    def __call__(self):
        name = self.request.steps[-1]
        if name == 'index_html':
            name = ''
        query_string = self.request.QUERY_STRING

        headers = {
            'Cookie': self.request.HTTP_COOKIE,
        }

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
            content_type = self.request.CONTENT_TYPE

        else:
            post_data = None
            content_type = None

        (status, headers, body) = get_backend_page(
            self.aq_parent, relative_url, headers,
            post_data, content_type)

        response = self.request.RESPONSE
        response.setStatus(status)
        for name, value in headers.iteritems():
            response.setHeader(name, value)
        response.setBody(body)
