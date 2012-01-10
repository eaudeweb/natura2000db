import urllib
import re
from Products.Five.browser import BrowserView
from App.config import getConfiguration
from AccessControl import Unauthorized
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from webob import Request
import paste.proxy
import lxml.html.soupparser
from lxml.cssselect import CSSSelector


_env = getConfiguration().environment
BACKEND_URL = _env.get('CHMRIO_BACKEND_URL').rstrip('/')
proxy = paste.proxy.Proxy(BACKEND_URL + '/')

frame_zpt = PageTemplateFile('frame.zpt', globals())


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


def _css_iter(tree, selector):
    return CSSSelector(selector)(tree)


_res_pattern = re.compile(r'(?<=^var R = {assets: ")'
                          r'[^"]*'
                          r'(?="};$)')

def fix_resource_link(script_tag, zope_link):
    flask_link = _res_pattern.search(script_tag.text).group(0)
    script_tag.text = _res_pattern.sub(script_tag.text, zope_link)
    return flask_link

def reframe_html(html, site):
    doc = lxml.html.soupparser.fromstring(html)

    zope_link = site.absolute_url() + '/++resource++chmrio_zope2/'
    script_tag = _css_iter(doc, 'script.link-to-static')[0]
    flask_link = fix_resource_link(script_tag, zope_link)

    for e in list(_css_iter(doc, 'head title')):
        e.getparent().remove(e)

    def translated_elements_in(selector):
        for selected in _css_iter(doc, selector):
            for e in _css_iter(selected, 'script[src], img[src]'):
                url = e.attrib['src']
                if url.startswith(flask_link):
                    e.attrib['src'] = zope_link + url[len(flask_link):]
            for e in _css_iter(selected, 'link[href], a[href]'):
                url = e.attrib['href']
                if url.startswith(flask_link):
                    e.attrib['href'] = zope_link + url[len(flask_link):]

            for e in selected:
                yield e

    def fetch(selector):
        elements = translated_elements_in(selector)
        html = u' '.join(lxml.html.tostring(e) for e in elements)
        return html.strip()

    options = {
        'head': fetch('head'),
        'body': fetch('body'),
    }
    return frame_zpt.__of__(site)(**options)


class ChmRioFormsProxy(BrowserView):

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

        return reframe_html(body, self.aq_parent.getSite())



class ChmRioFormsProxyEdit(ChmRioFormsProxy):
    """
    Subclass of ChmRioFormsProxy that only allows Manager access
    (hack because zope 2.10 ignores the `permission` option
    of `browser:view`)
    """

    def __call__(self):
        user = self.request.AUTHENTICATED_USER
        if not user.has_permission(view_management_screens, self):
            raise Unauthorized
        return ChmRioFormsProxy.__call__(self)
