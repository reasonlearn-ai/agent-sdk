def calculate_average(numbers):
    if not numbers:
        return 0
    if not isinstance(numbers, (list, tuple, set, frozenset)):
        return 0
    total = 0
    count = 0
    for num in numbers:
        if not isinstance(num, (int, float)):
            continue
        total += num
        count += 1
    if count == 0:
        return 0
    return total / count


def get_user_name(user):
    if not isinstance(user, dict):
        return ""
    name = user.get("name")
    if name is None:
        return ""
    return str(name).upper()
