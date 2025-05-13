import os 
from dotenv import load_dotenv
import requests
import time 
import io 


load_dotenv()

url = os.getenv("AI_SERVER_ENDPOINT")

# ADD IF AI SERVER NOT RESPONSIVE 

def request_ai_description(audio_file: io.BytesIO):
    start_time = time.time()

    files = { "file": audio_file }
    response = requests.post(url, files=files)

    end_time = time.time()

    try:
        response_json = response.json()  # Parse JSON
        ai_description = response_json.get("description", "No description found")
    except ValueError:
        print(response.text)
        ai_description = "Error"  


    time_ai_get = end_time - start_time
    print(f"AI Server time elapsed: {time_ai_get}")
    return ai_description  
