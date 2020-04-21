

def get_all_fields_from_feat(feature):
    all_attr = feature.attributevalue_set.all()

    out_string = ''
    for item in all_attr:
        out_string += item.attribute.name +': '
        out_string += item.value +'<br/>'

    return out_string
