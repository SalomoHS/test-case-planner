from supabase import create_client
from dotenv import load_dotenv
import os
load_dotenv()

supabase_admin = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SECRET_KEY")
)

supabase_client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_ANON_KEY")
)