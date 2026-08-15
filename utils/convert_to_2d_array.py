def convert_to_2d_array(data, fields=None):
    if not data:
        return []

    if fields is None:
        fields = list(data[0].keys())

    result = []
    for field in fields:
        row = [person.get(field, "") for person in data]
        result.append(row)

    return result
