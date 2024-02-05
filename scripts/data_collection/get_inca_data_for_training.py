import json
from datetime import datetime
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.inca_data_extraction import get_geosphere_data_point
from src.utils import load_paths_from_yaml, replace_base_path, calculate_date_of_interest_x_hours_before


def transform_date(input_date):
    """transforms date from "%m/%d/%Y" into '%Y-%m-%dT12:00' format"""
    date_object = datetime.strptime(input_date, "%m/%d/%Y")
    output_date = date_object.strftime('%Y-%m-%dT12:00')
    return str(output_date)


def main():

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # loading and preprocessingg fire event dataset
    event_data = gpd.read_file(paths["fire_events"]["final"])
    event_data["date"] = event_data["date"].apply(transform_date)
    event_data["year"] = event_data["year"].astype("int")
    event_data_subset = event_data[event_data["year"] >= 2012]
    event_data_subset.to_crs("EPSG:4326", inplace=True)

    with open(paths["inca"]["training_data"], 'a') as f:
        params = ["T2M", "RR", "UU", "VV", "RH2M"]

        for i, row in event_data_subset.loc[690:].iterrows():
            start_date = calculate_date_of_interest_x_hours_before(
                row.date, hours=24)
            data = get_geosphere_data_point(
                params, start_date, row.date, row["geometry"].y, row["geometry"].x)
            f.write(f'{i}')
            json.dump(data, f)
            f.write('\n')


if __name__ == "__main__":
    main()
