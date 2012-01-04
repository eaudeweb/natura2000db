import flask
import jinja2
from flatland.out.markup import Tag, Generator


class WidgetDispatcher(object):

    def __init__(self, jinja_env, context):
        self.jinja_env = jinja_env
        self.context = context

    def __call__(self, element, default_widget='input'):
        tmpl_name = 'widgets-%s.html' % self.context['widgets_template']
        tmpl = self.jinja_env.get_template(tmpl_name)
        widget_name = element.properties.get('widget', default_widget)
        widget_macro = getattr(tmpl.module, widget_name)
        return widget_macro(self.context, element)


class MarkupGenerator(Generator):

    _default_settings = {
        'skip_labels': False,
        'widgets_template': 'edit',
        'auto_domid': True,
        'auto_for': True,
    }

    def __init__(self, jinja_env):
        super(MarkupGenerator, self).__init__('html')
        self._frames[-1].update(self._default_settings)
        self.widget = WidgetDispatcher(jinja_env, self)

    def is_hidden(self, field):
        return (field.properties.get('widget', 'input') == 'hidden')

    def table_virtual_child(self, list_element):
        slot_cls = list_element.slot_type
        member_template = slot_cls(name=u'NEW_LIST_ITEM',
                                   parent=list_element,
                                   element=list_element.member_schema())
        return member_template.element

    def table_nested_th(self, list_element):
        row = self.table_virtual_child(list_element)

        level = lambda e: len(list(e.parents))

        table_depth = level(row)
        table_kids_depth = max([0] + [(level(e) - table_depth)
                                      for e in row.all_children])

        current_level = [row[name] for name in
                         row.properties['order']
                         if not self.is_hidden(row[name])]
        current_level_n = 0

        html = "\n"

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

    def table_append(self, list_element):
        virtual_element = self.table_virtual_child(list_element)
        return self.widget(virtual_element, 'table_td')


class SearchMarkupGenerator(MarkupGenerator):

    _default_settings = dict(MarkupGenerator._default_settings, **{
        'search_view': 'webpages.search',
        'facets': [],
    })

    def url_for_search(self, search_form, **delta):
        search_data = search_form.value
        search_data.update(delta)
        search_data = dict((str(k), v) for k, v in search_data.items())
        return flask.url_for(self['search_view'], **search_data)


class StatsMarkupGenerator(SearchMarkupGenerator):

    _default_settings = dict(SearchMarkupGenerator._default_settings, **{
        'search_view': 'webpages.stats',
        'compute': None,
    })

    def url_for_search(self, search_form, **delta):
        if self['compute'] is not None:
            delta['compute'] = self['compute']
        sup = super(StatsMarkupGenerator, self).url_for_search
        return sup(search_form, **delta)
