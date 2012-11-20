import flask
import jinja2
import requests

from werkzeug.contrib.cache import SimpleCache

class ZopeTemplateLoader(jinja2.BaseLoader):

    def __init__(self, parent_loader, base_path,
                 cache_templates=True, template_list=[]):
        self.parent_loader = parent_loader
        self.cache = SimpleCache()
        self.cache_templates = cache_templates
        self.path = base_path
        self.template_list = template_list

    def get_source(self, environment, template):
        def passthrough(cachable=True):
            up = self.parent_loader
            source, path, uptodate = up.get_source(environment, template)
            if not cachable:
                uptodate = lambda: False
            return source, path, uptodate

        if not template in self.template_list:
            return passthrough()

        path = "%s%s" % (self.path, template)
        source = self.cache.get(path)
        if not source:
            try:
                response = requests.get(path)
            except requests.exceptions.ConnectionError:
                return passthrough(cachable=False)

            if response.status_code != 200:
                return passthrough(cachable=False)

            # escape jinja tags
            source = response.text
            source = source.strip()
            source = source.replace("{%", "{{ '{%' }}").replace("%}", "{{ '%}' }}")
            source = source.replace("{{", "{{ '{{' }}").replace("}}", "{{ '}}' }}")

            # template blocks
            source = source.replace("<!-- block_content -->",
                                    "{% block natura2000_content %}{% endblock %}")
            source = source.replace("<!-- block_head -->",
                                    "{% block head %}{% endblock %}")

            # fix breadcrumb link
            source = source.replace('"%s"' % self.path,
                                    '"%s"' % flask.url_for('naturasites.index'))

            if self.cache_templates:
                self.cache.set(path, source)

        return source, path, lambda: False
