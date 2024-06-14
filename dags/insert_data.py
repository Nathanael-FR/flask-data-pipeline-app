# Insert data into the postgres database

import psycopg2
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()

def connect():
    try:
        engine = create_engine(f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')
        # Vérifiez la connexion
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("Connection successful")
        return engine
    except Exception as e:
        raise Exception(f"An error occurred while connecting to the database: {e}")

def insert_data(df):  
    try:
        engine = create_engine(f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')
        df.to_sql('eco2mix_data', engine, if_exists='append', index=False)
        print("Data inserted successfully")
    except Exception as e:
        raise Exception(f"An error occurred while inserting into postgres: {e}")

