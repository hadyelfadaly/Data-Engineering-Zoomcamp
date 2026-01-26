#libraries used for linking with postgresql
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm #to see progress of inserting

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
    "congestion_surcharge": "float64"
}
parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


def run(): 

    year = 2021
    month = 1
    url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_{year}-{month:02d}.csv.gz'
    chunk_size = 100000
    pguser = 'root'
    pgpassword = 'root'
    pghost = 'localhost'
    pgport = 5432
    pgdatabase = 'ny_taxi'
    engine = create_engine(f'postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}')
    first = True
    table_name = 'yellow_taxi_data'

    #to divide the data into chunks of equal size so we can inser chunk by chunk
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunk_size
    )

    for df_chunk in tqdm(df_iter):

        if first:

            df_chunk.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace') #creating table

            first = False

            print("Table created successfully")

        df_chunk.to_sql(name=table_name, con=engine, if_exists='append') #inserting chunk by chunk

        print("Inserted another chunk")


if __name__ == '__main__':

    run()