import flask
import jinja2
from flatland.out.markup import Tag, Generator
from flatland.schema import containers


class WidgetDispatcher(object):

    def __init__(self, jinja_env, context):
        self.jinja_env = jinja_env
        self.context = context

    def widget_name(self, element):
        if not element.properties.get('editable', True):
            if self.context['widgets_template'] == 'edit':
                return 'hidden'

        return element.properties.get('widget', 'input')

    def __call__(self, element, widget_name=None):
        tmpl_name = 'widgets-%s.html' % self.context['widgets_template']
        tmpl = self.jinja_env.get_template(tmpl_name)
        if widget_name is None:
            widget_name = self.widget_name(element)
        widget_macro = getattr(tmpl.module, widget_name)
        return widget_macro(self.context, element)


_auto = object()

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
        widget_name = self.widget.widget_name(field)
        return (widget_name == 'hidden')

    def virtual_child(self, list_element):
        slot_cls = list_element.slot_type
        member_template = slot_cls(name=u'NEW_LIST_ITEM',
                                   parent=list_element,
                                   element=list_element.member_schema())
        return member_template.element

    def colspan(self, field):
        return len([f for f in field.all_children if not self.is_hidden(f)])

    def order(self, field):
        if isinstance(field, containers.Mapping):
            return [kid.name for kid in field.field_schema]
        else:
            return []

    def table_nested_th(self, list_element):
        row = self.virtual_child(list_element)

        level = lambda e: len(list(e.parents))

        table_depth = level(row)
        table_kids_depth = max([0] + [(level(e) - table_depth)
                                      for e in row.all_children])

        current_level = [row[name] for name in self.order(row)
                         if not self.is_hidden(row[name])]
        current_level_n = 0

        html = "\n"

        while current_level:
            next_level = []
            html += "<tr>"

            for field in current_level:
                kids_order = self.order(field)
                kids = [field[name] for name in kids_order
                        if not self.is_hidden(field[name])]
                if kids:
                    rowspan = 1
                else:
                    rowspan = table_kids_depth - current_level_n
                colspan = self.colspan(field)
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

    def container_class(self, field):
        return field.properties.get('container_class', '')

    def sorted_with_labels(self, field):
        label = field.properties['value_labels'].get
        for value in sorted(field.valid_values, key=label):
            yield value, label(value)

    def any_value(self, field):
        if isinstance(field, dict):
            return any(self.any_value(child) for child in field.values())
        else:
            return not field.is_empty

    def linkify(self, field, value=_auto):
        if value is _auto:
            value = field.value

        if 'view_href' not in field.properties:
            return value
        else:
            return jinja2.Markup('<a href="%(url)s">%(value)s</a>' % {
                'url': jinja2.escape(field.properties['view_href'](field)),
                'value': jinja2.escape(value),
            })


class SearchMarkupGenerator(MarkupGenerator):

    _default_settings = dict(MarkupGenerator._default_settings, **{
        'view_name': 'webpages.search',
        'facets': [],
    })

    def url_for_search(self, search_form, view_name=None, **delta):
        if view_name is None:
            view_name = self['view_name']

        search_data = search_form.value
        search_data.update(delta)
        search_data = dict((str(k), v) for k, v in search_data.items())

        return flask.url_for(view_name, **search_data)
