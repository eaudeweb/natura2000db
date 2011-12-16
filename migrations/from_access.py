table_names = ['CheckForm', 'QueryCombine', 'RegCod', 'actvty', 'amprep',
    'biotop', 'bird', 'corine', 'desigc', 'desigr', 'fishes', 'habit1',
    'habit2', 'histry', 'invert', 'mammal', 'map', 'photo', 'plant',
    'resp', 'sitrel', 'spec']


def lower_keys(dic):
    return {k.lower(): dic[k] for k in dic}


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


if __name__ == '__main__':
    import json
    biotop_list = load_from_sql()
    print json.dumps(biotop_list, indent=2)
