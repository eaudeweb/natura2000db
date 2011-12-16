from pprint import pprint
from schema import SpaDoc


table_names = ['CheckForm', 'QueryCombine', 'RegCod', 'actvty', 'amprep',
    'biotop', 'bird', 'corine', 'desigc', 'desigr', 'fishes', 'habit1',
    'habit2', 'histry', 'invert', 'mammal', 'map', 'photo', 'plant',
    'resp', 'sitrel', 'spec']


def lower_keys(dic):
    return {k.lower(): unicode(dic[k]) for k in dic if dic[k] is not None}


def load_from_sql():
    from itertools import imap
    from collections import defaultdict
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
            biotop_list[row['sitecode']]['_relations'][name].append(row)

    return biotop_list


def map_fields(biotop):
    flat = {}
    for element in SpaDoc().all_children:
        if element.name in biotop:
            print '%s: %r' % (element.name, biotop[element.name])
            flat[element.flattened_name()] = biotop.pop(element.name)
    return flat


def print_errors(root_element):
    for element in root_element.all_children:
        if element.errors:
            print element.flattened_name('/'), element.errors


def verify_data(biotop_list):
    for biotop in biotop_list.itervalues():
        pprint(dict(biotop['_relations']))
        del biotop['_relations']
        doc = SpaDoc.from_flat(map_fields(biotop))
        if not doc.validate():
            pprint(biotop)
            print
            print_errors(doc)
            print
            break


if __name__ == '__main__':
    import json
    biotop_list = load_from_sql()
    verify_data(biotop_list)
