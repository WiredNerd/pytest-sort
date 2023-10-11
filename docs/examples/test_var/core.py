from test_var.service import get_values


def get_all_values():
    response = get_values()
    values = response["values"]

    while response["next"]:
        response = get_values(response["next"])
        values.extend(response["values"])

    return values
