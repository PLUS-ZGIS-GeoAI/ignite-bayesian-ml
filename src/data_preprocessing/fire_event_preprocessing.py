from datetime import datetime


def transform_date(input_date: str):
    """transforms date from '%m/%d/%Y' into '%Y-%m-%dT12:00' format

    Args:
        input_date (str): date of fire (or non-fire) event in format '%m/%d/%Y'

    Returns:
        str: date in format '%Y-%m-%dT12:00'
    """

    date_object = datetime.strptime(input_date, "%m/%d/%Y")
    output_date = date_object.strftime('%Y-%m-%dT12:00')
    return str(output_date)
