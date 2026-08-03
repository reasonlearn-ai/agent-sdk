def calculate_average(numbers):
    """Return the mean of `numbers`, or 0.0 if there are none.

    Accepts any iterable, including one-shot iterators such as generators.
    """
    total = 0
    count = 0
    for num in numbers or ():
        total += num
        count += 1
    if count == 0:
        return 0.0
    return total / count


def get_user_name(user):
    """Return the user's name upper-cased, or "" if it is missing or empty."""
    if not isinstance(user, dict):
        return ""
    name = user.get("name")
    if not name:
        return ""
    return str(name).upper()
