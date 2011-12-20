import sys
from pprint import pformat
from collections import defaultdict
import re
from schema import SpaDoc


table_names = ['CheckForm', 'QueryCombine', 'RegCod', 'actvty', 'amprep',
    'biotop', 'bird', 'corine', 'desigc', 'desigr', 'fishes', 'habit1',
    'habit2', 'histry', 'invert', 'mammal', 'map', 'photo', 'plant',
    'resp', 'sitrel', 'spec']


def lower_keys(dic, prune=False):
    return {k.lower(): dic[k] for k in dic if (not prune or dic[k] is not None)}


def load_from_sql():
    from itertools import imap
    from sqlwrapper import open_db
    sw = open_db('rio')

    biotop_list = {}
    for row in (lower_keys(r, True) for r in sw.iter_table('biotop')):
        row['_relations'] = defaultdict(list)
        biotop_list[row['sitecode']] = row

    for name in table_names:
        if name == 'biotop':
            continue
        for row in imap(lower_keys, sw.iter_table(name)):
            sitecode = row.pop('sitecode')
            if sitecode == 'ROSCI0406' and name == 'habit1':
                continue # TODO problem in data, coverage values are NULL
            biotop_list[sitecode]['_relations'][name.lower()].append(row)

    for biotop in biotop_list.itervalues():
        biotop['_relations'] = dict(biotop['_relations'])

    return biotop_list


skip_relations = ['photo'] # TODO we don't have any actual images


info_table_map = {
    'bird': 'species_types',
    #'???': 'migratory_species_types', # TODO
    'mammal': 'mammals_types',
    'amprep': 'reptiles_types',
    'fishes': 'fishes_types',
    'invert': 'invertebrates_types',
}


taxgroup_map = {
    'P': 'plante',
    'I': 'nevertebrate',
    'R': 'reptile',
    'F': 'pesti',
    'M': 'amfibieni',
    'A': 'mamifere',
    'B': 'pasari',
}


strip = lambda (v): v.strip() if isinstance(v, basestring) else v


def map_info_table(row):
    val = lambda(name): strip(row.pop(name))
    flat_row = {
        '_code': val('specnum'),
        '_tax_code': val('tax_code'),
        '_name': val('specname'),
        '_annex_ii': val('annex_ii'),
        '_population_resident': val('resident'),
        '_population_migratory_reproduction': val('breeding'),
        '_population_migratory_wintering': val('winter'),
        '_population_migratory_passage': val('staging'),
        '_sit_evaluation_population': val('population'),
        '_sit_evaluation_conservation': val('conserve'),
        '_sit_evaluation_isolation': val('isolation'),
        '_sit_evaluation_global_eval': val('global'),
    }
    assert not row
    return flat_row


def map_fields(biotop):
    flat = {}

    relations = biotop.pop('_relations')
    for i, regcod_row in enumerate(relations.pop('regcod')):
        for key in regcod_row:
            flat['section2_regcod_%d_%s' % (i, key)] = regcod_row[key]

    for rel_name, record_name in info_table_map.items():
        for i, rel_row in enumerate(relations.pop(rel_name, [])):
            prefix = 'section3_%s_%d_dict_name' % (record_name, i)
            flat_row = map_info_table(rel_row)
            for name in flat_row:
                flat[prefix + name] = flat_row[name]

    for i, plant_row in enumerate(relations.pop('plant', [])):
        val = lambda(name): plant_row.pop(name)
        prefix = 'section3_plants_types_%d_plant_types' % i
        flat[prefix + '_code'] = val('specnum')
        flat[prefix + '_tax_code'] = val('tax_code')
        flat[prefix + '_name'] = val('specname')
        flat[prefix + '_annex_ii'] = val('annex_ii')
        flat[prefix + '_population'] = val('resident')
        flat[prefix + '_sit_evaluation_population'] = val('population')
        flat[prefix + '_sit_evaluation_conservation'] = val('isolation')
        flat[prefix + '_sit_evaluation_isolation'] = val('conserve')
        flat[prefix + '_sit_evaluation_global_eval'] = val('global')
        assert not plant_row

    for i, spec_row in enumerate(relations.pop('spec', [])):
        val = lambda(name): spec_row.pop(name)
        prefix = 'section3_other_species_%d_other_specie' % i
        flat[prefix + '_category'] = taxgroup_map[val('taxgroup')]
        flat[prefix + '_code'] = strip(val('specnum'))
        flat[prefix + '_tax_code'] = strip(val('tax_code'))
        flat[prefix + '_scientific_name'] = val('specname')
        flat[prefix + '_population_population_text'] = strip(val('population'))
        flat[prefix + '_population_population_trend'] = val('motivation')
        assert not spec_row, repr(spec_row)

    for i, habit1_row in enumerate(relations.pop('habit1', [])):
        val = lambda(name): habit1_row.pop(name)
        prefix = 'section3_habitat_types_%d_habitat_type' % i
        flat[prefix + '_code'] = val('hbcdax')
        flat[prefix + '_percentage'] = val('cover')
        flat[prefix + '_repres'] = val('represent')
        flat[prefix + '_relativ_area'] = val('rel_surf')
        flat[prefix + '_conservation_status'] = val('conserve')
        flat[prefix + '_global_evaluation'] = val('global')
        assert not habit1_row

    for habit2_row in relations.pop('habit2', []):
        name = habit2_row.pop('habcode')
        key = 'section4_site_characteristics_habitat_classes_' + name
        flat[key] = habit2_row.pop('cover')
        assert not habit2_row

    for i, sitrel_row in enumerate(relations.pop('sitrel', [])):
        flat['section1_other_sites_%d_other_site' % i] = sitrel_row.pop('othersite')
        sitrel_row.pop('othertype') # redundant info
        assert not sitrel_row

    for i, map_row in enumerate(relations.pop('map', [])):
        val = lambda(name): map_row.pop(name)
        flat['section7_map_%d_number' % i] = val('map_no')
        flat['section7_map_%d_scale' % i] = val('scale')
        flat['section7_map_%d_projection' % i] = val('projection')
        assert val('details') == 'Datum Dealul_Piscului_1970'
        assert not map_row

    for i, corine_row in enumerate(relations.pop('corine', [])):
        val = lambda(name): corine_row.pop(name)
        prefix = 'section5_corine_relations_%d_record' % i
        flat[prefix + '_code'] = val('corine')
        flat[prefix + '_type'] = val('overlap') # TODO is the mapping right?
        flat[prefix + '_overlap'] = val('overlap_p')
        assert not corine_row

    for i, desigc_row in enumerate(relations.pop('desigc', [])):
        val = lambda(name): desigc_row.pop(name)
        prefix = 'section5_clasification_%d_record' % i
        flat[prefix + '_code'] = val('desicode')
        flat[prefix + '_percentage'] = val('cover')
        assert not desigc_row

    for i, desigr_row in enumerate(relations.pop('desigr', [])):
        val = lambda(name): desigr_row.pop(name)
        prefix = 'section5_national_relations_%d_record' % i
        flat[prefix + '_type'] = val('overlap') # TODO is the mapping right?
        flat[prefix + '_name'] = val('des_site')
        flat[prefix + '_overlap'] = val('overlap_p')
        val('desicode') # TODO ok to ignore?
        assert not desigr_row

    activity_in = activity_out = 0
    for actvty_row in relations.pop('actvty', []):
        val = lambda(name): actvty_row.pop(name)
        if val('in_out') == 'O':
            i = activity_in
            activity_in += 1
            prefix = 'section6_in_jur_outside_activities_%d_record' % i
            val('cover') # TODO for 'outside' activities, coverage is ignored
        else:
            i = activity_out
            activity_out += 1
            prefix = 'section6_in_jur_inside_activities_%d_record' % i
            flat[prefix + '_percentage'] = val('cover')
        flat[prefix + '_code'] = val('act_code')
        flat[prefix + '_intensity'] = val('intensity')
        flat[prefix + '_influence'] = val('influence')
        assert not actvty_row

    for name in skip_relations:
        relations.pop(name, [])
    if relations:
        print>>sys.stderr, 'unhandled relations: %r' % (relations.keys(),)

    assert biotop.pop('lon_ew') == 'E'
    assert biotop.pop('lat_nz') == 'N'
    val = lambda(name): biotop.pop(name)
    dms_val = lambda(n): val(n+'_deg') + val(n+'_min')/60. + val(n+'_sec')/3600.
    flat['section2_longitude'] = dms_val('lon')
    flat['section2_latitude'] = dms_val('lat')

    flat['section4_site_characteristics_other'] = val('charact')

    assert val('mapsincl') == val('photos') == 0

    for element in SpaDoc().all_children:
        flat_name = element.flattened_name()
        if element.name in biotop:
            flat[flat_name] = biotop.pop(element.name)

    assert not biotop, repr(biotop)

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
            print>>sys.stderr, pformat(doc.value)
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
