import flatland as fl

def Ordered_dict_of(*fields):
    order = [field.name for field in fields]
    return fl.Dict.of(*fields).with_properties(order=order)

section_1 = Ordered_dict_of(

    fl.String.named('type').with_properties(label='Tip'),
    fl.String.named('code').with_properties(label='Codul sitului'),
    fl.String.named('release_date').with_properties(label='Data completarii'),
    fl.String.named('last_modified').with_properties(label='Data actualizarii'),
    fl.List.named('other_sites').of(fl.String) \
                                .with_properties(widget='list', 
                                                label='Coduri ale siturilor Natura 2000'),
    fl.String.named('responsible').with_properties(widget='textarea', 
                                                    label='Responsabili'),
    fl.String.named('sit_name').with_properties(label='Numele sitului'),

    Ordered_dict_of(
            fl.String.named('sci_prop_date').with_properties(label='Data propunerii ca sit SCI'),
            fl.String.named('sci_conf_date').with_properties(label='Data confirmarii ca sit SCI'),
            fl.String.named('spa_conf_date').with_properties(label='Data confirmarii ca sit SPA'),
            fl.String.named('sac_conf_date').with_properties(label='Data desemnarii ca sit SAC'),
        ).with_properties(label='Datele indicarii si desemnarii/clasificarii sitului',
                            widget='dict').named('sit_dates'),
    ).with_properties(label='1. IDENTIFICAREA SITULUI')

section_2 = Ordered_dict_of(

    fl.String.named('long').with_properties(label='Longitudine'),
    fl.String.named('lat').with_properties(label='Latitudine'),
    fl.Integer.named('area').with_properties(label='Suprafata (ha)', type='float'),
    fl.Integer.named('length').with_properties(label='Lungimea sitului (km)', type='float'),

    Ordered_dict_of(
            fl.Integer.named('alt_min').with_properties(label='Minima', type='float'),
            fl.Integer.named('alt_max').with_properties(label='Maxima', type='float'),
            fl.Integer.named('alt_med').with_properties(label='Medie', type='float'),
        ).named('altitude').with_properties(label='Altitudine (m)',
                            widget='dict'),
    Ordered_dict_of(
            fl.String.named('nuts_code').with_properties(label='Codul NUTS'),
            fl.String.named('reg_name').with_properties(label='Numele regiunii'),
            fl.String.named('percentage').with_properties(label='Pondere (%)'),
        ).named('admin_region').with_properties(label='Regiunea administrativa',
                            widget='dict'),
    Ordered_dict_of(
            fl.Boolean.named('alpine').with_properties(label='Alpina', widget='checkbox'),
            fl.Boolean.named('continental').with_properties(label='Continentala', widget='checkbox'),
            fl.Boolean.named('stepic').with_properties(label='Stepica', widget='checkbox'),
            fl.Boolean.named('pontic').with_properties(label='Pontica', widget='checkbox'),
            fl.Boolean.named('pannonian').with_properties(label='Panonica', widget='checkbox'),
        ).named('bio_region').with_properties(label='Regiunea biogeografica',
                            widget='dict'),
    ).with_properties(label='2. LOCALIZAREA SITULUI')

section_3 = Ordered_dict_of(

    fl.List.named('habitat_types').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.String.named('percentage').with_properties(label='Pondere'),
                fl.Enum.named('repres').valued('A', 'B', 'C', 'D').using(optional=True).with_properties(label='Reprezentativitate', widget='select'),
                fl.Enum.named('relativ_area').valued('A', 'B', 'C').using(optional=True).with_properties(label='Suprafata relativa', widget='select'),
                fl.Enum.named('conservation_status').valued('A', 'B', 'C').using(optional=True).with_properties(label='Stare de conservare', widget='select'),
                fl.Enum.named('global_evaluation').valued('A', 'B', 'C').using(optional=True).with_properties(label='Evaluare globala', widget='select'),
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
            fl.Integer.named('areas').with_properties(label='Arii marine, privaluri', type='float'),
            fl.Integer.named('rivers').with_properties(label='Rauri (fluvii) afectate de maree, estuare, terase mlastinoase sau nisipoase, lagune(inclusiv bazinele de colectare a sarii)', type='float'),
            fl.Integer.named('salt surfaces').with_properties(label='Suprafete saraturate (mlastini, pajisti, stepe)', type='float'),
            fl.Integer.named('beach').with_properties(label='Dune de coasta, plaje cu nisip, machair', type='float'),
            fl.Integer.named('litoral').with_properties(label='Litoral cu prundis, faleze, insulite', type='float'),
            fl.Integer.named('freshwater').with_properties(label='Ape dulci continentale (statatoare, curgatoare)', type='float'),
            fl.Integer.named('swamps').with_properties(label='Mlastini (vegetatie de centura), smarcuri, turbarii', type='float'),
            fl.Integer.named('maquis').with_properties(label='Lande, tufarisuri, maquis si garigue, phrygana', type='float'),
            fl.Integer.named('steppes').with_properties(label='Pajisti uscate, stepe', type='float'),
            fl.Integer.named('prairies').with_properties(label='Pajisti seminaturale umede, preerii mezofile', type='float'),
            fl.Integer.named('alpine').with_properties(label='Pajisti alpine si subalpine', type='float'),
            fl.Integer.named('crops').with_properties(label='Culturi cerealiere extensive (inclusiv culturile de rotatie cu dezmiristire)', type='float'),
            fl.Integer.named('rice').with_properties(label='Orezarii', type='float'),
            fl.Integer.named('meadows').with_properties(label='Pajisti ameliorate', type='float'),
            fl.Integer.named('other_arable').with_properties(label='Alte terenuri arabile', type='float'),
            fl.Integer.named('deciduous_forests').with_properties(label='Paduri caducifoliate', type='float'),
            fl.Integer.named('coniferous_forests').with_properties(label='Paduri de conifere', type='float'),
            fl.Integer.named('unconiferous_forests').with_properties(label='Paduri semperviriscente de nerasinoase', type='float'),
            fl.Integer.named('mixt_forests').with_properties(label='Paduri mixte', type='float'),
            fl.Integer.named('monoculture_forests').with_properties(label='Paduri de monocultura (plopi sau arbori exotici)', type='float'),
            fl.Integer.named('plantations').with_properties(label='Plantatii de arbori sau plante lemnoase (inclusiv livezi, cranguri, vii, dehesas)', type='float'),
            fl.Integer.named('rocks').with_properties(label='Stancarii interioare, grohotisuri, dune interioare, zone cu zapezi si gheturi vesnice', type='float'),
            fl.Integer.named('other_land').with_properties(label='Alte terenuri (inclusiv zone urbane, rurale, cai de comunicatie, rampe de depozitare, mine, zone industriale)', type='float'),
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
                fl.Integer.named('percentage').with_properties(label='Pondere %', type='float'),
            ).named('record'),
        ).with_properties(widget='table', label='Clasificare la nivel national si regional'),

    fl.List.named('national_relations').of(
        Ordered_dict_of(
                fl.String.named('type').with_properties(label='Tip'),
                fl.String.named('name').with_properties(label='Numele sitului'),
                fl.String.named('sit_type').with_properties(label='Tip'),
                fl.Integer.named('overlap').with_properties(label='Suprapunere %', type='float'),
            ).named('record'),
        ).with_properties(widget='table', label='Relatiile sitului descris cu alte situri - desemnate la nivel national sau regional'),

    fl.List.named('international_relations').of(
        Ordered_dict_of(
                fl.Enum.named('type').valued('Conventia Ramsar', 'Rezervatia biogenetica', 'Sit Eurodiploma', 
                                            'Rezervatia biosferei', 'Conventia Barcelona', 'Sit patrimoniu mondial', 
                                            'Altele').using(optional=True).with_properties(label='Tip', widget='select'),
                fl.String.named('name').with_properties(label='Numele sitului'),
                fl.String.named('sit_type').with_properties(label='Tip'),
                fl.Integer.named('overlap').with_properties(label='Suprapunere %', type='float'),
            ).named('record'),
        ).with_properties(widget='table', label='Relatiile sitului descris cu alte situri - desemnate la nivel international'),

    fl.List.named('corine_relations').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod sit Corine'),
                fl.String.named('type').with_properties(label='Tip'),
                fl.Integer.named('overlap').with_properties(label='Suprapunere %', type='float'),
            ).named('record'),
        ).with_properties(widget='table', label='Relatiile sitului descris cu biotopuri Corine'),

    ).with_properties(label='5. STATUTUL DE PROTECTIE AL SITULUI SI LEGATURA CU BIOTOPURILE CORINE')

section_6 = Ordered_dict_of(

    fl.List.named('inside_activities').of(
        Ordered_dict_of(
                fl.String.named('code').with_properties(label='Cod'),
                fl.Enum.named('intensity').valued('A', 'B', 'C').using(optional=True).with_properties(label='Intensitate', widget='select'),
                fl.Integer.named('percentage').with_properties(label='% din sit', type='float'),
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
