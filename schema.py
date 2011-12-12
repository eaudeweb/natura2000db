import flatland as fl


Enum_abc = fl.Enum.valued('A', 'B', 'C').with_properties(widget='radio')

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
    fl.String.named('sci_prop_date').with_properties(label='Data propunerii ca sit SCI'),
    fl.String.named('sci_conf_date').with_properties(label='Data confirmarii ca sit SCI'),
    fl.String.named('spa_conf_date').with_properties(label='Data confirmarii ca sit SPA'),
    fl.String.named('sac_conf_date').with_properties(label='Data desemnarii ca sit SAC')
    ).with_properties(label='1. IDENTIFICAREA SITULUI')

section_2 = Ordered_dict_of(
    fl.String.named('long').with_properties(label='Longitudine')).with_properties(label='2. LOCALIZAREA SITULUI')

SpaDoc = Ordered_dict_of(
    section_1.named('section1').with_properties(widget='section'),
    section_2.named('section2').with_properties(widget='section'))
