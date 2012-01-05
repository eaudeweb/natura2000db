import sys
from pprint import pformat
from collections import defaultdict
import re
import logging
import schema


log = logging.getLogger(__name__)


table_names = ['CheckForm', 'QueryCombine', 'RegCod', 'actvty', 'amprep',
    'biotop', 'bird', 'corine', 'desigc', 'desigr', 'fishes', 'habit1',
    'habit2', 'histry', 'invert', 'mammal', 'map', 'photo', 'plant',
    'resp', 'sitrel', 'spec']


def lower_keys(dic, prune=False):
    return dict((k.lower(), dic[k]) for k in dic if (not prune or dic[k] is not None))


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
    'mammal': 'species_mammal',
    'amprep': 'species_reptile',
    'fishes': 'species_fish',
    'invert': 'species_invertebrate',
}


taxgroup_map = {
    'P': 'plant',
    'I': 'invertebrate',
    'R': 'reptile',
    'F': 'fish',
    'M': 'amphibian',
    'A': 'mammal',
    'B': 'bird',
}


strip = lambda (v): v.strip() if isinstance(v, basestring) else v


def map_info_table(row):
    val = lambda(name): strip(row.pop(name))
    flat_row = {
        '_code': val('specnum'),
        '_tax_code': val('tax_code'),
        '_name': val('specname'),
        '_population_resident': val('resident'),
        '_population_migratory_reproduction': val('breeding'),
        '_population_migratory_wintering': val('winter'),
        '_population_migratory_passage': val('staging'),
        '_site_evaluation_population': val('population'),
        '_site_evaluation_conservation': val('conserve'),
        '_site_evaluation_isolation': val('isolation'),
        '_site_evaluation_global_eval': val('global'),
    }
    assert not row
    return flat_row


def map_fields(biotop):
    flat = {}
    sitecode = biotop.pop('sitecode')

    relations = biotop.pop('_relations')
    regcod_map = {
        'reg_code': 'code',
        'cover': 'coverage',
    }
    for i, regcod_row in enumerate(relations.pop('regcod')):
        prefix = 'section2_administrative_%d' % i
        flat[prefix + '_code'] = regcod_row.pop('reg_code')
        flat[prefix + '_coverage'] = regcod_row.pop('cover')
        assert not regcod_row

    bird_n = bird_extra_n = 0
    for bird_row in relations.pop('bird', []):
        annex_ii = bird_row.pop('annex_ii')
        if annex_ii == 'Y':
            record_name = 'species_bird'
            i = bird_n
            bird_n += 1
        else:
            record_name = 'species_bird_extra'
            i = bird_extra_n
            bird_extra_n += 1
        prefix = 'section3_%s_%d' % (record_name, i)
        flat_row = map_info_table(bird_row)
        for name in flat_row:
            flat[prefix + name] = flat_row[name]

    for rel_name, record_name in info_table_map.items():
        for i, rel_row in enumerate(relations.pop(rel_name, [])):
            prefix = 'section3_%s_%d' % (record_name, i)
            assert rel_row.pop('annex_ii') == 'Y'
            flat_row = map_info_table(rel_row)
            for name in flat_row:
                flat[prefix + name] = flat_row[name]

    for i, plant_row in enumerate(relations.pop('plant', [])):
        val = lambda(name): plant_row.pop(name)
        prefix = 'section3_species_plant_%d' % i
        flat[prefix + '_code'] = val('specnum')
        flat[prefix + '_tax_code'] = val('tax_code')
        flat[prefix + '_name'] = val('specname')
        flat[prefix + '_population'] = val('resident')
        flat[prefix + '_site_evaluation_population'] = val('population')
        flat[prefix + '_site_evaluation_conservation'] = val('isolation')
        flat[prefix + '_site_evaluation_isolation'] = val('conserve')
        flat[prefix + '_site_evaluation_global_eval'] = val('global')
        assert val('annex_ii') == 'Y'
        assert not plant_row

    for i, spec_row in enumerate(relations.pop('spec', [])):
        val = lambda(name): spec_row.pop(name)
        prefix = 'section3_species_other_%d' % i
        flat[prefix + '_category'] = taxgroup_map[val('taxgroup')]
        flat[prefix + '_code'] = strip(val('specnum'))
        flat[prefix + '_tax_code'] = strip(val('tax_code'))
        flat[prefix + '_scientific_name'] = val('specname')
        flat[prefix + '_population_text'] = strip(val('population'))
        flat[prefix + '_population_trend'] = val('motivation')
        assert not spec_row, repr(spec_row)

    i = 0
    for habit1_row in relations.pop('habit1', []):
        val = lambda(name): habit1_row.pop(name)
        prefix = 'section3_habitat_%d' % i
        code = val('hbcdax')
        if code not in schema.habitat_type_map:
            log.warn('%s - unknown habitat type code %r', sitecode, code)
            continue
        flat[prefix + '_code'] = code
        flat[prefix + '_percentage'] = val('cover')
        flat[prefix + '_representativeness'] = val('represent')
        flat[prefix + '_relative_area'] = val('rel_surf')
        flat[prefix + '_conservation_status'] = val('conserve')
        flat[prefix + '_global_evaluation'] = val('global')
        assert not habit1_row
        i += 1

    for habit2_row in relations.pop('habit2', []):
        name = habit2_row.pop('habcode')
        key = 'section4_characteristics_habitat_' + name
        flat[key] = habit2_row.pop('cover')
        assert not habit2_row

    for i, sitrel_row in enumerate(relations.pop('sitrel', [])):
        flat['section1_other_sites_%d' % i] = sitrel_row.pop('othersite')
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
        prefix = 'section5_corine_%d' % i
        flat[prefix + '_code'] = val('corine')
        flat[prefix + '_type'] = val('overlap')
        flat[prefix + '_overlap'] = val('overlap_p')
        assert not corine_row

    i = 0
    for desigc_row in relations.pop('desigc', []):
        val = lambda(name): desigc_row.pop(name)
        prefix = 'section5_classification_%d' % i
        code = val('desicode')
        if code not in schema.classification_map:
            log.warn('%s - unknown classification code %r', sitecode, code)
            continue
        flat[prefix + '_code'] = code
        flat[prefix + '_percentage'] = val('cover')
        assert not desigc_row
        i += 1

    for i, desigr_row in enumerate(relations.pop('desigr', [])):
        val = lambda(name): desigr_row.pop(name)
        prefix = 'section5_national_%d' % i
        flat[prefix + '_type'] = val('overlap')
        flat[prefix + '_site_name'] = val('des_site')
        flat[prefix + '_site_type'] = val('desicode')
        flat[prefix + '_overlap'] = val('overlap_p')
        assert not desigr_row

    activity_in = activity_out = 0
    for actvty_row in relations.pop('actvty', []):
        val = lambda(name): actvty_row.pop(name)
        code = val('act_code')
        if code not in schema.antropic_activities_map:
            log.warn('%s - unknown antropic activity code %r', sitecode, code)
            continue
        if val('in_out') == 'O':
            i = activity_in
            activity_in += 1
            prefix = 'section6_activity_external_%d' % i
        else:
            i = activity_out
            activity_out += 1
            prefix = 'section6_activity_internal_%d' % i
        flat[prefix + '_code'] = code
        flat[prefix + '_intensity'] = val('intensity')
        flat[prefix + '_percentage'] = val('cover') or '0.00'
        flat[prefix + '_influence'] = val('influence')
        assert not actvty_row

    for name in skip_relations:
        relations.pop(name, [])
    if relations:
        log.warn('unhandled relations: %r', relations.keys())

    _nodefault = object()
    def val(name, default=_nodefault):
        if default is _nodefault:
            try:
                return biotop.pop(name)
            except:
                import pdb; pdb.set_trace()
                raise
        else:
            return biotop.pop(name, default)

    flat['section1_code'] = sitecode
    flat['section1_date_document_add'] = val('date')
    flat['section1_date_document_update'] = val('update', '')
    flat['section1_responsible'] = val('respondent')
    flat['section1_name'] = val('site_name')
    flat['section1_date_proposal'] = val('date_prop', '')
    flat['section1_date_confirmation_sci'] = val('date_con', '')
    flat['section1_date_confirmation_spa'] = val('spa_date', '')
    flat['section1_date_confirmation_sac'] = val('sac_date', '')

    assert biotop.pop('lon_ew') == 'E'
    assert biotop.pop('lat_nz') == 'N'
    dms_val = lambda(n): val(n+'_deg') + val(n+'_min')/60. + val(n+'_sec')/3600.
    flat['section2_longitude'] = dms_val('lon')
    flat['section2_latitude'] = dms_val('lat')

    flat['section2_altitude_min'] = val('alt_min')
    flat['section2_altitude_max'] = val('alt_max')
    flat['section2_altitude_mean'] = val('alt_mean')
    flat['section2_biogeographic_alpine'] = val('alpine')
    flat['section2_biogeographic_continental'] = val('continent')
    flat['section2_biogeographic_steppic'] = val('steppic')
    flat['section2_biogeographic_pontic'] = val('pontic')
    flat['section2_biogeographic_pannonic'] = val('pannonic')

    flat['section4_characteristics_other'] = val('charact')
    flat['section4_vulnerability'] = val('vulnar')
    flat['section4_designation'] = val('design', '')
    flat['section4_ownership'] = val('owner', '')
    flat['section4_documentation'] = val('docum', '')

    flat['section6_management_organisation'] = val('manager')
    flat['section6_management_plan'] = val('managpl')

    assert val('mapsincl') == val('photos') == 0

    for element in schema.SpaDoc().all_children:
        flat_name = element.flattened_name()
        if element.name in biotop:
            flat[flat_name] = biotop.pop(element.name)

    assert not biotop, repr(biotop)

    return flat


def print_errors(root_element):
    for element in root_element.all_children:
        if element.errors:
            log.error('%s %s', element.flattened_name('/'), element.errors)


def verify_data(biotop_list):
    count = defaultdict(int)
    for biotop in biotop_list.itervalues():
        flat = map_fields(biotop)
        doc = schema.SpaDoc.from_flat(flat)

        def get_value(element):
            if element.optional and not element.value:
                return None
            else:
                return element.u

        if doc.validate():
            flat1 = dict((k, v) for k, v in flat.iteritems() if v)
            flat2 = dict((k, v) for k, v in doc.flatten(value=get_value) if v)
            if set(flat1.keys()) != set(flat2.keys()):
                log.warn('unused: %s, extra: %s',
                         dict((k, flat1[k]) for k in set(flat1) - set(flat2)),
                         dict((k, flat2[k]) for k in set(flat2) - set(flat1)))
                count['delta'] += 1
            else:
                count['ok'] += 1

            yield doc.value

        else:
            count['error'] += 1
            log.error(pformat(flat))
            log.error(pformat(biotop))
            log.error(pformat(doc.value))
            log.error('')
            print_errors(doc)
            break

    log.info('done: %r', dict(count))


if __name__ == '__main__':
    import json
    biotop_list = load_from_sql()
    docs = list(verify_data(biotop_list))
    print json.dumps(docs, indent=2)
