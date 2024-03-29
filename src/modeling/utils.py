import pandas as pd
import cloudpickle

def temporal_train_test_split(train_data: pd.DataFrame, date_col: str, train_size: float) -> tuple:
    """function splits dataframe into train and test dataframe. Split criteria is the date. Newer samples are contained in the testset. Older samples in the training set.
    Args:
        train_data (pd.DataFrame): Training data set that shall be splitted into training and test set
        date_col (str): date column, which will be used to split data by time
        train_size (float): size (%) of training dataset
    Returns:
        tuple: tuple contains two dataframes -> training and test set
    """
    train_data[date_col] = pd.to_datetime(train_data.date)
    train_data = train_data.sort_values(by=date_col)
    split_index = int(train_size * len(train_data))
    train_df = train_data.iloc[:split_index]
    test_df = train_data.iloc[split_index:]
    return train_df, test_df

def save_model(path_to_model: str, model, idata) -> None:
    dict_to_save = {'model': model,'idata': idata}
    with open(path_to_model , 'wb') as buff:
        cloudpickle.dump(dict_to_save, buff)
