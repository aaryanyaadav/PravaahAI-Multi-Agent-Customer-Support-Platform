import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("SUPABASE_URL"))
print(os.getenv("SUPABASE_KEY")[:20])