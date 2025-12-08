
def parse_float_input(value: str) -> float:
    """
    Parses a string input that might contain comma or dot as decimal separator.

    Args:
        value (str): The string to parse.

    Returns:
        float: The parsed float value.

    Raises:
        ValueError: If the value cannot be converted to float.
    """
    if not value:
        raise ValueError("Empty value")
    clean_value = value.replace(',', '.')
    return float(clean_value)

def format_float_output(value: float, precision: int = None) -> str:
    """
    Formats a float to a string using comma as decimal separator.

    Args:
        value (float): The value to format.
        precision (int, optional): Number of decimal places.

    Returns:
        str: The formatted string.
    """
    if value is None:
        return ""

    if precision is not None:
        s = f"{value:.{precision}f}"
    else:
        s = str(value)

    return s.replace('.', ',')
