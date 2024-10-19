import logging
import pandas as pd
from get_last_date import get_last_date

mapping = {
    '1. open':'stocks_open',
    '2. high':'stocks_high',
    '3. low':'stocks_low',
    '4. close':'stocks_close',
    '5. adjusted close':'stocks_adjusted_close',
    '6. volume':'stocks_volume',
    '7. dividend amount':'stocks_dividend_amount',
    '8. split coefficient':'stocks_split_coefficient',
}

column_order = [
    'stocks_name',
    'stocks_date',
    'stocks_timezone',
    'stocks_open',
    'stocks_high',
    'stocks_low',
    'stocks_close',
    'stocks_adjusted_close',
    'stocks_volume',
    'stocks_dividend_amount',
    'stocks_split_coefficient'
]

logging.basicConfig(level=logging.INFO)

def clean_data(**kwargs):

    previous_data = kwargs['ti'].xcom_pull(task_ids='clean_data', dag_id=kwargs['dag'].dag_id)
    last_date = kwargs['ti'].xcom_pull(task_ids='last_date', dag_id=kwargs['dag'].dag_id)

    if previous_data:
        return previous_data
    
    json_objects = kwargs['ti'].xcom_pull(task_ids='get_data', key='response_json')
    list_of_dataframes = []
    for json_object in json_objects:
        print(json_object)
        stock_name = json_object['Meta Data']['2. Symbol']
        time_series_data = json_object['Time Series (Daily)']

        values = time_series_data.values()
        print(values)

        time_zones_dataframes = []
        for time_zone, data in time_series_data.items():
            print(data)
            df = pd.DataFrame(data, index=[0])
            df['stocks_timezone'] = time_zone
            df['stocks_timezone'] = pd.to_datetime(df['stocks_timezone'])

            time_zones_dataframes.append(df)
        
        combined_df = pd.concat(time_zones_dataframes, ignore_index=True)
        combined_df['stocks_name'] = stock_name
        combined_df['stocks_date'] = combined_df['stocks_timezone'].dt.tz_localize(None)

        list_of_dataframes.append(combined_df.copy(deep=True))

    df = pd.concat(list_of_dataframes, ignore_index=True)
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    df.rename(columns=mapping, inplace=True)
    df = df[column_order]

    for value in mapping.values():
        try:
            df[value] = pd.to_numeric(df[value], errors='raise')
        except:
            raise KeyError(f'Mapping to numeric values has failed. Column {value} does not exist in the dataframe')

    last_date = get_last_date()
    start_date = last_date if last_date else kwargs['dag'].start_date 

    kwargs['ti'].xcom_push(key='df', value=df)