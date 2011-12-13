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
                            widget='dict'),
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
                    fl.Enum.named('repres').valued('A', 'B', 'C').with_properties(label='Reprezentativitate', widget='select'),
                    fl.String.named('relativ_area').with_properties(label='Suprafata relativa'),
                    fl.String.named('conservation_status').with_properties(label='Stare de conservare'),
                    fl.String.named('global_evaluation').with_properties(label='Evaluare globala'),
                ).named('habitat_type'),
            ).with_properties(widget='table', label='Tipuri de habitat prezente in sit si evaluarea sitului in ceea ce le priveste'),
    ).with_properties(label='3. INFORMATII ECOLOGICE')

SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'),
    section_3.named('section3').with_properties(widget='section'))
