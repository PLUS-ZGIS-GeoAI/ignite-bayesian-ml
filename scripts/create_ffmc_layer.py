from datetime import datetime, timedelta
import pandas as pd
from datetime import timedelta
from src.inca_data_extraction import get_inca_data, extract_inca_data, calculate_wind_speed
from src.fwi_system_calculator import FWISystemCalculator


# TODO retrieving inca values does not work yet
# TODO delete calculate_ffmc_from_inca_data, when script is running


def calculate_ffmc(row):
    """calculate Fine Fuel Moisture Code; function to be applied to dataframe"""
    calculator = FWISystemCalculator(
        row['T2M'], row['RH2M'], row['wind_speed'], row['RR'])
    # TODO 85 is ffmc starting value - should be given as input to function
    ffmc = calculator.ffmc_calc(85)
    return pd.Series({'FFMC': ffmc})


def calculate_24_hours_sooner(date_str):
    """produce a date in format YYYY-MM-DDTHH:MM but 24 hours sooner"""
    datetime_of_interest = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    delta_24_hours = timedelta(hours=24)
    result_datetime = datetime_of_interest - delta_24_hours
    result_formatted = result_datetime.strftime('%Y-%m-%dT%H:%M')
    return result_formatted


if __name__ == "__main__":

    date_of_interest = '2021-08-02T12:00'
    date_of_interest_24h_sooner = calculate_24_hours_sooner(date_of_interest)
    output_format = "geosjon"
    bounding_box = [47.45, 14.05, 47.50, 14.10]

    # request inca data from Geosphere Data API
    t2m_data = get_inca_data(parameter="T2M", start_date=date_of_interest,
                             end_date=date_of_interest, bbox=bounding_box, output_format=output_format)
    rr_data = get_inca_data(parameter="RR", start_date=date_of_interest_24h_sooner,
                            end_date=date_of_interest, bbox=bounding_box, output_format=output_format)
    rhum_data = get_inca_data(parameter="RH2M", start_date=date_of_interest,
                              end_date=date_of_interest, bbox=bounding_box, output_format=output_format)
    uu_data = get_inca_data(parameter="UU", start_date=date_of_interest,
                            end_date=date_of_interest, bbox=bounding_box, output_format=output_format)
    vv_data = get_inca_data(parameter="VV", start_date=date_of_interest,
                            end_date=date_of_interest, bbox=bounding_box, output_format=output_format)

    t2m_data_extracted = extract_inca_data(t2m_data, "T2M").loc[:, ["T2M"]]
    rr_data_extracted = extract_inca_data(rr_data, "RR").loc[:, ["RR"]]
    rhum_data_extracted = extract_inca_data(rhum_data, "RH2M").loc[:, ["RH2M"]]
    uu_data_extracted = extract_inca_data(uu_data, "UU").loc[:, ["UU"]]
    vv_data_extracted = extract_inca_data(vv_data, "VV")

    dfs_to_merge = [t2m_data_extracted, rr_data_extracted,
                    rhum_data_extracted, uu_data_extracted, vv_data_extracted]
    df = pd.concat(dfs_to_merge, axis=1)
    df["wind_speed"] = df.apply(
        lambda x: calculate_wind_speed(x.UU, x.VV), axis=1)

    # TODO variable names (result_df, df_result) here are weird; change
    # Assume df is your DataFrame with columns 'temp', 'rhum', 'wind', 'prcp'
    df_result = df.apply(calculate_ffmc, axis=1)

    # Concatenate the original DataFrame with the result DataFrame
    result_df = pd.concat([df, df_result], axis=1)

    print(result_df)
