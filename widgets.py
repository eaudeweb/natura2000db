import flask
import jinja2
from flatland.out.markup import Tag, Generator


_default_settings = {
    'skip_labels': False,
    'widgets_template': 'edit',
}

class WidgetDispatcher(object):

    def __init__(self, jinja_env, context):
        self.jinja_env = jinja_env
        self.context = context

    def __call__(self, element):
        tmpl_name = 'widgets-%s.html' % self.context['widgets_template']
        tmpl = self.jinja_env.get_template(tmpl_name)
        widget_name = element.properties.get('widget', 'input')
        widget_macro = getattr(tmpl.module, widget_name)
        return widget_macro(element)


class MarkupGenerator(Generator):

    def __init__(self, jinja_env):
        super(MarkupGenerator, self).__init__('html')
        self._frames[-1].update(_default_settings)
        self.widget = WidgetDispatcher(jinja_env, self)

    def table_nested_th(self, table_field):
        html = "\n"

        level = lambda e: len(list(e.parents))

        table_depth = level(table_field)
        table_kids_depth = max([0] + [(level(e) - table_depth)
                                      for e in table_field.all_children])

        current_level = list(table_field.children)
        current_level_n = 0

        while current_level:
            next_level = []
            html += "<tr>"

            for field in current_level:
                kids_order = field.properties.get('order', [])
                kids = [field[name] for name in kids_order]
                if kids:
                    rowspan = 1
                else:
                    rowspan = table_kids_depth - current_level_n
                colspan = len(list(field.all_children))
                attr = ''
                if colspan > 1: attr += ' colspan="%d"' % colspan
                if rowspan > 1: attr += ' rowspan="%d"' % rowspan
                label = jinja2.escape(field.properties.get('label', ''))
                html += "<th%s>%s</th>" % (attr, label)
                next_level += kids

            current_level = next_level
            current_level_n += 1
            html += "</tr>\n"

        return jinja2.Markup(html)


def install_widgets(jinja_env):
    jinja_env.globals['form'] = MarkupGenerator(jinja_env)
