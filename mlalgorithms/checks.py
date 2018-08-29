def check_types(value, *types, var_name="value"):
    """
    Check value by types compliance.

    :param value: object.
        Value to check.

    :param types: tuple.
        Types list to compare.

    :param var_name: str, optional (default="value").
        Name of the variable for exception message.
    """
    if len(types) == 0:
        raise ValueError("Types list is empty.")

    bad_type = True
    for type_ in types:
        if type(value) is type_:
            bad_type = False

    if bad_type:
        raise ValueError(f"{var_name} parameter must be {types}: "
                         f"got {type(value)}.")


def check_value(value, lower=None, upper=None, strict_less=False,
                strict_greater=False, var_name="value"):
    """
    Check for compliance with the bounds.

    :param value: object.
        Value to check.

    :param lower: object, optional (default=None).
        Lower bound for comparison.

    :param upper: object, optional (default=None).
        Upper bound for comparison.

    :param strict_less: bool, optional (default=False).
        Type of comparison for lower bound.

    :param strict_greater: bool, optional (default=False).
        Type of comparison for upper bound.

    :param var_name: str, optional (default="value").
        Name of the variable for exception message.
    """
    lower_value = lower is not None
    upper_value = upper is not None

    if not lower_value and strict_less:
        raise ValueError("strict_less argument must be False when lower is "
                         "not specified.")
    if not upper_value and strict_greater:
        raise ValueError("strict_greater argument must be False when upper is "
                         "not specified.")

    # Dict where keys have format like
    # (lower_value, upper_value, strict_less, strict_greater)
    possible_options = {
        (True, False, True, False): {"res": lambda x: lower < x,
                                     "str": f"({lower}, inf)"},

        (True, False, False, False): {"res": lambda x: lower <= x,
                                      "str": f"[{lower}, inf)"},

        (False, True, False, True): {"res": lambda x: x < upper,
                                     "str": f"(-inf, {upper})"},

        (False, True, False, False): {"res": lambda x: x <= upper,
                                      "str": f"(-inf, {upper}]"},

        (True, True, True, True): {"res": lambda x: lower < x < upper,
                                   "str": f"({lower}, {upper})"},

        (True, True, False, True): {"res": lambda x: lower <= x < upper,
                                    "str": f"[{lower}, {upper})"},

        (True, True, True, False): {"res": lambda x: lower < x <= upper,
                                    "str": f"({lower}, {upper}]"},

        (True, True, False, False): {"res": lambda x: lower <= x <= upper,
                                     "str": f"[{lower}, {upper}]"}
    }

    result = possible_options[lower_value, upper_value,
                              strict_less, strict_greater]
    if not result["res"](value):
        raise ValueError(f"{var_name} parameter must be in {result['str']}: "
                         f"got {value}.")


def check_equality(value, expected_value, message=None):
    """
    Check two values by equality.

    :param value: object.
        Value to check.

    :param expected_value: object.
        Value to compare.

    :param message: str, optional(default=None).
        Message to output with exception.
    """
    if value != expected_value:
        if message is None:
            raise ValueError(f"Variable has unexpected value: "
                             f"{value} != {expected_value}")
        raise ValueError(f"{message}: {value} != {expected_value}")


def check_inheritance(instance, class_, message=None):
    """
    Check class on the according interface.

    :param instance: object.
        Value to check.

    :param class_: class
        Type of the class to compare.

    :param message: str, optional(default=None).
        Message to output with exception.
    """
    if not isinstance(instance, class_):
        if message is None:
            raise ValueError(f"{type(instance)} is not subclass of {class_}.")
        raise ValueError(f"{message}: "
                         f"{type(instance)} is not subclass of {class_}.")
