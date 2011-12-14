import re
import flatland as fl


def valid_float(element, state):
    if isinstance(element.value, float):
        return True

    else:
        element.add_error("Value must be numeric")
        return False

def valid_char(element, state):
    patt = re.compile(r'^[a-k]$', re.IGNORECASE)
    if patt.match(element.value):
        return True

    else:
        element.add_error("Only one character from A to K is allowed")
        return False

def valid_date(element, state):
    patt = re.compile(r'^\d{6}$')
    if patt.match(element.value):
        return True

    else:
        element.add_error("Invalid date. Please use the YYYYMM format")
        return False

def valid_code(element, state):
    patt = re.compile(r'^\w{9}$')
    if patt.match(element.value):
        return True

    else:
        element.add_error("Invalid code")
        return False

def valid_dict_value(element, state):
    for child in element.values():
        if child.value is None:
            element.add_error("Please choose at least one value")
            return False
    return True


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


section_1 = Ordered_dict_of(

    String_using('type', optional=False).using(validators=[valid_char]).with_properties(label='Tip'),
    String_using('code', optional=False).using(validators=[valid_code]).with_properties(label='Codul sitului'),

    Date_using('release_date', optional=False).with_properties(label='Data completarii'),
    Date_using('last_modified', optional=False).with_properties(label='Data actualizarii'),

    fl.List.named('other_sites').of(
            String_using('other_site').using(validators=[valid_code])
        ).
        with_properties(widget='list', label='Coduri ale siturilor Natura 2000'),

    String('responsible').with_properties(widget='textarea', label='Responsabili'),

    String_using('sit_name', optional=False).with_properties(label='Numele sitului'),

    Ordered_dict_of(
            Date_using('sci_prop_date').with_properties(label='Data propunerii ca sit SCI'),
            Date_using('sci_conf_date').with_properties(label='Data confirmarii ca sit SCI'),
            Date_using('spa_conf_date').with_properties(label='Data confirmarii ca sit SPA'),
            Date_using('sac_conf_date').with_properties(label='Data desemnarii ca sit SAC'),

        ).named('sit_dates').with_properties(label='Datele indicarii si desemnarii/clasificarii sitului', widget='dict'),

    ).with_properties(label='1. IDENTIFICAREA SITULUI')

section_2 = Ordered_dict_of(

    String_using('long', optional=False).with_properties(label='Longitudine'),
    String_using('lat', optional=False).with_properties(label='Latitudine'),
    
    Date_using('area').with_properties(label='Suprafata (ha)'),
    Date_using('length').with_properties(label='Lungimea sitului (km)'),

    Ordered_dict_of(
            Float_using('alt_min').with_properties(label='Minima'),
            Float_using('alt_max').with_properties(label='Maxima'),
            Float_using('alt_med').with_properties(label='Medie'),

        ).named('altitude').with_properties(label='Altitudine (m)', widget='dict'),

    Ordered_dict_of(
            String_using('nuts_code').with_properties(label='Codul NUTS'),
            String_using('reg_name').with_properties(label='Numele regiunii'),
            String_using('percentage').with_properties(label='Pondere (%)'),

        ).named('admin_region').using(validators=[valid_dict_value]).with_properties(label='Regiunea administrativa', widget='dict'),

    Ordered_dict_of(
            Boolean_using('alpine').with_properties(label='Alpina', widget='checkbox'),
            Boolean_using('continental').with_properties(label='Continentala', widget='checkbox'),
            Boolean_using('stepic').with_properties(label='Stepica', widget='checkbox'),
            Boolean_using('pontic').with_properties(label='Pontica', widget='checkbox'),
            Boolean_using('pannonian').with_properties(label='Panonica', widget='checkbox'),

        ).named('bio_region').using(validators=[valid_dict_value]).with_properties(label='Regiunea biogeografica', widget='dict'),

    ).with_properties(label='2. LOCALIZAREA SITULUI')

section_3 = Ordered_dict_of(

    fl.List.named('habitat_types').of(

        Ordered_dict_of(

                String_using('code').with_properties(label='Cod'),
                String_using('percentage').with_properties(label='Pondere'),
                Enum_using('repres').valued('A', 'B', 'C', 'D').with_properties(label='Reprezentativitate', widget='select'),
                Enum_using('relativ_area').valued('A', 'B', 'C').with_properties(label='Suprafata relativa', widget='select'),
                Enum_using('conservation_status').valued('A', 'B', 'C').with_properties(label='Stare de conservare', widget='select'),
                Enum_using('global_evaluation').valued('A', 'B', 'C').with_properties(label='Evaluare globala', widget='select'),
            ).named('habitat_type'),

        ).with_properties(widget='table', label='Tipuri de habitat prezente in sit si evaluarea sitului in ceea ce le priveste'),

    fl.List.named('species_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                Ordered_dict_of(
                    fl.String.named('resident').with_properties(label='Residenta'),
                    Ordered_dict_of(
                        fl.String.named('reproduction').with_properties(label='Reproducere'),
                        fl.String.named('wintering').with_properties(label='Iernat'),
                        fl.String.named('passage').with_properties(label='Pasaj'),
                        ).named('migratory').with_properties(label='Migratoare'),
                    ).named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('specie_type'),
        ).with_properties(widget='table', label='Specii de pasari enumerate in anexa I la Directiva Consiliului 79/409/CEE'),

    fl.List.named('migratory_species_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                Ordered_dict_of(
                    fl.String.named('resident').with_properties(label='Residenta'),
                    Ordered_dict_of(
                        fl.String.named('reproduction').with_properties(label='Reproducere'),
                        fl.String.named('wintering').with_properties(label='Iernat'),
                        fl.String.named('passage').with_properties(label='Pasaj'),
                        ).named('migratory').with_properties(label='Migratoare'),
                    ).named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('specie_type'),
        ).with_properties(widget='table', label='Specii de pasari cu migratie regulata nementionate in anexa I la Directiva Consiliului 79/409/CEE'),

    fl.List.named('mammals_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                Ordered_dict_of(
                    fl.String.named('resident').with_properties(label='Residenta'),
                    Ordered_dict_of(
                        fl.String.named('reproduction').with_properties(label='Reproducere'),
                        fl.String.named('wintering').with_properties(label='Iernat'),
                        fl.String.named('passage').with_properties(label='Pasaj'),
                        ).named('migratory').with_properties(label='Migratoare'),
                    ).named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('mammal_types'),
        ).with_properties(widget='table', label='Specii de mamifere enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('reptiles_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                Ordered_dict_of(
                    fl.String.named('resident').with_properties(label='Residenta'),
                    Ordered_dict_of(
                        fl.String.named('reproduction').with_properties(label='Reproducere'),
                        fl.String.named('wintering').with_properties(label='Iernat'),
                        fl.String.named('passage').with_properties(label='Pasaj'),
                        ).named('migratory').with_properties(label='Migratoare'),
                    ).named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('reptile_types'),
        ).with_properties(widget='table', label='Specii de amfibieni si reptile enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('fishes_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                Ordered_dict_of(
                    fl.String.named('resident').with_properties(label='Residenta'),
                    Ordered_dict_of(
                        fl.String.named('reproduction').with_properties(label='Reproducere'),
                        fl.String.named('wintering').with_properties(label='Iernat'),
                        fl.String.named('passage').with_properties(label='Pasaj'),
                        ).named('migratory').with_properties(label='Migratoare'),
                    ).named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('fish_types'),
        ).with_properties(widget='table', label='Specii de pesti enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('invertebrates_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                Ordered_dict_of(
                    fl.String.named('resident').with_properties(label='Residenta'),
                    Ordered_dict_of(
                        fl.String.named('reproduction').with_properties(label='Reproducere'),
                        fl.String.named('wintering').with_properties(label='Iernat'),
                        fl.String.named('passage').with_properties(label='Pasaj'),
                        ).named('migratory').with_properties(label='Migratoare'),
                    ).named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('invertebrate_types'),
        ).with_properties(widget='table', label='Specii de nevertebrate enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('plants_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('name').with_properties(label='Nume'),
                fl.String.named('population').with_properties(label='Populatie'),
                Ordered_dict_of(
                    fl.Enum.named('population').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    fl.Enum.named('conservation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Conservare', widget='select'),
                    fl.Enum.named('isolation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Izolare', widget='select'),
                    fl.Enum.named('global_eval').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
                    ).named('sit_evaluation').with_properties(label='Evaluarea sitului'),
            ).named('plant_types'),
        ).with_properties(widget='table', label='Specii de plante enumerate in anexa II la Directiva Consiliului 92/43/CEE'),

    fl.List.named('other_species').of(
        Ordered_dict_of(
                fl.Enum.named('category').
                        valued('pasari', 'mamifere', 'amfibieni', 'reptile', 'pesti', 'nevertebrate', 'plante').
                        using(optional=True).
                        with_properties(label='Categorie', widget='select'),
                fl.String.named('scientific_name').with_properties(label='Denumire stiintifica'),
                Ordered_dict_of(
                    fl.String.named('population_text').with_properties(label='Populatie'),
                    fl.Enum.named('population_trend').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Populatie', widget='select'),
                    ).named('population').with_properties(label='Populatie'),
            ).named('other_specie'),
        ).with_properties(widget='table', label='Alte specii importante de flora si fauna'),

    ).with_properties(label='3. INFORMATII ECOLOGICE')

section_4 = Ordered_dict_of(

    Ordered_dict_of(
            fl.Float.named('areas').with_properties(label='Arii marine, privaluri'),
            fl.Float.named('rivers').with_properties(label='Rauri (fluvii) afectate de maree, estuare, terase mlastinoase sau nisipoase, lagune(inclusiv bazinele de colectare a sarii)'),
            fl.Float.named('salt surfaces').with_properties(label='Suprafete saraturate (mlastini, pajisti, stepe)'),
            fl.Float.named('beach').with_properties(label='Dune de coasta, plaje cu nisip, machair'),
            fl.Float.named('litoral').with_properties(label='Litoral cu prundis, faleze, insulite'),
            fl.Float.named('freshwater').with_properties(label='Ape dulci continentale (statatoare, curgatoare)'),
            fl.Float.named('swamps').with_properties(label='Mlastini (vegetatie de centura), smarcuri, turbarii'),
            fl.Float.named('maquis').with_properties(label='Lande, tufarisuri, maquis si garigue, phrygana'),
            fl.Float.named('steppes').with_properties(label='Pajisti uscate, stepe'),
            fl.Float.named('prairies').with_properties(label='Pajisti seminaturale umede, preerii mezofile'),
            fl.Float.named('alpine').with_properties(label='Pajisti alpine si subalpine'),
            fl.Float.named('crops').with_properties(label='Culturi cerealiere extensive (inclusiv culturile de rotatie cu dezmiristire)'),
            fl.Float.named('rice').with_properties(label='Orezarii'),
            fl.Float.named('meadows').with_properties(label='Pajisti ameliorate'),
            fl.Float.named('other_arable').with_properties(label='Alte terenuri arabile'),
            fl.Float.named('deciduous_forests').with_properties(label='Paduri caducifoliate'),
            fl.Float.named('coniferous_forests').with_properties(label='Paduri de conifere'),
            fl.Float.named('unconiferous_forests').with_properties(label='Paduri semperviriscente de nerasinoase'),
            fl.Float.named('mixt_forests').with_properties(label='Paduri mixte'),
            fl.Float.named('monoculture_forests').with_properties(label='Paduri de monocultura (plopi sau arbori exotici)'),
            fl.Float.named('plantations').with_properties(label='Plantatii de arbori sau plante lemnoase (inclusiv livezi, cranguri, vii, dehesas)'),
            fl.Float.named('rocks').with_properties(label='Stancarii interioare, grohotisuri, dune interioare, zone cu zapezi si gheturi vesnice'),
            fl.Float.named('other_land').with_properties(label='Alte terenuri (inclusiv zone urbane, rurale, cai de comunicatie, rampe de depozitare, mine, zone industriale)'),
        ).named('habitat_classes').with_properties(label='Clase de habitat', widget='habitat_breakdown'),

    fl.String.named('quality').with_properties(widget='textarea', label='Calitate si importanta'),
    fl.String.named('vulnerability').with_properties(widget='textarea', label='Vulnerabilitate'),
    fl.String.named('designation').with_properties(widget='textarea', label='Desemnarea sitului (vezi observatiile privind datele cantitative de mai jos)'),
    fl.String.named('property_type').with_properties(widget='textarea', label='Tip de proprietate'),
    fl.String.named('documentation').with_properties(widget='textarea', label='Documentatie'),

    fl.List.named('history').of(
        Ordered_dict_of(
                fl.String.named('date').with_properties(label='Data'),
                fl.String.named('modified_field').with_properties(label='Campul modificat'),
                fl.String.named('description').with_properties(label='Descriere'),
            ).named('record'),
        ).with_properties(widget='table', label='Istoric (se va completa de catre Comisie)'),
    ).with_properties(label='4. DESCRIEREA SITULUI')

section_5 = Ordered_dict_of(

    fl.List.named('clasification').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.Float.named('percentage').with_properties(label='Pondere %'),
            ).named('record'),
        ).with_properties(widget='table', label='Clasificare la nivel national si regional'),

    fl.List.named('national_relations').of(
        Ordered_dict_of(
                fl.String.named('type').with_properties(label='Tip'),
                fl.String.named('name').with_properties(label='Numele sitului'),
                fl.String.named('sit_type').with_properties(label='Tip'),
                fl.Float.named('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),
        ).with_properties(widget='table', label='Relatiile sitului descris cu alte situri - desemnate la nivel national sau regional'),

    fl.List.named('international_relations').of(
        Ordered_dict_of(
                fl.Enum.named('type').valued('Conventia Ramsar', 'Rezervatia biogenetica', 'Sit Eurodiploma', 
                                            'Rezervatia biosferei', 'Conventia Barcelona', 'Sit patrimoniu mondial', 
                                            'Altele').using(optional=True).with_properties(label='Tip', widget='select'),
                fl.String.named('name').with_properties(label='Numele sitului'),
                fl.String.named('sit_type').with_properties(label='Tip'),
                fl.Float.named('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),
        ).with_properties(widget='table', label='Relatiile sitului descris cu alte situri - desemnate la nivel international'),

    fl.List.named('corine_relations').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod sit Corine'),
                fl.String.named('type').with_properties(label='Tip'),
                fl.Float.named('overlap').with_properties(label='Suprapunere %'),
            ).named('record'),
        ).with_properties(widget='table', label='Relatiile sitului descris cu biotopuri Corine'),

    ).with_properties(label='5. STATUTUL DE PROTECTIE AL SITULUI SI LEGATURA CU BIOTOPURILE CORINE')

section_6 = Ordered_dict_of(

    fl.List.named('inside_activities').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.Enum.named('intensity').valued('A', 'B', 'C').using(optional=True).with_properties(label='Intensitate', widget='select'),
                fl.Float.named('percentage').with_properties(label='% din sit'),
                fl.Enum.named('influence').valued('+', '0', '-').using(optional=True).with_properties(label='Influenta', widget='select'),
            ).named('record'),
        ).with_properties(widget='table', label='Activitati si consecinte in interiorul sitului'),

    fl.List.named('outside_activities').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.Enum.named('intensity').valued('A', 'B', 'C').using(optional=True).with_properties(label='Intensitate', widget='select'),
                fl.Enum.named('influence').valued('+', '0', '-').using(optional=True).with_properties(label='Influenta', widget='select'),
            ).named('record'),
        ).with_properties(widget='table', label='Activitati si consecinte in jurul sitului'),

    fl.String.named('responsible').with_properties(widget='textarea', label='Organismul responsabil pentru managementul sitului'),
    fl.String.named('plans').with_properties(widget='textarea', label='Planuri de management al sitului'),

    ).with_properties(label='6. ACTIVITATILE ANTROPICE SI EFECTELE LOR IN SIT SI IN JURUL ACESTUIA')

section_7 = Ordered_dict_of(

    Ordered_dict_of(
            fl.String.named('number').with_properties(label='Numar national harta'),
            fl.String.named('scale').with_properties(label='Scala'),
            fl.String.named('projection').with_properties(label='Proiectie'),
        ).named('map').with_properties(widget='dict', label='Harta fizica'),

    fl.String.named('site_limits').with_properties(widget='textarea', label='Specificati daca limitele sitului sunt disponibile in format digital'),

    ).with_properties(label='7. HARTA SITULUI')


SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'),
    section_3.named('section3').with_properties(widget='section'),
    section_4.named('section4').with_properties(widget='section'),
    section_5.named('section5').with_properties(widget='section'),
    section_6.named('section6').with_properties(widget='section'),
    section_7.named('section7').with_properties(widget='section'))
