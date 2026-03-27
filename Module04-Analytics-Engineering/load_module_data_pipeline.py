import dlt
import pandas as pd
from tqdm.auto import tqdm #to see progress of uploading
import os

#Fixing data types problem
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
    "ehail_fee": "float64",     
    "trip_type": "Int64"
}
parse_dates_yellow= [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"]
parse_dates_green = [
    "lpep_pickup_datetime",   
    "lpep_dropoff_datetime"
]

pipeline = dlt.pipeline(
    pipeline_name='nyc_taxi_pipeline',
    destination='bigquery',
    staging='filesystem',
    dataset_name='nytaxi',
    progress='tqdm'
)

if not os.path.exists("Uploaded Data.txt"):

    with open("Uploaded Data.txt", "w") as f:
    
        f.write("This file is used to keep track of the processed data files. It will be updated with the names of the files that have been successfully processed and loaded into the database.\n")

#function to download files from the NYC Taxi dataset for a given taxi type (yellow or green) and a specified year and month range.
#The function constructs the URLs for the files based on the provided parameters, makes HTTP GET requests to download the files, and yields the content as pandas DataFrames if the requests are successful.
def download_files(taxi_type, year, month):

    with open("Uploaded Data.txt", "r") as f:
        
        if f"{taxi_type}_tripdata_{year}-{month:02d}" in f.read():

            print(f"{taxi_type} - {year}-{month:02d} has already been uploaded. Skipping...") 

            return

    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/"
    url = f"{prefix}{taxi_type}/{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"

    print(f"Downloading: {taxi_type} - {year}-{month:02d}")
            
    if taxi_type == "yellow":
        df_iter = pd.read_csv(url, compression='gzip', low_memory=False, dtype=dtype, parse_dates=parse_dates_yellow, chunksize=100000)
    elif taxi_type == "green":
        df_iter = pd.read_csv(url, compression='gzip', low_memory=False, dtype=dtype, parse_dates=parse_dates_green, chunksize=100000)
    else:
        raise ValueError("Invalid taxi type. Please specify 'yellow' or 'green'.")

    def chunk_generator():

        for df in tqdm(df_iter, desc=f"Processing {taxi_type} {year}-{month:02d}", unit=" chunks"):

            yield df

    try:

        load_info = pipeline.run(chunk_generator(), table_name=f"{taxi_type}_taxi_trips", write_disposition="append")

        print(load_info)

        with open("Uploaded Data.txt", "a") as f:
                
            f.write(f"{taxi_type}_tripdata_{year}-{month:02d}" + "\n")
    
    except Exception as e:

        print(f"Error Uploading {taxi_type} - {year}-{month:02d}: {e}")


if __name__ == "__main__":

    for year in range(2019, 2021):

        for month in range(1, 13):

            download_files("yellow", year, month)
            download_files("green", year, month)