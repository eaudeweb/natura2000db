import flask
from flatland.out.markup import Tag, Generator


_default_settings = {
    'skip_labels': False,
}

class WidgetDispatcher(object):

    def __init__(self, jinja_env):
        self.jinja_env = jinja_env

    def __call__(self, element):
        tmpl = self.jinja_env.get_template('widgets-edit.html')
        widget_name = element.properties.get('widget', 'input')
        widget_macro = getattr(tmpl.module, widget_name)
        return widget_macro(element)


class MarkupGenerator(Generator):

    def __init__(self, jinja_env):
        super(MarkupGenerator, self).__init__('html')
        self._frames[-1].update(_default_settings)
        self.widget = WidgetDispatcher(jinja_env)


def install_widgets(jinja_env):
    jinja_env.globals['form'] = MarkupGenerator(jinja_env)
