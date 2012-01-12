# -*- coding: utf-8 -*-

import operator
import flask
import jinja2

import schema


available = {}
label = {}

def register_statistic(stat_label):
    def decorator(func):
        name = func.__name__
        available[name] = func
        label[name] = stat_label
        return func
    return decorator


class MissingFilterError(ValueError):
    """ A filter is missing from the search form """


def _nuts3_matcher(search_form):
    if not search_form['nuts3'].is_empty:
        search_nuts3 = search_form['nuts3'].value
        return lambda(code): (code == search_nuts3)

    elif not search_form['nuts2'].is_empty:
        search_nuts2 = search_form['nuts2'].value
        return lambda(code): code.startswith(search_nuts2)

    else:
        raise MissingFilterError(u"Trebuie selectată o regiune administrativă sau un judeţ pentru a vedea această statistică")


@register_statistic(u'Suprafata siturilor')
def area(search_form, search_answer):
    stat = {'table': [], 'total': 0}

    match_nuts3 = _nuts3_matcher(search_form)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        admin_area = 0
        for admin in data['section2']['administrative']:
            if match_nuts3(admin['code']):
                admin_area += total_area * (admin['coverage'] / 100)

        stat['total'] += admin_area
        stat['table'].append({
            'id': doc['id'],
            'name': doc['name'],
            'total_area': total_area,
            'admin_percent': admin['coverage'],
            'admin_area': admin_area,
        })

    stat['table'].sort(key=operator.itemgetter('admin_area'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_area.html', stat=stat))

@register_statistic(u'Suprafața siturilor CORINE')
def corine_area(search_form, search_answer):
    stat = {}
    for code in schema.corine_map.keys():
        stat['table_%s' % code] = []
        stat['total_%s' % code] = 0

    def match_corine(code):
        return schema.corine_map.has_key(code)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        corine_area = 0
        for code, coverage in data['section4']['characteristics']['habitat'].items():
            if match_corine(code) and coverage is not None:
                corine_area += total_area * (coverage / 100)
                stat['total_%s' % code] += corine_area
                stat['table_%s' % code].append({
                                            'id': doc['id'],
                                            'name': doc['name'],
                                            'total_area': total_area,
                                            'corine_percent': coverage,
                                            'corine_area': corine_area,
                                            })

    for code in schema.corine_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('corine_area'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_corine_area.html', 
                                                stat=stat, 
                                                corine_areas=schema.corine_map.items()))

@register_statistic(u'Suprafața ariilor protejate')
def protected_area(search_form, search_answer):
    stat = {}
    calculate = set()
    for code in schema.classification_map.keys():
        stat['table_%s' % code] = []
        stat['total_%s' % code] = 0
        calculate.add(code)

    if not search_form['protected_areas'].is_empty:
        calculate = set([search_form['protected_areas'].value])

    match_nuts3 = _nuts3_matcher(search_form)

    def match_protected(code):
        return schema.classification_map.has_key(code)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        protected_area = 0
        for area in data['section5']['classification']:
            if area['code'] not in calculate:
                continue

            if match_protected(area['code']) and area['percentage'] is not None:
                protected_area += total_area * (area['percentage'] / 100)
                stat['total_%s' % area['code']] += protected_area
                stat['table_%s' % area['code']].append({
                                            'id': doc['id'],
                                            'name': doc['name'],
                                            'total_area': total_area,
                                            'protected_percent': area['percentage'],
                                            'protected_area': protected_area,
                                            })

    for code in schema.classification_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('protected_area'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_protected_area.html', 
                                                stat=stat, 
                                                protected_areas=schema.classification_map.items()))

@register_statistic(u'Suprafața habitatelor')
def habitat_area(search_form, search_answer):
    stat = {}
    for code in schema.habitat_type_map.keys():
        stat['table_%s' % code] = []
        stat['total_%s' % code] = 0

    match_nuts3 = _nuts3_matcher(search_form)

    def match_habitat(code):
        return schema.habitat_type_map.has_key(code)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        habitat_area = 0
        for habitat in data['section3']['habitat']:
            if match_habitat(code) and habitat['percentage'] is not None:
                habitat_area += total_area * (habitat['percentage'] / 100)
                stat['total_%s' % habitat['code']] += habitat_area
                stat['table_%s' % habitat['code']].append({
                                            'id': doc['id'],
                                            'name': doc['name'],
                                            'total_area': total_area,
                                            'habitat_percent': habitat['percentage'],
                                            'habitat_area': habitat_area,
                                            })

    for code in schema.habitat_type_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('habitat_area'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_habitat_area.html', 
                                                stat=stat, 
                                                habitat_areas=schema.habitat_type_map.items()))

@register_statistic(u'Activități și consecințe în interiorul sitului')
def internal_antropic_activities(search_form, search_answer):
    stat = {}
    for code in schema.antropic_activities_map.keys():
        stat['table_%s' % code] = []

    match_nuts3 = _nuts3_matcher(search_form)

    def match_activity(code):
        return schema.antropic_activities_map.has_key(code)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        for activity in data['section6']['activity']['internal']:
            if match_activity(code) and activity['percentage'] is not None:
                stat['table_%s' % activity['code']].append({
                                            'id': doc['id'],
                                            'name': doc['name'],
                                            'total_area': total_area,
                                            'percentage': activity['percentage'],
                                            'intensity': activity['intensity'],
                                            'influence': activity['influence']
                                            })

    for code in schema.antropic_activities_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('percentage'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_internal_antropic_activities.html', 
                                                stat=stat, 
                                                activities=schema.antropic_activities_map.items()))

@register_statistic(u'Activități și consecințe în jurul sitului')
def external_antropic_activities(search_form, search_answer):
    stat = {}
    for code in schema.antropic_activities_map.keys():
        stat['table_%s' % code] = []

    match_nuts3 = _nuts3_matcher(search_form)

    def match_activity(code):
        return schema.antropic_activities_map.has_key(code)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        for activity in data['section6']['activity']['external']:
            if match_activity(code) and activity['percentage'] is not None:
                stat['table_%s' % activity['code']].append({
                                            'id': doc['id'],
                                            'name': doc['name'],
                                            'total_area': total_area,
                                            'percentage': activity['percentage'],
                                            'intensity': activity['intensity'],
                                            'influence': activity['influence']
                                            })

    for code in schema.antropic_activities_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('percentage'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_external_antropic_activities.html', 
                                                stat=stat, 
                                                activities=schema.antropic_activities_map.items()))


def compute(stat_form, search_answer):
    stat_name = stat_form['compute'].value

    if stat_name not in available:
        return jinja2.Markup(u"")

    stat = available[stat_name]

    try:
        html = stat(stat_form, search_answer)
    except MissingFilterError, e:
        html = flask.render_template('stat_error.html', msg=e.message)

    return jinja2.Markup(html)
