# Retrieve the data from the eco2mix API and update the database
from __future__ import unicode_literals
import requests
from datetime import datetime, timedelta
from zipfile import ZipFile
import io
import pandas as pd
from xlwt import Workbook
import os
from typing import Union

DATA_URL = "https://eco2mix.rte-france.com/curves/eco2mixDl?date={}/{}/{}"

def get_last_date():

    yesterday_date = datetime.now() - timedelta(days=1)
    day, month, year = yesterday_date.day,  yesterday_date.month, yesterday_date.year

    day = f'0{day}' if day < 10 else day
    month = f'0{month}' if month < 10 else month

    return day, month, year

def fetch_data(day: Union[str,int], month: Union[str,int], year: int) -> None:
    try:
        res = requests.get(DATA_URL.format(day, month, year))
        res = res.content
        z = ZipFile(io.BytesIO(res))
        z.extractall("./data/")
    except Exception as e:
        raise Exception(f"An error occurred while fetching the data: {e}")
    else:
        file_path = f"./data/eCO2mix_RTE_{year}-{month}-{day}.xls"
        if not os.path.exists(file_path):
            raise Exception("The file has not been downloaded")

def repair_data(day, month, year) -> pd.DataFrame:

    try : 
        data_file = io.open(f"./data/eCO2mix_RTE_{year}-{month}-{day}.xls", "r", encoding="iso-8859-1")
        data = data_file.readlines()
        xldoc = Workbook()

        sheet = xldoc.add_sheet("Sheet1", cell_overwrite_ok=True)
        # Iterating and saving the data to sheet
        for i, row in enumerate(data):
            # Two things are done here
            # Removeing the '\n' which comes while reading the file using io.open
            # Getting the values after splitting using '\t'
            for j, val in enumerate(row.replace('\n', '').split('\t')):
                sheet.write(i, j, val)
    except Exception as e:
        raise Exception(f"An error occurred while repairing the data file fetched: {e}")
    
    else :
        xldoc.save(f'./data/eCO2mix_RTE_{year}-{month}-{day}_repaired.xls')
        df = pd.ExcelFile(f'./data/eCO2mix_RTE_{year}-{month}-{day}_repaired.xls').parse('Sheet1')
        return df

def del_excel_files(day, month, year) -> None:
    
    file_path = f"./data/eCO2mix_RTE_{year}-{month}-{day}"
    
    try :
        if os.path.exists(file_path + '.xls'):
            os.remove(file_path + '.xls')
            print(f'{file_path}.xls has been deleted')

        if os.path.exists(file_path + '_repaired.xls'):
            os.remove(file_path + '_repaired.xls')
            print(f'{file_path}_repaired.xls has been deleted')
    except Exception as e:
        print(f"Files couldn't been removed: {e}")

def clean_data(df):
    
    try : 
        df = df.drop(columns=["Périmètre","Nature","Consommation corrigée"])
        df.drop(df.tail(1).index,inplace = True)
        df.columns = df.columns.str.normalize('NFKD')\
                                    .str.encode('ascii', errors='ignore')\
                                    .str.decode('utf-8')\
                                    .str.strip()\
                                    .str.replace(" - ","_")\
                                    .str.replace(". ","_")\
                                    .str.replace("?","_")\
                                    .str.replace(" ","_")\
                                    .str.replace(".","")\
                                    .str.replace("-","_")\
                                    .str.lower()
        
        df.rename(
            columns={
                "hydraulique_fil_de_l_eau_+_eclusee":"hydraulique_fildeleau_eclusee",
                
            }, inplace=True)

        df["date"] = pd.to_datetime(df["date"])
        df['heures'] = pd.to_datetime(df['heures'], format='%H:%M').dt.time
        df['date_heures'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['heures'].astype(str))

        df['heures'] = df['heures'].astype('string')

        int32_cols = ["consommation","prevision_j_1","prevision_j","nucleaire"]

        int16_cols = [col for col in df.columns if col not in ["date","heures","date_heures"]+int32_cols]

        df[int32_cols] = df[int32_cols].apply(pd.to_numeric, 
                                            errors='coerce', downcast='integer')\
                                                .astype("Int32")

        df[int16_cols] = df[int16_cols].apply(pd.to_numeric, 
                                            errors='coerce', downcast='integer')\
                                                .astype("Int16")
    except Exception as e:
        raise Exception(f"An error occurred while cleaning the data: {e}")
    
    else :
        return df

if __name__ == "__main__":

    day, month, year = get_last_date()
    fetch_data(day, month, year)
    df = repair_data(day, month, year)
    df = clean_data(df)
    del_excel_files(day, month, year)
