import os 
from dotenv import load_dotenv
from pytest import param
import requests
import time 
import io 


load_dotenv()

url = os.getenv("AI_SERVER_ENDPOINT")

# ADD IF AI SERVER NOT RESPONSIVE 

def request_ai_description(audio_file: io.BytesIO):
    start_time = time.time()

    files = { "file": audio_file }
    response = requests.post(url + "describe", files=files)

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

def request_session_description(analysis_texts: str): 
    # print(analysis_texts)
    start_time = time.time()
    response = requests.post(url + "summarize", params={"descriptions": analysis_texts})
    end_time = time.time()

    try: 
        response_json = response.json()
        session_description = response_json.get("summary", "Error generating AI response, please try again!")
    except ValueError:
        print(response.text)
        session_description = "Error accessing AI endpoint, please try again!"
    
    time_ai_get = end_time - start_time
    print(f"Session Description: {session_description}, time elapsed: {time_ai_get}")

    return session_description