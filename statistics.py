import operator
import flask
import jinja2


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

        for admin in data['section2']['administrative']:
            if match_nuts3(admin['code']):
                break
        else:
            raise ValueError('no matching nuts3, doc_id=%r'
                             % data['section1']['code'])

        admin_area = total_area * (admin['coverage'] / 100)
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


compute = {
    'area': area,
}
