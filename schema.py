import re
import flatland as fl


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

        InfoColumn.named('sit_evaluation').with_properties(label='Evaluarea sitului'),

        ).named('dict_name'),
    )


section_1 = Ordered_dict_of(

    CommonString.named('type').using(optional=False, validators=[valid_type]).with_properties(label='Tip'),
    CommonString.named('sitecode').using(optional=False, validators=[valid_site_code]).with_properties(label='Codul sitului'),

    CommonDate.named('date').using(optional=False).with_properties(label='Data completarii'),
    CommonDate.named('update').with_properties(label='Data actualizarii'),

    CommonList.named('other_sites').of(

        CommonString.named('other_site').using(validators=[valid_site_code]).with_properties(label='Coduri ale siturilor Natura 2000')

        ).with_properties(widget='list', label='Legaturi cu alte situri Natura 2000:'),

    CommonString.named('respondent').with_properties(widget='textarea', label='Responsabili'),

    CommonString.named('site_name').using(optional=False).with_properties(label='Numele sitului', widget='textarea'),

    Ordered_dict_of(
        CommonDate.named('date_prop').with_properties(label='Data propunerii ca sit SCI'),
        CommonDate.named('date_con').with_properties(label='Data confirmarii ca sit SCI'),
        CommonDate.named('spa_date').with_properties(label='Data confirmarii ca sit SPA'),
        CommonDate.named('sac_date').with_properties(label='Data desemnarii ca sit SAC'),
        ).named('sit_dates') \
         .with_properties(label='Datele indicarii si desemnarii/clasificarii sitului',
                          widget='dict'),

    ).with_properties(label='1. IDENTIFICAREA SITULUI')


section_2 = Ordered_dict_of(

    CommonGeoFloat.named('longitude').with_properties(label='Longitudine'),
    CommonGeoFloat.named('latitude').with_properties(label='Latitudine'),

    CommonFloat.named('area').with_properties(label='Suprafata (ha)'),
    CommonFloat.named('length').with_properties(label='Lungimea sitului (km)'),

    Ordered_dict_of(
        CommonFloat.named('alt_min').with_properties(label='Minima'),
        CommonFloat.named('alt_max').with_properties(label='Maxima'),
        CommonFloat.named('alt_mean').with_properties(label='Medie'),
        ).named('altitude').with_properties(label='Altitudine (m)', widget='dict'),

    CommonList.named('regcod').of(

        Ordered_dict_of(
            CommonString.named('reg_code').with_properties(label='Codul NUTS'),
            CommonString.named('reg_name').with_properties(label='Numele regiunii'),
            CommonString.named('cover').with_properties(label='Pondere (%)'),
            ),

        ).using(optional=False).with_properties(label='Regiunea administrativa'),

    Ordered_dict_of(
        CommonBoolean.named('alpine').with_properties(label='Alpina'),
        CommonBoolean.named('continent').with_properties(label='Continentala'),
        CommonBoolean.named('steppic').with_properties(label='Stepica'),
        CommonBoolean.named('pontic').with_properties(label='Pontica'),
        CommonBoolean.named('pannonic').with_properties(label='Panonica'),
        ).named('bio_region').using(validators=[valid_any]).with_properties(label='Regiunea biogeografica', widget='dict'),

    ).with_properties(label='2. LOCALIZAREA SITULUI')


section_3 = Ordered_dict_of(

    CommonList.named('habitat_types').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod'),
            CommonString.named('percentage').using(optional=False).with_properties(label='Pondere'),
            CommonEnum.named('repres').valued('A', 'B', 'C', 'D').with_properties(label='Reprezentativitate'),
            CommonEnum.named('relativ_area').valued('A', 'B', 'C').with_properties(label='Suprafata relativa'),
            CommonEnum.named('conservation_status').valued('A', 'B', 'C').with_properties(label='Stare de conservare'),
            CommonEnum.named('global_evaluation').valued('A', 'B', 'C').with_properties(label='Evaluare globala'),
            ).named('habitat_type'),

        ).with_properties(label='Tipuri de habitat prezente in sit si evaluarea sitului in ceea ce le priveste:'),

    InfoTable.named('bird_types').with_properties(label='Specii de pasari enumerate in anexa I la Directiva Consiliului 79/409/CEE'),
    InfoTable.named('bird_types_extra').with_properties(label='Specii de pasari cu migratie regulata nementionate in anexa I la Directiva Consiliului 79/409/CEE'),
    InfoTable.named('mammals_types').with_properties(label='Specii de mamifere enumerate in anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('reptiles_types').with_properties(label='Specii de amfibieni si reptile enumerate in anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('fishes_types').with_properties(label='Specii de pesti enumerate in anexa II la Directiva Consiliului 92/43/CEE'),
    InfoTable.named('invertebrates_types').with_properties(label='Specii de nevertebrate enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    CommonList.named('plants_types').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod'),
            CommonString.named('tax_code').with_properties(widget='hidden', label='Cod taxonomic'),
            CommonString.named('name').using(optional=False).with_properties(label='Nume'),
            CommonString.named('population').with_properties(label='Populatie'),
            InfoColumn.named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('plant_types'),

        ).with_properties(label='Specii de plante enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    CommonList.named('other_species').of(
        Ordered_dict_of(

            CommonEnum.named('category') \
                      .with_properties(optional=False) \
                      .valued('pasari', 'mamifere', 'amfibieni', 'reptile', 'pesti', 'nevertebrate', 'plante') \
                      .with_properties(label='Categorie'),

            CommonString.named('code').with_properties(label='Cod'),
            CommonString.named('tax_code').with_properties(widget='hidden', label='Cod taxonomic'),
            CommonString.named('scientific_name').using(optional=False).with_properties(label='Denumire stiintifica'),

            Ordered_dict_of(
                CommonString.named('population_text'),
                CommonEnum.named('population_trend').valued('A', 'B', 'C', 'D'),
                ).named('population').with_properties(label='Populatie'),

            ).named('other_specie'),

        ).with_properties(label='Alte specii importante de flora si fauna'),

    ).with_properties(label='3. INFORMATII ECOLOGICE')


habitat_class_map = {
    'N01': u"Arii marine, privaluri",
    'N02': u"Rauri (fluvii) afectate de maree, estuare, terase mlastinoase sau nisipoase, lagune(inclusiv bazinele de colectare a sarii)",
    'N03': u"Suprafete saraturate (mlastini, pajisti, stepe)",
    'N04': u"Dune de coasta, plaje cu nisip, machair",
    'N05': u"Litoral cu prundis, faleze, insulite",
    'N06': u"Ape dulci continentale (statatoare, curgatoare)",
    'N07': u"Mlastini (vegetatie de centura), smarcuri, turbarii",
    'N08': u"Lande, tufarisuri, maquis si garigue, phrygana",
    'N09': u"Pajisti uscate, stepe",
    'N10': u"Pajisti seminaturale umede, preerii mezofile",
    'N11': u"Pajisti alpine si subalpine",
    'N12': u"Culturi cerealiere extensive (inclusiv culturile de rotatie cu dezmiristire)",
    'N13': u"Orezarii",
    'N14': u"Pajisti ameliorate",
    'N15': u"Alte terenuri arabile",
    'N16': u"Paduri caducifoliate",
    'N17': u"Paduri de conifere",
    'N18': u"Paduri semperviriscente de nerasinoase",
    'N19': u"Paduri mixte",
    'N20': u"Paduri de monocultura (plopi sau arbori exotici)",
    'N21': u"Plantatii de arbori sau plante lemnoase (inclusiv livezi, cranguri, vii, dehesas)",
    'N22': u"Stancarii interioare, grohotisuri, dune interioare, zone cu zapezi si gheturi vesnice",
    'N23': u"Alte terenuri (inclusiv zone urbane, rurale, cai de comunicatie, rampe de depozitare, mine, zone industriale)",
    'N26': u"Habitate de paduri (paduri in tranzitie)",
}


section_4 = Ordered_dict_of(

    Ordered_dict_of(

        Ordered_dict_of(
            *[CommonFloat.named(key).with_properties(label=habitat_class_map[key])
              for key in sorted(habitat_class_map)]
            ).named('habitat_classes') \
             .using(optional=True) \
             .with_properties(label='Clase de habitat', widget='habitat_breakdown'),

        CommonString.named('other').with_properties(label='Alte caracteristici ale sitului', widget='textarea'),

        ).named('site_characteristics') \
         .using(optional=True) \
         .with_properties(label='Caracteristici generale ale sitului', widget='dict'),

    CommonString.named('quality').with_properties(widget='textarea', label='Calitate si importanta'),
    CommonString.named('vulnar').with_properties(widget='textarea', label='Vulnerabilitate'),
    CommonString.named('design').with_properties(widget='textarea', label='Desemnarea sitului (vezi observatiile privind datele cantitative de mai jos)'),
    CommonString.named('owner').with_properties(widget='textarea', label='Tip de proprietate'),
    CommonString.named('docum').with_properties(widget='textarea', label='Documentatie'),

    CommonList.named('history').of(

        Ordered_dict_of(
            CommonString.named('date').with_properties(label='Data'),
            CommonString.named('modified_field').with_properties(label='Campul modificat'),
            CommonString.named('description').with_properties(label='Descriere'),
            ).named('record'),

        ).with_properties(label='Istoric (se va completa de catre Comisie)'),

    ).with_properties(label='4. DESCRIEREA SITULUI')


section_5 = Ordered_dict_of(

    CommonList.named('clasification').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod'),
            CommonFloat.named('percentage').with_properties(label='Pondere %'),
            ).named('record'),

        ).with_properties(label='Clasificare la nivel national si regional'),

    CommonList.named('national_relations').of(

        Ordered_dict_of(
            CommonString.named('type').with_properties(label='Tip'),
            CommonString.named('name').using(optional=False).with_properties(label='Numele sitului'),
            CommonString.named('sit_type').with_properties(label='Tip'),
            CommonFloat.named('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),

        ).with_properties(label='Relatiile sitului descris cu alte situri - desemnate la nivel national sau regional'),

    CommonList.named('international_relations').of(

        Ordered_dict_of(
            CommonEnum.named('type') \
                      .valued('Conventia Ramsar', 'Rezervatia biogenetica', 'Sit Eurodiploma', 'Rezervatia biosferei',
                              'Conventia Barcelona', 'Sit patrimoniu mondial', 'Altele') \
                      .with_properties(label='Tip'),
            CommonString.named('name').using(optional=False).with_properties(label='Numele sitului'),
            CommonString.named('sit_type').with_properties(label='Tip'),
            CommonFloat.named('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),

        ).with_properties(label='Relatiile sitului descris cu alte situri - desemnate la nivel international'),

    CommonList.named('corine_relations').of(

        Ordered_dict_of(
            CommonString.named('code').using(optional=False).with_properties(label='Cod sit Corine'),
            CommonString.named('type').with_properties(label='Tip'),
            CommonFloat.named('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),

        ).with_properties(label='Relatiile sitului descris cu biotopuri Corine'),

    ).with_properties(label='5. STATUTUL DE PROTECTIE AL SITULUI SI LEGATURA CU BIOTOPURILE CORINE')


section_6 = Ordered_dict_of(

    Ordered_dict_of(

        CommonList.named('inside_activities').of(

            Ordered_dict_of(
                CommonString.named('code').using(optional=False).with_properties(label='Cod'),
                CommonEnum.named('intensity').valued('A', 'B', 'C').with_properties(label='Intensitate'),
                CommonFloat.named('percentage').with_properties(label='% din sit'),
                CommonEnum.named('influence').valued('+', '0', '-').with_properties(label='Influenta'),
                ).named('record'),

            ).with_properties(label='Activitati si consecinte in interiorul sitului'),

        CommonList.named('outside_activities').of(

            Ordered_dict_of(
                CommonString.named('code').using(optional=False).with_properties(label='Cod'),
                CommonEnum.named('intensity').valued('A', 'B', 'C').with_properties(label='Intensitate'),
                CommonFloat.named('percentage').with_properties(label='% din sit'),
                CommonEnum.named('influence').valued('+', '0', '-').with_properties(label='Influenta'),
                ).named('record'),

            ).with_properties(label='Activitati si consecinte in jurul sitului'),

        ).named('in_jur') \
         .with_properties(widget='dict', label="Activitati antropice, consecintele lor generale si suprafata din sit afectata"),

    Ordered_dict_of(
        CommonString.named('manager').with_properties(widget='textarea', label='Organismul responsabil pentru managementul sitului'),
        CommonString.named('managpl').with_properties(widget='textarea', label='Planuri de management al sitului'),
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

    CommonString.named('site_limits').with_properties(widget='textarea', label='Specificati daca limitele sitului sunt disponibile in format digital'),

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
    bio_regions = doc['section2']['bio_region'].value
    out = []
    for name in bio_regions:
        if bio_regions[name]:
            out.append(name)
    return ' '.join(out)


def habitat_class_index(doc):
    hc_element = doc['section4']['site_characteristics']['habitat_classes']
    return [element.name for element in hc_element.children if element.value]


def spa_sci_index(doc):
    doc_id = doc['section1']['sitecode'].value
    if doc_id[2:5] == 'SPA':
        return 'spa'
    elif doc_id[2:5] == 'SCI':
        return 'sci'
    else:
        raise ValueError('unkown document type (spa/sci) %r' % doc_id)


full_text_fields = [
    'section1/site_name',
    'section1/sitecode',
    'section1/respondent',
    'section2/regcod[:]/reg_code',
    'section2/regcod[:]/reg_name',
    'section3/habitat_types[:]/code',
    'section3/bird_types[:]/code',
    'section3/bird_types[:]/tax_code',
    'section3/bird_types[:]/name',
    'section3/bird_types_extra[:]/code',
    'section3/bird_types_extra[:]/tax_code',
    'section3/bird_types_extra[:]/name',
    'section3/mammals_types[:]/code',
    'section3/mammals_types[:]/tax_code',
    'section3/mammals_types[:]/name',
    'section3/reptiles_types[:]/code',
    'section3/reptiles_types[:]/tax_code',
    'section3/reptiles_types[:]/name',
    'section3/fishes_types[:]/code',
    'section3/fishes_types[:]/tax_code',
    'section3/fishes_types[:]/name',
    'section3/invertebrates_types[:]/code',
    'section3/invertebrates_types[:]/tax_code',
    'section3/invertebrates_types[:]/name',
    'section3/plants_types[:]/code',
    'section3/plants_types[:]/tax_code',
    'section3/plants_types[:]/name',
    'section3/other_species[:]/code',
    'section3/other_species[:]/tax_code',
    'section3/other_species[:]/scientific_name',
    'section4/design',
    'section4/owner',
    'section4/quality',
    'section4/vulnar',
    'section4/docum',
    'section5/national_relations[:]/name',
    'section5/international_relations[:]/name',
    'section5/corine_relations[:]/code',
    'section6/management/manager',
    'section6/management/managpl',
]

Search = Ordered_dict_of(
    fl.String.named('text') \
             .with_properties(label='Text',
                              index=indexer(*full_text_fields)),
    fl.Enum.named('habitat_class') \
           .valued(*sorted(habitat_class_map)) \
           .with_properties(label='Clase de habitat',
                            index=habitat_class_index,
                            widget='select',
                            value_labels=habitat_class_map,
                            advanced=True),
    fl.String.named('regcod') \
             .with_properties(label='Regiune administrativa',
                              index=indexer('section2/regcod[:]/reg_code',
                                            concat=False),
                              widget='facets',
                              facet=True),
    fl.String.named('type') \
             .with_properties(label='Tip de document',
                              index=spa_sci_index,
                              widget='facets',
                              facet=True),
    fl.String.named('bio_region') \
             .with_properties(label='Regiune biogeografica',
                              index=bio_region_index,
                              widget='facets',
                              facet=True),
)
