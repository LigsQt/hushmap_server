import os 
from dotenv import load_dotenv
from supabase import create_client
import datetime
import pytz 

load_dotenv()

SUPABASE_URL: str  = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str  = os.getenv("SUPABASE_KEY")

database = create_client(SUPABASE_URL, SUPABASE_KEY)


def is_point_active(point_id: int) -> bool:
    print(f"{point_id}")
    try:
        session_response = database.table("sessions") \
            .select("session_id, end_date") \
            .eq("point_id", point_id)\
            .order("session_id", desc=True) \
            .limit(1) \
            .execute()
        
        latest_id = session_response.data[0]["session_id"]
        latest_date = session_response.data[0]["end_date"] 
    except:
        return False
  
    print(f"latest session: {latest_id}")
    
    
    data_res = database.table("audio_recordings") \
        .select("start_time")\
        .eq("session_id", latest_id)\
        .order("id", desc=True) \
        .limit(1) \
        .execute()
    
    latest_time = data_res.data[0]["start_time"]

    utc_now = datetime.datetime.now(pytz.utc)
    gmt8 = utc_now.astimezone(pytz.timezone("Asia/Manila"))
    current_day =  gmt8.date()

    print(current_day)
    print(f"time:{latest_date} {latest_time}")

    if str(current_day) != str(latest_date):
        return False 
    
    input_time_today = pytz.timezone("Asia/Manila").localize(
    datetime.datetime.combine(gmt8.date(), datetime.datetime.strptime(latest_time, "%H:%M").time())
)

    delta = gmt8 - input_time_today
    print(f"{delta} | {input_time_today}, {gmt8}")   
    # get latest time point
    # compare to actual time  
    if datetime.timedelta(0) < delta < datetime.timedelta(hours=1):
        return True
    else:
        return False
    