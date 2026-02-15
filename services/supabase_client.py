"""
Supabase Backend Client
BACKEND USE ONLY - Uses service role key to bypass RLS
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# WARNING: This client uses the SERVICE ROLE KEY
# It bypasses Row Level Security (RLS)
# NEVER expose this to the frontend or client-side code
# Use ONLY in server-side Python code

_supabase_client: Client = None


def get_supabase_client() -> Client:
    """
    Get Supabase client with service role privileges.
    
    WARNING: This client bypasses RLS. Use carefully!
    Perfect for:
    - Admin operations
    - Background tasks
    - Server-side file uploads
    - System-level queries
    
    NEVER use in:
    - Frontend JavaScript
    - Public API endpoints
    - User-facing code
    
    Returns:
        Supabase client with full access
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            raise ValueError(
                "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env"
            )
        
        _supabase_client = create_client(supabase_url, service_key)
    
    return _supabase_client


# For convenience exports
supabase = get_supabase_client
