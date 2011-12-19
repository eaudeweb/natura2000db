import sys
from pprint import pformat
from collections import defaultdict
import re
from schema import SpaDoc


table_names = ['CheckForm', 'QueryCombine', 'RegCod', 'actvty', 'amprep',
    'biotop', 'bird', 'corine', 'desigc', 'desigr', 'fishes', 'habit1',
    'habit2', 'histry', 'invert', 'mammal', 'map', 'photo', 'plant',
    'resp', 'sitrel', 'spec']


def lower_keys(dic):
    return {k.lower(): dic[k] for k in dic if dic[k] is not None}


def load_from_sql():
    from itertools import imap
    from sqlwrapper import open_db
    sw = open_db('rio')

    biotop_list = {}
    for row in imap(lower_keys, sw.iter_table('biotop')):
        row['_relations'] = defaultdict(list)
        biotop_list[row['sitecode']] = row

    for name in table_names:
        if name == 'biotop':
            continue
        for row in imap(lower_keys, sw.iter_table(name)):
            row = lower_keys(row)
            biotop_list[row['sitecode']]['_relations'][name.lower()].append(row)

    for biotop in biotop_list.itervalues():
        biotop['_relations'] = dict(biotop['_relations'])

    return biotop_list


skip_relations = set(['actvty', 'amprep', 'bird', 'corine', 'desigc', 'desigr',
                      'fishes', 'habit1', 'habit2', 'invert', 'mammal', 'map',
                      'photo', 'plant', 'sitrel', 'spec'])


def map_fields(biotop):
    flat = {}

    relations = biotop.pop('_relations')
    for i, regcod_row in enumerate(relations.pop('regcod')):
        for key in regcod_row:
            flat['section2_regcod_%d_%s' % (i, key)] = regcod_row[key]

    for name in skip_relations:
        relations.pop(name, [])
    if relations:
        print>>sys.stderr, 'unhandled relations: %r' % (relations.keys(),)

    for element in SpaDoc().all_children:
        flat_name = element.flattened_name()
        if element.name in biotop:
            flat[flat_name] = biotop.pop(element.name)

    return flat


def print_errors(root_element):
    for element in root_element.all_children:
        if element.errors:
            print>>sys.stderr, element.flattened_name('/'), element.errors


def known_unused_field(name):
    return any(re.match(p, name) for p in [
        r'^section2_regcod_\d+_sitecode$',
    ])

def known_extra_field(name):
    return any(re.match(p, name) for p in [
    ])


def verify_data(biotop_list):
    count = defaultdict(int)
    for biotop in biotop_list.itervalues():
        flat = map_fields(biotop)
        doc = SpaDoc.from_flat(flat)

        def get_value(element):
            if element.optional and not element.value:
                return None
            else:
                return element.u

        if doc.validate():
            flat1 = {k: v for k, v in flat.iteritems() if v}
            for name in flat1.keys():
                if known_unused_field(name):
                    del flat1[name]
            flat2 = {k: v for k, v in doc.flatten(value=get_value) if v}
            for name in flat2.keys():
                if known_extra_field(name):
                    del flat2[name]
            if set(flat1.keys()) != set(flat2.keys()):
                print>>sys.stderr, 'unused: %s, extra: %s' % (
                    {k: flat1[k] for k in set(flat1) - set(flat2)},
                    {k: flat2[k] for k in set(flat2) - set(flat1)},
                )
                count['delta'] += 1
            else:
                count['ok'] += 1

            yield doc.value

        else:
            count['error'] += 1
            print>>sys.stderr, pformat(biotop)
            print>>sys.stderr, ''
            print_errors(doc)
            print>>sys.stderr, ''
            break

    print>>sys.stderr, dict(count)


if __name__ == '__main__':
    import json
    biotop_list = load_from_sql()
    docs = list(verify_data(biotop_list))
    print json.dumps(docs, indent=2)
