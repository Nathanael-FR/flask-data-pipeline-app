# Insert data into the postgres database

import psycopg2
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()

POSTGRES_DB_LINK = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(

    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME')
)

def connect():
    try:
        engine = create_engine(POSTGRES_DB_LINK)

        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("Connection successful")
        return engine
    
    except Exception as e:
        raise Exception(f"An error occurred while connecting to the database: {e}")

def insert_data(df):  
    try:
        engine = create_engine(POSTGRES_DB_LINK)
        df.to_sql('eco2mix_data', engine, if_exists='append', index=False)
        print("Data inserted successfully")
    except Exception as e:
        raise Exception(f"An error occurred while inserting into postgres: {e}")

