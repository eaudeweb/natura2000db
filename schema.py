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

SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'),
    section_3.named('section3').with_properties(widget='section'))
