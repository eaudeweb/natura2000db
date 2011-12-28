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
        element.add_error("Value must be numeric")
        return False

def valid_int(element, state):
    if element.value is None and element.optional:
        return True

    if isinstance(element.value, int):
        return True

    else:
        element.add_error("Value must be numeric (%r)" % element.optional)
        return False

def valid_type(element, state):
    patt = re.compile(r'^[a-k]$', re.IGNORECASE)
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error("Only one character from A to K is allowed")
        return False

def valid_year_month(element, state):
    patt = re.compile(r'^\d{6}$')
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error("Invalid date. Please use the YYYYMM format")
        return False

def valid_site_code(element, state):
    patt = re.compile(r'^\w{9}$')
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error("Invalid code")
        return False

def valid_any(element, state):
    for child in element.values():
        if child.value:
            return True
    element.add_error("Please choose at least one value")
    return False


from flatland.signals import validator_validated
from flatland.schema.base import NotEmpty
@validator_validated.connect
def validated(sender, element, result, **kwargs):
    if sender is NotEmpty:
        if not result:
            element.add_error("required")


def id_and_label(mapping):
    return dict((k, '%s (%s)' % (k, v)) for k, v in mapping.iteritems())


CommonFloat = fl.Float.using(optional=True, validators=[valid_float], format='%.2f')
CommonDate = fl.String.using(optional=True, validators=[valid_year_month])
CommonBoolean = fl.Boolean.using(optional=True).with_properties(widget='checkbox')
CommonString = fl.String.using(optional=True)
CommonEnum = fl.Enum.using(optional=True).with_properties(widget='select')
CommonList = fl.List.using(optional=True).with_properties(widget='table')
CommonGeoFloat = fl.Float.using(optional=True)

def Ordered_dict_of(*fields):
    order = [field.name for field in fields]
    return fl.Dict.of(*fields).with_properties(order=order)


InfoColumn = Ordered_dict_of(
    CommonEnum.named('population').valued('A', 'B', 'C', 'D').with_properties(label='Populatie'),
    CommonEnum.named('conservation').valued('A', 'B', 'C').with_properties(label='Conservare'),
    CommonEnum.named('isolation').valued('A', 'B', 'C').with_properties(label='Izolare'),
    CommonEnum.named('global_eval').valued('A', 'B', 'C').with_properties(label='Evaluare globala'),
    )


InfoTable = CommonList.of(
    Ordered_dict_of(

        CommonString.named('code').using(optional=False).with_properties(label='Cod'),
        CommonString.named('tax_code').with_properties(widget='hidden', label='Cod taxonomic'),
        CommonString.named('name').using(optional=False).with_properties(label='Nume'),

        Ordered_dict_of(

            CommonString.named('resident').with_properties(label='Residenta'),

            Ordered_dict_of(
                CommonString.named('reproduction').with_properties(label='Reproducere'),
                CommonString.named('wintering').with_properties(label='Iernat'),
                CommonString.named('passage').with_properties(label='Pasaj'),
                ).named('migratory').with_properties(label='Migratoare'),

            ).named('population').with_properties(label='Populatie'),

        InfoColumn.named('site_evaluation').with_properties(label='Evaluarea sitului'),

        ),
    )


section_1 = Ordered_dict_of(

    CommonString.named('type').using(optional=False, validators=[valid_type]).with_properties(label='Tip'),
    CommonString.named('code').using(optional=False, validators=[valid_site_code]).with_properties(label='Codul sitului'),

    CommonDate.named('date_document_add').using(optional=False).with_properties(label='Data completarii'),
    CommonDate.named('date_document_update').with_properties(label='Data actualizarii'),

    CommonList.named('other_sites').of(

        CommonString.using(validators=[valid_site_code]).with_properties(label='Coduri ale siturilor Natura 2000')

        ).with_properties(widget='list', label='Legaturi cu alte situri Natura 2000:'),

    CommonString.named('responsible').with_properties(widget='textarea', label='Responsabili'),

    CommonString.named('name').using(optional=False).with_properties(label='Numele sitului', widget='textarea'),

    Ordered_dict_of(
        CommonDate.named('proposal').with_properties(label='Data propunerii ca sit SCI'),
        CommonDate.named('confirmation_sci').with_properties(label='Data confirmarii ca sit SCI'),
        CommonDate.named('confirmation_spa').with_properties(label='Data confirmarii ca sit SPA'),
        CommonDate.named('confirmation_sac').with_properties(label='Data desemnarii ca sit SAC'),
        ).named('date') \
         .with_properties(label='Datele indicarii si desemnarii/clasificarii sitului',
                          widget='dict'),

    ).with_properties(label='1. IDENTIFICAREA SITULUI')


section_2 = Ordered_dict_of(

    CommonGeoFloat.named('longitude').with_properties(label='Longitudine'),
    CommonGeoFloat.named('latitude').with_properties(label='Latitudine'),

    CommonFloat.named('area').with_properties(label='Suprafata (ha)'),
    CommonFloat.named('length').with_properties(label='Lungimea sitului (km)'),

    Ordered_dict_of(
        CommonFloat.named('min').with_properties(label='Minima'),
        CommonFloat.named('max').with_properties(label='Maxima'),
        CommonFloat.named('mean').with_properties(label='Medie'),
        ).named('altitude').with_properties(label='Altitudine (m)', widget='dict'),

    CommonList.named('administrative').of(

        Ordered_dict_of(
            CommonString.named('code').with_properties(label='Codul NUTS'),
            CommonString.named('name').with_properties(label='Numele regiunii'),
            CommonString.named('coverage').with_properties(label='Pondere (%)'),
            ),

        ).using(optional=False).with_properties(label='Regiunea administrativa'),

    Ordered_dict_of(
        CommonBoolean.named('alpine').with_properties(label='Alpina'),
        CommonBoolean.named('continental').with_properties(label='Continentala'),
        CommonBoolean.named('steppic').with_properties(label='Stepica'),
        CommonBoolean.named('pontic').with_properties(label='Pontica'),
        CommonBoolean.named('pannonic').with_properties(label='Panonica'),
        ).named('biogeographic').using(validators=[valid_any]).with_properties(label='Regiunea biogeografica', widget='dict'),

    ).with_properties(label='2. LOCALIZAREA SITULUI')


section_3 = Ordered_dict_of(

    CommonList.named('habitat').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod'),
            CommonString.named('percentage').using(optional=False).with_properties(label='Pondere'),
            CommonEnum.named('representativeness').valued('A', 'B', 'C', 'D').with_properties(label='Reprezentativitate'),
            CommonEnum.named('relative_area').valued('A', 'B', 'C').with_properties(label='Suprafata relativa'),
            CommonEnum.named('conservation_status').valued('A', 'B', 'C').with_properties(label='Stare de conservare'),
            CommonEnum.named('global_evaluation').valued('A', 'B', 'C').with_properties(label='Evaluare globala'),
            ),

        ).with_properties(label='Tipuri de habitat prezente in sit si evaluarea sitului in ceea ce le priveste:'),

    InfoTable.named('species_bird').with_properties(label='Specii de pasari enumerate in anexa I la Directiva Consiliului 79/409/CEE'),
    InfoTable.named('species_bird_extra').with_properties(label='Specii de pasari cu migratie regulata nementionate in anexa I la Directiva Consiliului 79/409/CEE'),
    InfoTable.named('species_mammal').with_properties(label='Specii de mamifere enumerate in anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('species_reptile').with_properties(label='Specii de amfibieni si reptile enumerate in anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('species_fish').with_properties(label='Specii de pesti enumerate in anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('species_invertebrate').with_properties(label='Specii de nevertebrate enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    CommonList.named('species_plant').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod'),
            CommonString.named('tax_code').with_properties(widget='hidden', label='Cod taxonomic'),
            CommonString.named('name').using(optional=False).with_properties(label='Nume'),
            CommonString.named('population').with_properties(label='Populatie'),
            InfoColumn.named('site_evaluation').with_properties(label='Evaluarea sitului'),
            ),

        ).with_properties(label='Specii de plante enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    CommonList.named('species_other').of(
        Ordered_dict_of(

            CommonEnum.named('category') \
                      .with_properties(optional=False) \
                      .valued('bird', 'mammal', 'amphibian', 'reptile', 'fish', 'invertebrate', 'plant') \
                      .with_properties(label='Categorie'),

            CommonString.named('code').with_properties(label='Cod'),
            CommonString.named('tax_code').with_properties(widget='hidden', label='Cod taxonomic'),
            CommonString.named('scientific_name').using(optional=False).with_properties(label='Denumire stiintifica'),

            Ordered_dict_of(
                CommonString.named('text'),
                CommonEnum.named('trend').valued('A', 'B', 'C', 'D'),
                ).named('population').with_properties(label='Populatie'),

            ),

        ).with_properties(label='Alte specii importante de flora si fauna'),

    ).with_properties(label='3. INFORMATII ECOLOGICE')


habitat_class_map = _load_json('reference/habitat_ro.json')


section_4 = Ordered_dict_of(

    Ordered_dict_of(

        Ordered_dict_of(
            *[CommonFloat.named(key).with_properties(label=habitat_class_map[key])
              for key in sorted(habitat_class_map)]
            ).named('habitat') \
             .using(optional=True) \
             .with_properties(label='Clase de habitat', widget='habitat_breakdown'),

        CommonString.named('other').with_properties(label='Alte caracteristici ale sitului', widget='textarea'),

        ).named('characteristics') \
         .using(optional=True) \
         .with_properties(label='Caracteristici generale ale sitului', widget='dict'),

    CommonString.named('quality').with_properties(widget='textarea', label='Calitate si importanta'),
    CommonString.named('vulnerability').with_properties(widget='textarea', label='Vulnerabilitate'),
    CommonString.named('designation').with_properties(widget='textarea', label='Desemnarea sitului (vezi observatiile privind datele cantitative de mai jos)'),
    CommonString.named('ownership').with_properties(widget='textarea', label='Tip de proprietate'),
    CommonString.named('documentation').with_properties(widget='textarea', label='Documentatie'),

    CommonList.named('history').of(

        Ordered_dict_of(
            CommonString.named('date').with_properties(label='Data'),
            CommonString.named('field').with_properties(label='Campul modificat'),
            CommonString.named('description').with_properties(label='Descriere'),
            ),

        ).with_properties(label='Istoric (se va completa de catre Comisie)'),

    ).with_properties(label='4. DESCRIEREA SITULUI')


international_classification_map = _load_json('reference/international_ro.json')


classification_map = _load_json('reference/classification_ro.json')


section_5 = Ordered_dict_of(

    CommonList.named('clasification').of(

        Ordered_dict_of(

            CommonEnum.named('code') \
                      .with_properties(optional=False) \
                      .valued(*sorted(classification_map.keys())) \
                      .with_properties(label='Cod',
                                       value_labels=id_and_label(classification_map)),
            CommonFloat.named('percentage').with_properties(label='Pondere %'),
            ),

        ).with_properties(label='Clasificare la nivel national si regional'),

    CommonList.named('national').of(

        Ordered_dict_of(
            CommonString.named('type').with_properties(label='Tip'),
            CommonString.named('site_name').using(optional=False).with_properties(label='Numele sitului'),
            CommonString.named('site_type').with_properties(label='Tipul sitului'),
            CommonFloat.named('overlap').with_properties(label='Suprapunere %'),
            ),

        ).with_properties(label='Relatiile sitului descris cu alte situri - desemnate la nivel national sau regional'),

    CommonList.named('international').of(

        Ordered_dict_of(
            CommonEnum.named('type') \
                      .valued(*[k for k,v in international_classification_map]) \
                      .with_properties(label='Tip'),
            CommonString.named('site_name').using(optional=False).with_properties(label='Numele sitului'),
            CommonString.named('site_type').with_properties(label='Tipul sitului'),
            CommonFloat.named('overlap').with_properties(label='Suprapunere %'),
            ),

        ).with_properties(label='Relatiile sitului descris cu alte situri - desemnate la nivel international'),

    CommonList.named('corine').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod sit Corine'),
            CommonString.named('type').with_properties(label='Tip'),
            CommonFloat.named('overlap').with_properties(label='Suprapunere %'),
            ),

        ).with_properties(label='Relatiile sitului descris cu biotopuri Corine'),

    ).with_properties(label='5. STATUTUL DE PROTECTIE AL SITULUI SI LEGATURA CU BIOTOPURILE CORINE')


antropic_activities_map = _load_json('reference/activities_ro.json')


antropic_activity = Ordered_dict_of(
    CommonEnum.named('code') \
              .using(optional=False) \
              .valued(*sorted(antropic_activities_map.keys())) \
              .with_properties(label='Cod',
                               value_labels=id_and_label(antropic_activities_map)),
    CommonEnum.named('intensity').valued('A', 'B', 'C').with_properties(label='Intensitate'),
    CommonFloat.named('percentage').with_properties(label='% din sit'),
    CommonEnum.named('influence').valued('+', '0', '-').with_properties(label='Influenta'),
    )


section_6 = Ordered_dict_of(

    Ordered_dict_of(

        CommonList.named('internal').of(antropic_activity) \
            .with_properties(label='Activitati si consecinte in interiorul sitului'),

        CommonList.named('external').of(antropic_activity) \
            .with_properties(label='Activitati si consecinte in jurul sitului'),

        ).named('activity') \
         .with_properties(widget='dict', label="Activitati antropice, consecintele lor generale si suprafata din sit afectata"),

    Ordered_dict_of(
        CommonString.named('organisation').with_properties(widget='textarea', label='Organismul responsabil pentru managementul sitului'),
        CommonString.named('plan').with_properties(widget='textarea', label='Planuri de management al sitului'),
        ).named('management') \
         .with_properties(widget='dict', label="Managementul sitului"),

    ).with_properties(label='6. ACTIVITATILE ANTROPICE SI EFECTELE LOR IN SIT SI IN JURUL ACESTUIA')


section_7 = Ordered_dict_of(

    CommonList.named('map').of(

        Ordered_dict_of(
            CommonString.named('number').with_properties(label='Numar national harta'),
            CommonString.named('scale').with_properties(label='Scara'),
            CommonString.named('projection').with_properties(label='Proiectie'),
            ).with_properties(widget='dict'),

        ).with_properties(widget='list', label='Harta fizica'),

    CommonString.named('limits').with_properties(widget='textarea', label='Specificati daca limitele sitului sunt disponibile in format digital'),

    ).with_properties(label='7. HARTA SITULUI')


SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'),
    section_3.named('section3').with_properties(widget='section'),
    section_4.named('section4').with_properties(widget='section'),
    section_5.named('section5').with_properties(widget='section'),
    section_6.named('section6').with_properties(widget='section'),
    section_7.named('section7').with_properties(widget='section'))



def indexer(*paths, **kwargs):
    def values(doc):
        for p in paths:
            for element in doc.find(p):
                value = element.value
                if value:
                    yield value

    def index(doc):
        if kwargs.get('concat', False):
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
    return ' '.join(out)


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


full_text_fields = [
    'section1/name',
    'section1/code',
    'section1/responsible',
    'section2/administrative[:]/code',
    'section2/administrative[:]/name',
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
             .with_properties(label='Text',
                              index=indexer(*full_text_fields),
                              advanced=False),
    fl.Enum.named('habitat_class') \
           .valued(*sorted(habitat_class_map)) \
           .with_properties(label='Clase de habitat',
                            index=habitat_class_index,
                            widget='select',
                            value_labels=habitat_class_map),
    fl.String.named('regcod') \
             .with_properties(label='Regiune administrativa',
                              index=indexer('section2/administrative[:]/code',
                                            concat=False),
                              facet=True),
    fl.Enum.named('type') \
             .valued('sci', 'spa') \
             .with_properties(label='Tip de document',
                              index=spa_sci_index,
                              widget='select',
                              facet=True),
    fl.String.named('bio_region') \
             .with_properties(label='Regiune biogeografica',
                              index=bio_region_index,
                              facet=True),
)
