import jinja2
import requests

from werkzeug.contrib.cache import SimpleCache

class ZopeTemplateLoader(jinja2.BaseLoader):

    def __init__(self, base_path, cache_templates=True, template_list=[]):
        self.cache = SimpleCache()
        self.cache_templates = cache_templates
        self.path = base_path
        self.template_list = template_list

    def get_source(self, environment, template):
        if not template in self.template_list:
            raise jinja2.TemplateNotFound(template)

        path = "%s%s" % (self.path, template)
        source = self.cache.get(path)
        if not source:
            response = requests.get(path)
            if response.status_code != 200:
                raise jinja2.TemplateNotFound(template)

            # escape jinja tags
            source = response.text
            source = source.strip()
            source = source.replace("{{", "{{ '{{' }}").replace("}}", "{{ '}}' }}")
            source = source.replace("<!-- block_content -->", "{% block content %}{% endblock %}")

            if self.cache_templates:
                self.cache.set(path, source)

        return source, path, lambda: False
