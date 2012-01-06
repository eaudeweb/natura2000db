import operator
import flask
import jinja2

from schema import habitat_class_map, classification_map

def area(search_form, search_answer):
    stat = {'table': [], 'total': 0}

    if not search_form['nuts3'].is_empty:
        search_nuts3 = search_form['nuts3'].value
        def match_nuts3(code):
            return (code == search_nuts3)

    elif not search_form['nuts2'].is_empty:
        search_nuts2 = search_form['nuts2'].value
        def match_nuts3(code):
            return code.startswith(search_nuts2)

    else:
        raise ValueError("Either a nuts3 or nuts2 code must be specified")

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

def corine_area(search_form, search_answer):
    stat = {}
    for code in habitat_class_map.keys():
        stat['table_%s' % code] = []
        stat['total_%s' % code] = 0

    if not search_form['nuts3'].is_empty:
        search_nuts3 = search_form['nuts3'].value
        def match_nuts3(code):
            return (code == search_nuts3)

    elif not search_form['nuts2'].is_empty:
        search_nuts2 = search_form['nuts2'].value
        def match_nuts3(code):
            return code.startswith(search_nuts2)

    else:
        raise ValueError("Either a nuts3 or nuts2 code must be specified")

    def match_corine(code):
        return habitat_class_map.has_key(code)

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

    for code in habitat_class_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('corine_area'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_corine_area.html', 
                                                stat=stat, 
                                                corine_areas=habitat_class_map.items()))

def protected_area(search_form, search_answer):
    stat = {}
    for code in classification_map.keys():
        stat['table_%s' % code] = []
        stat['total_%s' % code] = 0

    if not search_form['nuts3'].is_empty:
        search_nuts3 = search_form['nuts3'].value
        def match_nuts3(code):
            return (code == search_nuts3)

    elif not search_form['nuts2'].is_empty:
        search_nuts2 = search_form['nuts2'].value
        def match_nuts3(code):
            return code.startswith(search_nuts2)

    else:
        raise ValueError("Either a nuts3 or nuts2 code must be specified")

    def match_protected(code):
        return classification_map.has_key(code)

    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        protected_area = 0
        for area in data['section5']['classification']:
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

    for code in classification_map.keys():
        stat['table_%s' % code].sort(key=operator.itemgetter('protected_area'), reverse=True)

    return jinja2.Markup(flask.render_template('stat_protected_area.html', 
                                                stat=stat, 
                                                protected_areas=classification_map.items()))

compute = {
    'area': area,
    'corine_area': corine_area,
    'protected_area': protected_area,
}
