
def str_to_bool(val):
    """
    Convert a string representation of truth to a boolean value.

    Args:
        val (str): The string to convert. Can be "true", "false", "1", "0", "yes", "no".

    Returns:
        bool: The corresponding boolean value. If the string is not recognized, it returns False.
    """
    return val.lower() in ("true", "1", "yes") if isinstance(val, str) else bool(val)
