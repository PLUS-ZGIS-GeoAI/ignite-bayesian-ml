import json
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.data_collection.inca_data_extraction import get_geosphere_data_point
from src.data_preprocessing.inca_data_preprocessing import calculate_date_of_interest_x_hours_before
from src.data_preprocessing.fire_event_preprocessing import transform_date


def main():

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # loading and preprocessingg fire event dataset
    event_data = gpd.read_file(paths["fire_events"]["final"])
    event_data["date"] = event_data["date"].apply(transform_date)
    event_data["year"] = event_data["year"].astype("int")
    # At Geosphere Data API only data from 2012 and later is available
    event_data_subset = event_data[event_data["year"] >= 2012]
    event_data_subset.to_crs("EPSG:4326", inplace=True)

    with open(paths["inca"]["training_data"], 'a') as f:
        params = ["T2M", "RR", "UU", "VV", "RH2M"]

        # TODO dataframe is sliced at certain location because only a number of requests can be made to Geosphere Data API
        for i, row in event_data_subset.loc[713:].iterrows():
            start_date = calculate_date_of_interest_x_hours_before(
                row.date, hours=24)
            data = get_geosphere_data_point(
                params, start_date, row.date, row["geometry"].y, row["geometry"].x)
            f.write(f'{i}')
            json.dump(data, f)
            f.write('\n')


if __name__ == "__main__":
    main()
