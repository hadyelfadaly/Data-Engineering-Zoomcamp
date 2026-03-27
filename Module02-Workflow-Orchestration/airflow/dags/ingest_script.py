#libraries used for linking with postgresql
import pandas as pd
from sqlalchemy import create_engine

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

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, table_name, chunk_size, csv_file):

    print(table_name, csv_file)

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')
    engine.connect() #to check if the connection is successful

    print("Connection to PostgreSQL database established successfully, ingesting data...")

    first = True

    #to divide the data into chunks of equal size so we can inser chunk by chunk
    df_iter = pd.read_csv(
        csv_file,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunk_size
    )

    for df_chunk in df_iter:

        if first:

            df_chunk.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace') #creating table
            #this line ensures idempotency,
            #if we run the script multiple times it will not create duplicate tables, 
            #it will just replace the existing table with the new one, 
            #and since we are using head(n=0) it will create an empty table with the same structure as the original data,
            #and then we will insert the data chunk by chunk,
            #and since we are using if_exists='append' it will append the data to the existing table without creating duplicates,
            #and since we are using first variable to check if it's the first chunk or not,
            #we will only create the table once and then we will append the data to it,
            #and after the first chunk is inserted we will set first to False so we will not create the table again and we will just append the data to it.

            first = False

            print("Table created successfully")

        df_chunk.to_sql(name=table_name, con=engine, if_exists='append') #inserting chunk by chunk

        print("Inserted another chunk")