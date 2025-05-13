from app.services.db import database as supabase



def write_to_db(audio_data):
    try:
        supabase.table("audio_recordings").insert(audio_data).execute()
        print("Data written in database!")
    except Exception as e:
        print(f"error writing to database")