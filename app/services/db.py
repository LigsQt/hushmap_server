import os 
from dotenv import load_dotenv
from supabase import create_client 

load_dotenv()

SUPABASE_URL: str  = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str  = os.getenv("SUPABASE_KEY")

database = create_client(SUPABASE_URL, SUPABASE_KEY)