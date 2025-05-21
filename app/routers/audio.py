from email.mime import audio
from fastapi import APIRouter, Request
from app.services import ai_description
from app.services.process_audio import process_audio
from app.services.ai_description import request_ai_description
from app.services.writedb import write_to_db
import numpy as np 
import wave 
import io
import datetime
import pytz
# import os  

router = APIRouter()

# Configurations/ constants:
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 4    # Bytes per sample
NUM_CHANNELS = 1    # Mono 
LEQ_PERIOD_SEC = 10 # Number of seconds to be recorded
SAMPLES_PER_LEQ = SAMPLE_RATE * LEQ_PERIOD_SEC
bytes_needed_for_leq = SAMPLES_PER_LEQ * SAMPLE_WIDTH
GAIN = 8


buffered_audio = bytearray()

@router.post("/upload/{session_id}")
async def receive_audio_chunk(session_id: int, request: Request): 
    """
    Receives audio chunk from the ESP32 hardware
    """
    data = await request.body()
    buffered_audio.extend(data)
    print(request.headers)
    print_stats()

    # Need timeout logic 
    if len(buffered_audio) >= bytes_needed_for_leq: 
        # This is the indicator that this is the one minute file that will be saved in the database

        # Compute DBA
        dBA = process_audio(SAMPLES_PER_LEQ, buffered_audio)
        print(f"dBA level: {dBA}")
        
        # Get AI Description
        audio_file = save_file()
        ai_description = request_ai_description(audio_file)
        print(ai_description)
        
        # Write Time 
        utc_now = datetime.datetime.now(pytz.utc)
        gmt8 = utc_now.astimezone(pytz.timezone("Asia/Manila"))
        timestamp = gmt8.strftime("%H:%M")
        # Write to Database
        # pass ai_description, dBA level, point_id (hard coded), session_id(hard coded)
        

        audio_data = {
            "session_id": session_id,
            "db_level": dBA,
            "start_time": timestamp, # 10:00 24 hr format  
            "analysis_text": ai_description
        }
        write_to_db(audio_data)

        # clear buffer
        buffered_audio.clear()

def print_stats():
    current_time_stored = len(buffered_audio) // ( SAMPLE_RATE * SAMPLE_WIDTH ) 
    time_stats = f"Time recorded: {current_time_stored} / {LEQ_PERIOD_SEC}"
    size_stats = f"Size buffered: {len(buffered_audio)} / {bytes_needed_for_leq}"
    print(size_stats)
    print(time_stats)

def save_file():
    # Code that ehhances volume when file is saved
    # 1. Convert bytes to NumPy int32 array
    audio_array = np.frombuffer(bytes(buffered_audio), dtype=np.int32)

    # 2. Amplify audio
    amplified = audio_array.astype(np.float64) * GAIN # Promote to float for multiplication to avoid overflow
    amplified = np.clip(amplified, -2147483648, 2147483647).astype(np.int32)

    # 3. Convert back to bytes
    amplified_bytes = amplified.tobytes()

    buffer_file = io.BytesIO()
    with wave.open(buffer_file, 'wb') as wf:
        wf.setnchannels(NUM_CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(amplified_bytes)

    buffer_file.seek(0)
    return buffer_file

# def old_save_file():
#     OUTPUT_DIR = "save_audio"
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.wav")

#     # Code that ehhances volume when file is saved
#     # 1. Convert bytes to NumPy int16 array
#     audio_array = np.frombuffer(bytes(buffered_audio), dtype=np.int16)

#     # 2. Amplify audio
#     amplified = audio_array * GAIN
#     amplified = np.clip(amplified, -32768, 32767).astype(np.int16)

#     # 3. Convert back to bytes
#     amplified_bytes = amplified.tobytes()

#     with wave.open(filename, 'wb') as wf:
#         wf.setnchannels(NUM_CHANNELS)
#         wf.setsampwidth(SAMPLE_WIDTH)
#         wf.setframerate(SAMPLE_RATE)
#         wf.writeframes(amplified_bytes)

#     print(f"Saved: {filename}")
