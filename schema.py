import flatland as fl


Enum_abc = fl.Enum.valued('A', 'B', 'C').with_properties(widget='radio')

def Ordered_dict_of(*fields):
    order = [field.name for field in fields]
    return fl.Dict.of(*fields).with_properties(order=order)

section_1 = Ordered_dict_of(
    fl.String.named('type').with_properties(label='Tip'),
    fl.String.named('code').with_properties(label='Codul sitului'),
    fl.String.named('release_date').with_properties(label='Data completarii'),
    fl.String.named('last_modified').with_properties(label='Data actualizarii'))
    
Species = Ordered_dict_of(
    fl.Integer.named('code'),
    fl.String.named('name'),
    Ordered_dict_of(
            fl.String.named('resident'),
            Ordered_dict_of(
                    fl.String.named('repro'),
                    fl.String.named('winter'),
                    fl.String.named('transit'),
                ).named('migratory').with_properties(
                    widget='dict',
                    order=['repro', 'winter', 'transit'],
                ),
        ).named('population').with_properties(widget='dict'),
    Ordered_dict_of(
            Enum_abc.named('population'),
            Enum_abc.named('conservation'),
            Enum_abc.named('isolation'),
            Enum_abc.named('global'),
        ).named('site').with_properties(widget='dict'),
)
