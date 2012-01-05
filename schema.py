# -*- coding: utf-8 -*-

import os.path
import re
import json
import flatland as fl


def _load_json(name):
    with open(os.path.join(os.path.dirname(__file__), name), 'rb') as f:
        return json.load(f)


def valid_float(element, state):
    if element.value is None and element.optional:
        return True

    if isinstance(element.value, float):
        return True

    else:
        element.add_error(u"Valoarea trebuie sa fie numerică")
        return False

def valid_int(element, state):
    if element.value is None and element.optional:
        return True

    if isinstance(element.value, int):
        return True

    else:
        element.add_error(u"Valoarea trebuie sa fie numerică (%r)" % element.optional)
        return False

def valid_type(element, state):
    patt = re.compile(r'^[a-k]$', re.IGNORECASE)
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error(u"Numai literele intre A si K sunt acceptate")
        return False

def valid_year_month(element, state):
    patt = re.compile(r'^\d{6}$')
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error(u"Dată incorectă. Formatul acceptat este: YYYYMM")
        return False

def valid_site_code(element, state):
    patt = re.compile(r'^\w{9}$')
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error(u"Cod incorect")
        return False

def valid_any(element, state):
    for child in element.values():
        if child.value:
            return True
    element.add_error(u"Cel puțin o valoare trebuie selectată")
    return False

def valid_enum(element, state):
    if element.value not in element.valid_values:
        element.add_error(u"%r nu este o valoare corectă pentru %s" %
                          (element.value, element.name))
        return False

    return True


from flatland.signals import validator_validated
from flatland.schema.base import NotEmpty
@validator_validated.connect
def validated(sender, element, result, **kwargs):
    if sender is NotEmpty:
        if not result:
            element.add_error(u"obligatorie")


def id_and_label(mapping):
    return dict((k, '%s (%s)' % (k, v)) for k, v in mapping.iteritems())


CommonFloat = fl.Float.using(optional=True, validators=[valid_float], format='%.2f')
CommonDate = fl.String.using(optional=True, validators=[valid_year_month])
CommonBoolean = fl.Boolean.using(optional=True).with_properties(widget='checkbox')
CommonString = fl.String.using(optional=True)
CommonEnum = fl.Enum.using(optional=True, validators=[valid_enum]).with_properties(widget='select')
CommonList = fl.List.using(optional=True).with_properties(widget='table')
CommonGeoFloat = fl.Float.using(optional=True)

def Ordered_dict_of(*fields):
    order = [field.name for field in fields]
    return fl.Dict.of(*fields).with_properties(order=order)


InfoColumn = Ordered_dict_of(
    CommonEnum.named('population').valued('A', 'B', 'C', 'D').with_properties(label=u'Populație'),
    CommonEnum.named('conservation').valued('A', 'B', 'C').with_properties(label=u'Conservare'),
    CommonEnum.named('isolation').valued('A', 'B', 'C').with_properties(label=u'Izolare'),
    CommonEnum.named('global_eval').valued('A', 'B', 'C').with_properties(label=u'Evaluare globală'),
    )


InfoTable = CommonList.of(
    Ordered_dict_of(

        CommonString.named('code').using(optional=False).with_properties(label=u'Cod'),
        CommonString.named('tax_code').with_properties(widget='hidden', label=u'Cod taxonomic'),
        CommonString.named('name').using(optional=False).with_properties(label=u'Nume'),

        Ordered_dict_of(

            CommonString.named('resident').with_properties(label=u'Residentă'),

            Ordered_dict_of(
                CommonString.named('reproduction').with_properties(label=u'Reproducere'),
                CommonString.named('wintering').with_properties(label=u'Iernat'),
                CommonString.named('passage').with_properties(label=u'Pasaj'),
                ).named('migratory').with_properties(label=u'Migratoare'),

            ).named('population').with_properties(label=u'Populație'),

        InfoColumn.named('site_evaluation').with_properties(label=u'Evaluarea sitului'),

        ),
    )


section_1 = Ordered_dict_of(

    CommonString.named('type').using(optional=False, validators=[valid_type]).with_properties(label=u'Tip'),
    CommonString.named('code').using(optional=False, validators=[valid_site_code]).with_properties(label=u'Codul sitului'),

    CommonDate.named('date_document_add').using(optional=False).with_properties(label=u'Data completării'),
    CommonDate.named('date_document_update').with_properties(label=u'Data actualizării'),

    CommonList.named('other_sites').of(

        CommonString.using(validators=[valid_site_code]) \
                    .with_properties(label=u'Coduri ale siturilor Natura 2000',
                                     widget='site_link')

        ).with_properties(widget='list', label=u'Legături cu alte situri Natura 2000:'),

    CommonString.named('responsible').with_properties(widget='textarea', label=u'Responsabili'),

    CommonString.named('name').using(optional=False).with_properties(label=u'Numele sitului', widget='textarea'),

    Ordered_dict_of(
        CommonDate.named('proposal').with_properties(label=u'Data propunerii ca sit SCI'),
        CommonDate.named('confirmation_sci').with_properties(label=u'Data confirmării ca sit SCI'),
        CommonDate.named('confirmation_spa').with_properties(label=u'Data confirmării ca sit SPA'),
        CommonDate.named('confirmation_sac').with_properties(label=u'Data desemnării ca sit SAC'),
        ).named('date') \
         .with_properties(label=u'Datele indicării și desemnării/clasificării sitului',
                          widget='dict'),

    ).with_properties(label=u'1. IDENTIFICAREA SITULUI')


nuts2 = _load_json('reference/nuts2003_level2_ro.json')
nuts3 = _load_json('reference/nuts2003_level3_ro.json')
biogeographic_map = _load_json('reference/biogeographic_ro.json')


section_2 = Ordered_dict_of(

    CommonGeoFloat.named('longitude').with_properties(label=u'Longitudine'),
    CommonGeoFloat.named('latitude').with_properties(label=u'Latitudine'),

    CommonFloat.named('area').with_properties(label=u'Suprafață (ha)'),
    CommonFloat.named('length').with_properties(label=u'Lungimea sitului (km)'),

    Ordered_dict_of(
        CommonFloat.named('min').with_properties(label=u'Minimă'),
        CommonFloat.named('max').with_properties(label=u'Maximă'),
        CommonFloat.named('mean').with_properties(label=u'Medie'),
        ).named('altitude').with_properties(label=u'Altitudine (m)', widget='dict'),

    CommonList.named('administrative').of(

        Ordered_dict_of(
            CommonEnum.named('code') \
                      .valued(*sorted(nuts3.keys())) \
                      .using(optional=False) \
                      .with_properties(label=u'Județ',
                                       widget='select',
                                       value_labels=id_and_label(nuts3)),
            CommonFloat.named('coverage') \
                       .using(optional=False) \
                       .with_properties(label=u'Pondere (%)'),
            ),

        ).using(optional=False).with_properties(label=u'Regiunea administrativă'),

    Ordered_dict_of(
        *[CommonBoolean.named(key).with_properties(label=label)
          for key, label in sorted(biogeographic_map.items())]
        ).named('biogeographic').using(validators=[valid_any]).with_properties(label=u'Regiunea biogeografică', widget='dict'),

    ).with_properties(label=u'2. LOCALIZAREA SITULUI')


_habitat_type_data = _load_json('reference/habitat_type_ro.json')
habitat_type_map = dict((k, ('%s %s' % (name, pri)).strip())
                        for k, [pri, name] in _habitat_type_data.iteritems())

species_category_map = _load_json('reference/species_category_ro.json')


section_3 = Ordered_dict_of(

    CommonList.named('habitat').of(

        Ordered_dict_of(
            CommonEnum.named('code') \
                      .valued(*sorted(habitat_type_map.keys())) \
                      .using(optional=False) \
                      .with_properties(label=u'Cod',
                                       value_labels=id_and_label(habitat_type_map)),
            CommonString.named('percentage').using(optional=False).with_properties(label=u'Pondere'),
            CommonEnum.named('representativeness').valued('A', 'B', 'C', 'D').with_properties(label=u'Reprezentativitate'),
            CommonEnum.named('relative_area').valued('A', 'B', 'C').with_properties(label=u'Suprafață relativă'),
            CommonEnum.named('conservation_status').valued('A', 'B', 'C').with_properties(label=u'Stare de conservare'),
            CommonEnum.named('global_evaluation').valued('A', 'B', 'C').with_properties(label=u'Evaluare globală'),
            ),

        ).with_properties(label=u'Tipuri de habitat prezente în sit și evaluarea sitului în ceea ce le priveste:'),

    InfoTable.named('species_bird').with_properties(label=u'Specii de păsări enumerate în anexa I la Directiva Consiliului 79/409/CEE'),
    InfoTable.named('species_bird_extra').with_properties(label=u'Specii de păsări cu migrație regulată nemenționate în anexa I la Directiva Consiliului 79/409/CEE'),
    InfoTable.named('species_mammal').with_properties(label=u'Specii de mamifere enumerate în anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('species_reptile').with_properties(label=u'Specii de amfibieni și reptile enumerate în anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('species_fish').with_properties(label=u'Specii de pești enumerate în anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('species_invertebrate').with_properties(label=u'Specii de nevertebrate enumerate în anexa II la Directiva Consiliului 92/43/CEE'),

    CommonList.named('species_plant').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label=u'Cod'),
            CommonString.named('tax_code').with_properties(widget='hidden', label=u'Cod taxonomic'),
            CommonString.named('name').using(optional=False).with_properties(label=u'Nume'),
            CommonString.named('population').with_properties(label=u'Populație'),
            InfoColumn.named('site_evaluation').with_properties(label=u'Evaluarea sitului'),
            ),

        ).with_properties(label=u'Specii de plante enumerate în anexa II la Directiva Consiliului 92/43/CEE'),

    CommonList.named('species_other').of(
        Ordered_dict_of(

            CommonEnum.named('category') \
                      .with_properties(optional=False) \
                      .valued(*sorted(species_category_map.keys())) \
                      .with_properties(label=u'Categorie',
                                       value_labels=species_category_map),

            CommonString.named('code').with_properties(label=u'Cod'),
            CommonString.named('tax_code').with_properties(widget='hidden', label=u'Cod taxonomic'),
            CommonString.named('scientific_name').using(optional=False).with_properties(label=u'Denumire științifică'),

            Ordered_dict_of(
                CommonString.named('text'),
                CommonEnum.named('trend').valued('A', 'B', 'C', 'D'),
                ).named('population').with_properties(label=u'Populație'),

            ),

        ).with_properties(label=u'Alte specii importante de floră si faună'),

    ).with_properties(label=u'3. INFORMATII ECOLOGICE')


habitat_class_map = _load_json('reference/habitat_class_ro.json')


section_4 = Ordered_dict_of(

    Ordered_dict_of(

        Ordered_dict_of(
            *[CommonFloat.named(key).with_properties(label=habitat_class_map[key])
              for key in sorted(habitat_class_map)]
            ).named('habitat') \
             .using(optional=True) \
             .with_properties(label=u'Clase de habitat', widget='habitat_breakdown'),

        CommonString.named('other').with_properties(label=u'Alte caracteristici ale sitului', widget='textarea'),

        ).named('characteristics') \
         .using(optional=True) \
         .with_properties(label=u'Caracteristici generale ale sitului', widget='dict'),

    CommonString.named('quality').with_properties(widget='textarea', label=u'Calitate si importanță'),
    CommonString.named('vulnerability').with_properties(widget='textarea', label=u'Vulnerabilitate'),
    CommonString.named('designation').with_properties(widget='textarea', label=u'Desemnarea sitului (vezi observațiile privind datele cantitative de mai jos)'),
    CommonString.named('ownership').with_properties(widget='textarea', label=u'Tip de proprietate'),
    CommonString.named('documentation').with_properties(widget='textarea', label=u'Documentație'),

    CommonList.named('history').of(

        Ordered_dict_of(
            CommonString.named('date').with_properties(label=u'Dată'),
            CommonString.named('field').with_properties(label=u'Câmpul modificat'),
            CommonString.named('description').with_properties(label=u'Descriere'),
            ),

        ).with_properties(label=u'Istoric (se va completa de catre Comisie)'),

    ).with_properties(label=u'4. DESCRIEREA SITULUI')


international_classification_map = _load_json('reference/international_ro.json')


classification_map = _load_json('reference/classification_ro.json')


section_5 = Ordered_dict_of(

    CommonList.named('classification').of(

        Ordered_dict_of(

            CommonEnum.named('code') \
                      .with_properties(optional=False) \
                      .valued(*sorted(classification_map.keys())) \
                      .with_properties(label=u'Cod',
                                       value_labels=id_and_label(classification_map)),
            CommonFloat.named('percentage').with_properties(label=u'Pondere %'),
            ),

        ).with_properties(label=u'Clasificare la nivel național si regional'),

    CommonList.named('national').of(

        Ordered_dict_of(
            CommonString.named('type').with_properties(label=u'Tip'),
            CommonString.named('site_name').using(optional=False).with_properties(label=u'Numele sitului'),
            CommonString.named('site_type').with_properties(label=u'Tipul sitului'),
            CommonFloat.named('overlap').with_properties(label=u'Suprapunere %'),
            ),

        ).with_properties(label=u'Relațiile sitului descris cu alte situri - desemnate la nivel national sau regional'),

    CommonList.named('international').of(

        Ordered_dict_of(
            CommonEnum.named('type') \
                      .valued(*[k for k,v in international_classification_map]) \
                      .with_properties(label=u'Tip'),
            CommonString.named('site_name').using(optional=False).with_properties(label=u'Numele sitului'),
            CommonString.named('site_type').with_properties(label=u'Tipul sitului'),
            CommonFloat.named('overlap').with_properties(label=u'Suprapunere %'),
            ),

        ).with_properties(label=u'Relațiile sitului descris cu alte situri - desemnate la nivel international'),

    CommonList.named('corine').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label=u'Cod sit Corine'),
            CommonString.named('type').with_properties(label=u'Tip'),
            CommonFloat.named('overlap').with_properties(label=u'Suprapunere %'),
            ),

        ).with_properties(label=u'Relațiile sitului descris cu biotopuri Corine'),

    ).with_properties(label=u'5. STATUTUL DE PROTECȚIE AL SITULUI ȘI LEGĂTURA CU BIOTOPURILE CORINE')


antropic_activities_map = _load_json('reference/activities_ro.json')


antropic_activity = Ordered_dict_of(
    CommonEnum.named('code') \
              .using(optional=False) \
              .valued(*sorted(antropic_activities_map.keys())) \
              .with_properties(label=u'Cod',
                               value_labels=id_and_label(antropic_activities_map)),
    CommonEnum.named('intensity').valued('A', 'B', 'C').with_properties(label=u'Intensitate'),
    CommonFloat.named('percentage').with_properties(label=u'% din sit'),
    CommonEnum.named('influence').valued('+', '0', '-').with_properties(label=u'Influență'),
    )


section_6 = Ordered_dict_of(

    Ordered_dict_of(

        CommonList.named('internal').of(antropic_activity) \
            .with_properties(label=u'Activitâți și consecințe în interiorul sitului'),

        CommonList.named('external').of(antropic_activity) \
            .with_properties(label=u'Activitâți și consecințe în jurul sitului'),

        ).named('activity') \
         .with_properties(widget='dict', label=u"Activitâți antropice, consecințele lor generale și suprafața din sit afectată"),

    Ordered_dict_of(
        CommonString.named('organisation').with_properties(widget='textarea', label=u'Organismul responsabil pentru managementul sitului'),
        CommonString.named('plan').with_properties(widget='textarea', label=u'Planuri de management al sitului'),
        ).named('management') \
         .with_properties(widget='dict', label=u"Managementul sitului"),

    ).with_properties(label=u'6. ACTIVITĂȚILE ANTROPICE ȘI EFECTELE LOR ÎN SIT ȘI ÎN JURUL ACESTUIA')


section_7 = Ordered_dict_of(

    CommonList.named('map').of(

        Ordered_dict_of(
            CommonString.named('number').with_properties(label=u'Numar național hartă'),
            CommonString.named('scale').with_properties(label=u'Scara'),
            CommonString.named('projection').with_properties(label=u'Proiecție'),
            ).with_properties(widget='dict'),

        ).with_properties(widget='list', label=u'Hartă fizică'),

    CommonString.named('limits').with_properties(widget='textarea', label=u'Specificați dacă limitele sitului sunt disponibile în format digital'),

    ).with_properties(label=u'7. HARTA SITULUI')


SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'),
    section_3.named('section3').with_properties(widget='section'),
    section_4.named('section4').with_properties(widget='section'),
    section_5.named('section5').with_properties(widget='section'),
    section_6.named('section6').with_properties(widget='section'),
    section_7.named('section7').with_properties(widget='section'))



def indexer(*paths, **kwargs):
    concat = kwargs.pop('concat', False)
    labels = kwargs.pop('labels', True)

    def values(doc):
        for p in paths:
            for element in doc.find(p):
                value = element.value
                if value:
                    yield value
                    if labels and 'value_labels' in element.properties:
                        yield element.properties['value_labels'][value]

    def index(doc):
        if concat:
            return ' '.join(unicode(v) for v in values(doc))
        else:
            return list(values(doc))

    return index


def bio_region_index(doc):
    bio_regions = doc['section2']['biogeographic'].value
    out = []
    for name in bio_regions:
        if bio_regions[name]:
            out.append(name)
    return out


def habitat_class_index(doc):
    hc_element = doc['section4']['characteristics']['habitat']
    return [element.name for element in hc_element.children if element.value]


def spa_sci_index(doc):
    doc_id = doc['section1']['code'].value
    if doc_id[2:5] == 'SPA':
        return 'spa'
    elif doc_id[2:5] == 'SCI':
        return 'sci'
    else:
        raise ValueError('unkown document type (spa/sci) %r' % doc_id)


def nuts2_index(doc):
    values = set()
    for element in doc.find('section2/administrative[:]/code'):
        n2code = element.value[:-1]
        if n2code in nuts2:
            values.add(n2code)
    return sorted(values)


full_text_fields = [
    'section1/name',
    'section1/code',
    'section1/responsible',
    'section2/administrative[:]/code',
    'section3/habitat[:]/code',
    'section3/species_bird[:]/code',
    'section3/species_bird[:]/tax_code',
    'section3/species_bird[:]/name',
    'section3/species_bird_extra[:]/code',
    'section3/species_bird_extra[:]/tax_code',
    'section3/species_bird_extra[:]/name',
    'section3/species_mammal[:]/code',
    'section3/species_mammal[:]/tax_code',
    'section3/species_mammal[:]/name',
    'section3/species_reptile[:]/code',
    'section3/species_reptile[:]/tax_code',
    'section3/species_reptile[:]/name',
    'section3/species_fish[:]/code',
    'section3/species_fish[:]/tax_code',
    'section3/species_fish[:]/name',
    'section3/species_invertebrate[:]/code',
    'section3/species_invertebrate[:]/tax_code',
    'section3/species_invertebrate[:]/name',
    'section3/species_plant[:]/code',
    'section3/species_plant[:]/tax_code',
    'section3/species_plant[:]/name',
    'section3/species_other[:]/code',
    'section3/species_other[:]/tax_code',
    'section3/species_other[:]/scientific_name',
    'section4/designation',
    'section4/ownership',
    'section4/quality',
    'section4/vulnerability',
    'section4/documentation',
    'section5/national[:]/site_name',
    'section5/international[:]/name',
    'section5/corine[:]/code',
    'section6/management/organisation',
    'section6/management/plan',
]

Search = Ordered_dict_of(
    fl.String.named('text') \
             .with_properties(label=u'Text',
                              index=indexer(*full_text_fields, concat=True),
                              advanced=False),
    fl.Enum.named('habitat_class') \
           .valued(*sorted(habitat_class_map)) \
           .with_properties(label=u'Clase de habitat',
                            index=habitat_class_index,
                            widget='select',
                            value_labels=habitat_class_map),
    fl.Enum.named('nuts2') \
           .valued(*sorted(nuts2.keys())) \
           .with_properties(label=u'Regiune administrativă',
                            index=nuts2_index,
                            widget='select',
                            value_labels=nuts2,
                            facet=True),
    fl.Enum.named('nuts3') \
           .valued(*sorted(nuts3.keys())) \
           .with_properties(label=u'Județ',
                            index=indexer('section2/administrative[:]/code',
                                          concat=False, labels=False),
                            widget='select',
                            value_labels=nuts3,
                            facet=True),
    fl.Enum.named('type') \
           .valued('sci', 'spa') \
           .with_properties(label=u'Tip de document',
                            index=spa_sci_index,
                            widget='select',
                            value_labels={'sci': u"SCI", 'spa': u"SPA"},
                            facet=True),
    fl.Enum.named('bio_region') \
           .valued(*sorted(biogeographic_map.keys())) \
           .with_properties(label=u'Regiune biogeografică',
                            index=bio_region_index,
                            widget='select',
                            value_labels=biogeographic_map,
                            facet=True),
)


Statistics = Ordered_dict_of(*(Search.field_schema + (
    fl.Enum.named('compute') \
           .valued('area') \
           .with_properties(widget='hidden'),
)))
