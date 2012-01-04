import flask
import jinja2


def area(search_form, search_answer):
    stat = {'table': [], 'total': 0}
    for doc in search_answer['docs']:
        data = doc['data']
        total_area = data['section2']['area']

        admin_code = search_form['nuts3'].value
        for admin in data['section2']['administrative']:
            if admin['code'] == admin_code:
                break
        else:
            raise ValueError('no matching nuts3 %r' % admin_code)

        admin_area = total_area * (admin['coverage'] / 100)
        stat['total'] += admin_area

        stat['table'].append({
            'id': doc['id'],
            'name': doc['name'],
            'total_area': total_area,
            'admin_percent': admin['coverage'],
            'admin_area': admin_area,
        })

    return jinja2.Markup(flask.render_template('stat_area.html', stat=stat))


compute = {
    'area': area,
}
