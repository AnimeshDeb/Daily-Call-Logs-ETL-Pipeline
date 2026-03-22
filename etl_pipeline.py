import pandas as pd
from datetime import datetime
from supabase import create_client, Client 
import uuid
import os 
from dotenv import load_dotenv 
from google.oauth2.service_account import Credentials
import gspread
import random
import json
load_dotenv()

SUPABASE_URL=os.environ.get("SUPABASE_URL")
SUPABASE_KEY=os.environ.get("SUPABASE_KEY")
CSV_FILE_PATH="simulated_call_centre.csv"


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing supabase credentials. check the .env file.")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
google_creds_json=os.environ.get("GOOGLE_CREDENTIALS")
if google_creds_json:
    info=json.loads(google_creds_json)
    creds=Credentials.from_service_account_info(info,scopes=scope)
else:
    creds=Credentials.from_service_account_file("credentials.json", scopes=scope)

client = gspread.authorize(creds)
sheet = client.open("Call_Centre_Life_Data").sheet1

def push_to_sheet(df):
    try:
        gs_df=df.copy()

        gs_df['call_arrived_time'] = gs_df['call_arrived_time'].astype(str)
        gs_df['call_answered_time'] = gs_df['call_answered_time'].astype(str)

        data_to_push = [gs_df.columns.values.tolist()] + gs_df.values.tolist()
        sheet.clear()
        sheet.update('A1', data_to_push)
        print("Successfully updated google sheets.")


    except Exception as e:
        print(f"Google sheets error {e}")


def run_etl():
    print("Starting ETL Pipeline...")



    #extracting 

    print("Extracting data...")


    try:
        df=pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        print(f"Error: Could not find the file '{CSV_FILE_PATH}'. Make sure it's in the same folder as this script.")

        return 
    daily_batch=df.sample(n=150).copy()

    #transforming

    print("Transforming data and simulated timestamps...")


    daily_batch['call_id']=[str(uuid.uuid4()) for _ in range(len(daily_batch))]

    call_categories = ['General Inquiry', 'Technical Support', 'Billing', 'Cancellations', 'Returns']
    daily_batch['call_type'] = [random.choice(call_categories) for _ in range(len(daily_batch))]
    daily_batch['wait_time_seconds']=daily_batch['wait_length'].fillna(0).astype(int)
    daily_batch['service_time_seconds']=daily_batch['service_length'].fillna(0).astype(int)


    #overwriting kaggle dates with today's date

    today_str=datetime.now().strftime('%Y-%m-%d')

    #grabbing call_arrived_time and attaching todays date to it

    
    daily_batch['call_arrived_time']=pd.to_datetime(today_str+' ' + daily_batch['call_started'].astype(str))

    #calculating answered time by adding the wait length to the arrival time
    daily_batch['call_answered_time']=daily_batch['call_arrived_time']+ pd.to_timedelta(daily_batch['wait_time_seconds'], unit='s')

    #calculating sla target
    daily_batch['sla_met']=daily_batch['wait_time_seconds']<=60

    final_df=daily_batch[[
        'call_id', 'call_type', 'call_arrived_time', 
        'call_answered_time', 'wait_time_seconds', 
        'service_time_seconds', 'sla_met'
    ]].copy()

    push_to_sheet(final_df)

    #converting timestamps to strings for supabase
    final_df['call_arrived_time']=final_df['call_arrived_time'].astype(str)
    final_df['call_answered_time']=final_df['call_answered_time'].astype(str)

    #converting dataframe into a list of dictionaries
    records=final_df.to_dict(orient='records')

    #load


    print(f"Loading {len(records)} records into supabase...")

    #inserting data into supabase table

    response=supabase.table('daily_call_logs').insert(records).execute()

    print("ETL pipeline completed successfully! Data is live in supabase.")

if __name__=="__main__":
    run_etl()







