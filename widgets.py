class WidgetDispatcher(object):

    def __init__(self, jinja_env):
        self.jinja_env = jinja_env

    def __call__(self, element, **kwargs):
        tmpl = self.jinja_env.get_template('widgets.html')
        widget_name = element.properties.get('widget', 'input')
        widget_impl = getattr(tmpl.module, widget_name)
        return widget_impl(element, **kwargs)
