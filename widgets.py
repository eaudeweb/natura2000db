import flask
import jinja2
from flatland.out.markup import Tag, Generator


class WidgetDispatcher(object):

    def __init__(self, jinja_env, context):
        self.jinja_env = jinja_env
        self.context = context

    def __call__(self, element):
        tmpl_name = 'widgets-%s.html' % self.context['widgets_template']
        tmpl = self.jinja_env.get_template(tmpl_name)
        widget_name = element.properties.get('widget', 'input')
        widget_macro = getattr(tmpl.module, widget_name)
        return widget_macro(self.context, element)


class MarkupGenerator(Generator):

    _default_settings = {
        'skip_labels': False,
        'widgets_template': 'edit',
    }

    def __init__(self, jinja_env):
        super(MarkupGenerator, self).__init__('html')
        self._frames[-1].update(self._default_settings)
        self.widget = WidgetDispatcher(jinja_env, self)

    def is_hidden(self, field):
        return (field.properties.get('widget', 'input') == 'hidden')

    def table_nested_th(self, table_field):
        html = "\n"

        level = lambda e: len(list(e.parents))

        table_depth = level(table_field)
        table_kids_depth = max([0] + [(level(e) - table_depth)
                                      for e in table_field.all_children])

        current_level = [table_field[name] for name in
                         table_field.properties['order']
                         if not self.is_hidden(table_field[name])]
        current_level_n = 0

        while current_level:
            next_level = []
            html += "<tr>"

            for field in current_level:
                kids_order = field.properties.get('order', [])
                kids = [field[name] for name in kids_order
                        if not self.is_hidden(field[name])]
                if kids:
                    rowspan = 1
                else:
                    rowspan = table_kids_depth - current_level_n
                colspan = len([f for f in field.all_children
                               if not self.is_hidden(f)])
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


class SearchMarkupGenerator(MarkupGenerator):

    _default_settings = dict(MarkupGenerator._default_settings, **{
        'facets': [],
    })

    def url_for_search(self, search_form, **delta):
        search_data = search_form.value
        search_data.update(delta)
        search_data = dict((str(k), v) for k, v in search_data.items())
        return flask.url_for('webpages.search', **search_data)
