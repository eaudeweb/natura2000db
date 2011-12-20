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

def valid_date(element, state):
    patt = re.compile(r'^\d{6}$')
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error("Invalid date. Please use the YYYYMM format")
        return False

def valid_code(element, state):
    patt = re.compile(r'^\w{9}$')
    if element.value is not None and patt.match(element.value):
        return True

    else:
        element.add_error("Invalid code")
        return False

def valid_dict_value(element, state):
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


def Float_using(name, optional=True):
    return fl.Float.named(name).using(optional=optional, validators=[valid_float], format='%.2f')

def Date_using(name, optional=True):
    return fl.String.named(name).using(optional=optional, validators=[valid_date])

def Boolean_using(name, optional=True):
    return fl.Boolean.named(name).using(optional=optional)

def String_using(name, optional=True):
    return fl.String.named(name).using(optional=optional)

def Enum_using(name, optional=True):
    return fl.Enum.named(name).using(optional=optional)

def Ordered_dict_of(*fields):
    order = [field.name for field in fields]
    return fl.Dict.of(*fields).with_properties(order=order)

def InfoColumn(name, label):
    return Ordered_dict_of(
                Enum_using('population').valued('A', 'B', 'C', 'D').with_properties(label='Populatie', widget='select'),
                Enum_using('conservation').valued('A', 'B', 'C').with_properties(label='Conservare', widget='select'),
                Enum_using('isolation').valued('A', 'B', 'C').with_properties(label='Izolare', widget='select'),
                Enum_using('global_eval').valued('A', 'B', 'C').with_properties(label='Evaluare globala', widget='select'),
            ).named(name).with_properties(label=label)

def InfoTable(list_name, dict_name):
    return fl.List.named(list_name).of(
                Ordered_dict_of(

                        String_using('code', optional=False).with_properties(label='Cod'),
                        String_using('name', optional=False).with_properties(label='Nume'),

                        Ordered_dict_of(

                            String_using('resident').with_properties(label='Residenta'),
                            Ordered_dict_of(
                                String_using('reproduction').with_properties(label='Reproducere'),
                                String_using('wintering').with_properties(label='Iernat'),
                                String_using('passage').with_properties(label='Pasaj'),
                                ).named('migratory').with_properties(label='Migratoare'),

                            ).named('population').with_properties(label='Populatie'),

                        InfoColumn('sit_evaluation', label='Evaluarea sitului'),

                    ).named('dict_name'),
                )


section_1 = Ordered_dict_of(

    String_using('type', optional=False).using(validators=[valid_type]).with_properties(label='Tip'),
    String_using('sitecode', optional=False).using(validators=[valid_code]).with_properties(label='Codul sitului'),

    Date_using('date', optional=False).with_properties(label='Data completarii'),
    Date_using('update').with_properties(label='Data actualizarii'),
    # TODO validator to ensure update >= date

    fl.List.named('other_sites').of(
            String_using('other_site').using(validators=[valid_code]).with_properties(label='Coduri ale siturilor Natura 2000')
        ).using(optional=True).
          with_properties(widget='list', label='Legaturi cu alte situri Natura 2000:'),

    String_using('respondent').with_properties(widget='textarea', label='Responsabili'),

    String_using('site_name', optional=False).with_properties(label='Numele sitului', widget='textarea'),

    Ordered_dict_of(
            Date_using('date_prop').with_properties(label='Data propunerii ca sit SCI'),
            Date_using('date_con').with_properties(label='Data confirmarii ca sit SCI'),
            Date_using('spa_date').with_properties(label='Data confirmarii ca sit SPA'),
            Date_using('sac_date').with_properties(label='Data desemnarii ca sit SAC'),

        ).named('sit_dates').with_properties(label='Datele indicarii si desemnarii/clasificarii sitului', widget='dict'),

    ).with_properties(label='1. IDENTIFICAREA SITULUI')

section_2 = Ordered_dict_of(

    fl.Float.named('longitude').using(optional=True).
                                with_properties(label='Longitudine'),
    fl.Float.named('latitude').using(optional=True).
                               with_properties(label='Latitudine'),

    Float_using('area').with_properties(label='Suprafata (ha)'),
    Float_using('length').with_properties(label='Lungimea sitului (km)'),

    Ordered_dict_of(
            Float_using('alt_min').with_properties(label='Minima'),
            Float_using('alt_max').with_properties(label='Maxima'),
            Float_using('alt_mean').with_properties(label='Medie'),

        ).named('altitude').with_properties(label='Altitudine (m)', widget='dict'),

    fl.List.named('regcod').of(
        Ordered_dict_of(
                String_using('reg_code').with_properties(label='Codul NUTS'),
                String_using('reg_name').with_properties(label='Numele regiunii'),
                String_using('cover').with_properties(label='Pondere (%)'),
            ),
        ).with_properties(label='Regiunea administrativa', widget='dict'),

    Ordered_dict_of(
            Boolean_using('alpine').with_properties(label='Alpina', widget='checkbox'),
            Boolean_using('continent').with_properties(label='Continentala', widget='checkbox'),
            Boolean_using('steppic').with_properties(label='Stepica', widget='checkbox'),
            Boolean_using('pontic').with_properties(label='Pontica', widget='checkbox'),
            Boolean_using('pannonic').with_properties(label='Panonica', widget='checkbox'),

        ).named('bio_region').using(validators=[valid_dict_value]).with_properties(label='Regiunea biogeografica', widget='dict'),

    ).with_properties(label='2. LOCALIZAREA SITULUI')

section_3 = Ordered_dict_of(

    fl.List.named('habitat_types').of(

        Ordered_dict_of(
                String_using('code', optional=False).with_properties(label='Cod'),
                String_using('percentage', optional=False).with_properties(label='Pondere'),
                Enum_using('repres').valued('A', 'B', 'C', 'D').with_properties(label='Reprezentativitate', widget='select'),
                Enum_using('relativ_area').valued('A', 'B', 'C').with_properties(label='Suprafata relativa', widget='select'),
                Enum_using('conservation_status').valued('A', 'B', 'C').with_properties(label='Stare de conservare', widget='select'),
                Enum_using('global_evaluation').valued('A', 'B', 'C').with_properties(label='Evaluare globala', widget='select'),

            ).named('habitat_type'),

        ).using(optional=True).
          with_properties(widget='table', label='Tipuri de habitat prezente in sit si evaluarea sitului in ceea ce le priveste:'),

    InfoTable(list_name='species_types', dict_name='specie_type').
            using(optional=True).
            with_properties(widget='table', label='Specii de pasari enumerate in anexa I la Directiva Consiliului 79/409/CEE'),

    InfoTable(list_name='migratory_species_types', dict_name='migratory_specie_type').
            using(optional=True).
            with_properties(widget='table', label='Specii de pasari cu migratie regulata nementionate in anexa I la Directiva Consiliului 79/409/CEE'),

    InfoTable(list_name='mammals_types', dict_name='mammal_types').
            using(optional=True).
            with_properties(widget='table', label='Specii de mamifere enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    InfoTable(list_name='reptiles_types', dict_name='reptile_types').
            using(optional=True).
            with_properties(widget='table', label='Specii de amfibieni si reptile enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    InfoTable(list_name='fishes_types', dict_name='fish_types').
            using(optional=True).
            with_properties(widget='table', label='Specii de pesti enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    InfoTable(list_name='invertebrates_types', dict_name='invertebrate_types').
            using(optional=True).
            with_properties(widget='table', label='Specii de nevertebrate enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('plants_types').of(
        Ordered_dict_of(
                String_using('code', optional=False).with_properties(label='Cod'),
                String_using('name', optional=False).with_properties(label='Nume'),
                String_using('population').with_properties(label='Populatie'),
                InfoColumn('sit_evaluation', label='Evaluarea sitului'),

            ).named('plant_types'),
        ).using(optional=True).
          with_properties(widget='table', label='Specii de plante enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('other_species').of(
        Ordered_dict_of(

                Enum_using('category', optional=False).valued('pasari', 'mamifere', 'amfibieni', 'reptile', 'pesti', 'nevertebrate', 'plante').
                                        with_properties(label='Categorie', widget='select'),
                String_using('scientific_name', optional=False).with_properties(label='Denumire stiintifica'),

                Ordered_dict_of(
                        String_using('population_text').with_properties(label='Populatie'),
                        Enum_using('population_trend').valued('A', 'B', 'C', 'D').with_properties(label='Populatie', widget='select'),

                    ).named('population').with_properties(label='Populatie'),
            ).named('other_specie'),
        ).using(optional=True).
          with_properties(widget='table', label='Alte specii importante de flora si fauna'),

    ).with_properties(label='3. INFORMATII ECOLOGICE')

section_4 = Ordered_dict_of(

    Ordered_dict_of(

        Ordered_dict_of(

                Float_using('N01').with_properties(label='Arii marine, privaluri'),
                Float_using('N02').with_properties(label='Rauri (fluvii) afectate de maree, estuare, terase mlastinoase sau nisipoase, lagune(inclusiv bazinele de colectare a sarii)'),
                Float_using('N03').with_properties(label='Suprafete saraturate (mlastini, pajisti, stepe)'),
                Float_using('N04').with_properties(label='Dune de coasta, plaje cu nisip, machair'),
                Float_using('N05').with_properties(label='Litoral cu prundis, faleze, insulite'),
                Float_using('N06').with_properties(label='Ape dulci continentale (statatoare, curgatoare)'),
                Float_using('N07').with_properties(label='Mlastini (vegetatie de centura), smarcuri, turbarii'),
                Float_using('N08').with_properties(label='Lande, tufarisuri, maquis si garigue, phrygana'),
                Float_using('N09').with_properties(label='Pajisti uscate, stepe'),
                Float_using('N10').with_properties(label='Pajisti seminaturale umede, preerii mezofile'),
                Float_using('N11').with_properties(label='Pajisti alpine si subalpine'),
                Float_using('N12').with_properties(label='Culturi cerealiere extensive (inclusiv culturile de rotatie cu dezmiristire)'),
                Float_using('N13').with_properties(label='Orezarii'),
                Float_using('N14').with_properties(label='Pajisti ameliorate'),
                Float_using('N15').with_properties(label='Alte terenuri arabile'),
                Float_using('N16').with_properties(label='Paduri caducifoliate'),
                Float_using('N17').with_properties(label='Paduri de conifere'),
                Float_using('N18').with_properties(label='Paduri semperviriscente de nerasinoase'),
                Float_using('N19').with_properties(label='Paduri mixte'),
                Float_using('N20').with_properties(label='Paduri de monocultura (plopi sau arbori exotici)'),
                Float_using('N21').with_properties(label='Plantatii de arbori sau plante lemnoase (inclusiv livezi, cranguri, vii, dehesas)'),
                Float_using('N22').with_properties(label='Stancarii interioare, grohotisuri, dune interioare, zone cu zapezi si gheturi vesnice'),
                Float_using('N23').with_properties(label='Alte terenuri (inclusiv zone urbane, rurale, cai de comunicatie, rampe de depozitare, mine, zone industriale)'),
                Float_using('N26').with_properties(label='Habitate de paduri (paduri in tranzitie)'),
            ).named('habitat_classes').
              using(optional=True).
              with_properties(label='Clase de habitat', widget='habitat_breakdown'),
        String_using('other').with_properties(label='Alte caracteristici ale sitului', widget='textarea'),

        ).named('site_characteristics').
          using(optional=True).
          with_properties(label='Caracteristici generale ale sitului', widget='dict'),

    String_using('quality').with_properties(widget='textarea', label='Calitate si importanta'),
    String_using('vulnar').with_properties(widget='textarea', label='Vulnerabilitate'),
    String_using('design').with_properties(widget='textarea', label='Desemnarea sitului (vezi observatiile privind datele cantitative de mai jos)'),
    String_using('owner').with_properties(widget='textarea', label='Tip de proprietate'),
    String_using('docum').with_properties(widget='textarea', label='Documentatie'),

    fl.List.named('history').of(
        Ordered_dict_of(

                String_using('date').with_properties(label='Data'),
                String_using('modified_field').with_properties(label='Campul modificat'),
                String_using('description').with_properties(label='Descriere'),
            ).named('record'),
        ).using(optional=True).
          with_properties(widget='table', label='Istoric (se va completa de catre Comisie)'),
    ).with_properties(label='4. DESCRIEREA SITULUI')

section_5 = Ordered_dict_of(

    fl.List.named('clasification').of(
        Ordered_dict_of(
                String_using('code', optional=False).with_properties(label='Cod'),
                Float_using('percentage').with_properties(label='Pondere %'),
            ).named('record'),
        ).using(optional=True).
          with_properties(widget='table', label='Clasificare la nivel national si regional'),

    fl.List.named('national_relations').of(
        Ordered_dict_of(

                String_using('type').with_properties(label='Tip'),
                String_using('name', optional=False).with_properties(label='Numele sitului'),
                String_using('sit_type').with_properties(label='Tip'),
                Float_using('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),
        ).using(optional=True).
          with_properties(widget='table', label='Relatiile sitului descris cu alte situri - desemnate la nivel national sau regional'),

    fl.List.named('international_relations').of(
        Ordered_dict_of(

                Enum_using('type').valued('Conventia Ramsar', 'Rezervatia biogenetica', 'Sit Eurodiploma', 
                                            'Rezervatia biosferei', 'Conventia Barcelona', 'Sit patrimoniu mondial', 
                                            'Altele').with_properties(label='Tip', widget='select'),
                String_using('name', optional=False).with_properties(label='Numele sitului'),
                String_using('sit_type').with_properties(label='Tip'),
                Float_using('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),
        ).using(optional=True).
          with_properties(widget='table', label='Relatiile sitului descris cu alte situri - desemnate la nivel international'),

    fl.List.named('corine_relations').of(
        Ordered_dict_of(

                String_using('code', optional=False).with_properties(label='Cod sit Corine'),
                String_using('type').with_properties(label='Tip'),
                Float_using('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),
        ).using(optional=True).
          with_properties(widget='table', label='Relatiile sitului descris cu biotopuri Corine'),

    ).with_properties(label='5. STATUTUL DE PROTECTIE AL SITULUI SI LEGATURA CU BIOTOPURILE CORINE')

section_6 = Ordered_dict_of(

    Ordered_dict_of(

        fl.List.named('inside_activities').of(
            Ordered_dict_of(

                    String_using('code', optional=False).with_properties(label='Cod'),
                    Enum_using('intensity').valued('A', 'B', 'C').with_properties(label='Intensitate', widget='select'),
                    Float_using('percentage').with_properties(label='% din sit'),
                    Enum_using('influence').valued('+', '0', '-').with_properties(label='Influenta', widget='select'),
                ).named('record'),
            ).using(optional=True).
              with_properties(widget='table', label='Activitati si consecinte in interiorul sitului'),

        fl.List.named('outside_activities').of(
            Ordered_dict_of(

                    String_using('code', optional=False).with_properties(label='Cod'),
                    Enum_using('intensity').valued('A', 'B', 'C').with_properties(label='Intensitate', widget='select'),
                    Enum_using('influence').valued('+', '0', '-').with_properties(label='Influenta', widget='select'),
                ).named('record'),
            ).using(optional=True).
              with_properties(widget='table', label='Activitati si consecinte in jurul sitului'),
        ).named('in_jur').
          with_properties(widget='dict', label="Activitati antropice, consecintele lor generale si suprafata din sit afectata"),

    Ordered_dict_of(

        String_using('manager').with_properties(widget='textarea', label='Organismul responsabil pentru managementul sitului'),
        String_using('managpl').with_properties(widget='textarea', label='Planuri de management al sitului'),
        ).named('management').
          with_properties(widget='dict', label="Managementul sitului"),

    ).with_properties(label='6. ACTIVITATILE ANTROPICE SI EFECTELE LOR IN SIT SI IN JURUL ACESTUIA')

section_7 = Ordered_dict_of(

    fl.List.named('map').of(

        Ordered_dict_of(
                String_using('number').with_properties(label='Numar national harta'),
                String_using('scale').with_properties(label='Scara'),
                String_using('projection').with_properties(label='Proiectie'),
            ).with_properties(widget='dict'),

        ).with_properties(widget='list', label='Harta fizica'),

    String_using('site_limits').with_properties(widget='textarea', label='Specificati daca limitele sitului sunt disponibile in format digital'),

    ).with_properties(label='7. HARTA SITULUI')


SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'),
    section_3.named('section3').with_properties(widget='section'),
    section_4.named('section4').with_properties(widget='section'),
    section_5.named('section5').with_properties(widget='section'),
    section_6.named('section6').with_properties(widget='section'),
    section_7.named('section7').with_properties(widget='section'))
