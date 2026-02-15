"""
Supabase Storage Service
Handles file uploads, downloads, and management for task attachments
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, List
import mimetypes
import time
import hashlib

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY_ANON")

supabase: Client = None

def get_supabase_client():
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY_ANON in .env")
        supabase = create_client(supabase_url, supabase_key)
    return supabase


class StorageService:
    """
    Service for handling file storage operations.
    
    Bucket: 'ai files' (PUBLIC)
    Allowed types: image/png, image/jpeg, application/pdf, application/json, text/csv
    Max size: 50 MB
    """
    
    BUCKET_NAME = "ai files"  # Your bucket name from Supabase
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    
    ALLOWED_MIME_TYPES = {
        'image/png',
        'image/jpeg',
        'image/jpg',
        'application/pdf',
        'application/json',
        'text/csv',
        'text/plain'
    }
    
    ALLOWED_EXTENSIONS = {
        'png', 'jpg', 'jpeg', 'pdf', 'json', 'csv', 'txt'
    }
    
    @staticmethod
    def validate_file(filename: str, file_size: int = None) -> tuple:
        """
        Validate file type and size.
        
        Returns:
            (is_valid: bool, error_message: str or None)
        """
        # Check extension
        if '.' not in filename:
            return False, "File must have an extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in StorageService.ALLOWED_EXTENSIONS:
            return False, f"File type .{ext} not allowed. Allowed: {', '.join(StorageService.ALLOWED_EXTENSIONS)}"
        
        # Check file size
        if file_size and file_size > StorageService.MAX_FILE_SIZE:
            size_mb = StorageService.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {size_mb} MB"
        
        return True, None
    
    @staticmethod
    def generate_secure_filename(original_filename: str, user_id: int = None) -> str:
        """
        Generate secure, unique filename.
        
        Args:
            original_filename: Original file name
            user_id: Optional user ID for namespacing
            
        Returns:
            Secure filename with timestamp and hash
        """
        timestamp = int(time.time())
        
        # Hash for uniqueness
        hash_input = f"{user_id or 'anon'}_{timestamp}_{original_filename}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        # Keep extension
        ext = original_filename.rsplit('.', 1)[1] if '.' in original_filename else ''
        
        if user_id:
            return f"{user_id}_{timestamp}_{file_hash}.{ext}"
        return f"{timestamp}_{file_hash}.{ext}"
    
    @staticmethod
    def upload_file(file_path: str, file_name: str, folder: str = "") -> dict:
        """
        Upload a file from local path to Supabase Storage.
        
        Args:
            file_path: Local path to file
            file_name: Name to save as in storage
            folder: Optional folder path (e.g., "tasks/123")
            
        Returns:
            dict with 'success', 'path', 'url', or 'error'
        """
        try:
            # Validate file size
            file_size = os.path.getsize(file_path)
            is_valid, error = StorageService.validate_file(file_name, file_size)
            if not is_valid:
                return {'success': False, 'error': error}
            
            # Construct storage path
            storage_path = f"{folder}/{file_name}" if folder else file_name
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_name)
            if mime_type not in StorageService.ALLOWED_MIME_TYPES:
                return {'success': False, 'error': f"MIME type {mime_type} not allowed"}
            
            # Upload to Supabase
            client = get_supabase_client()
            response = client.storage.from_(StorageService.BUCKET_NAME).upload(
                path=storage_path,
                file=file_data,
                file_options={"content-type": mime_type or "application/octet-stream"}
            )
            
            # Get public URL
            public_url = client.storage.from_(StorageService.BUCKET_NAME).get_public_url(storage_path)
            
            return {
                'success': True,
                'path': storage_path,
                'url': public_url,
                'size': file_size,
                'mime_type': mime_type
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def upload_from_bytes(file_bytes: bytes, file_name: str, folder: str = "", mime_type: str = None) -> dict:
        """
        Upload file from bytes (useful for Flask file uploads).
        
        Args:
            file_bytes: File content as bytes
            file_name: Name to save as
            folder: Optional folder path (e.g., "tasks/123")
            mime_type: MIME type (auto-detected if None)
            
        Returns:
            dict with 'success', 'path', 'url', or 'error'
        """
        try:
            # Validate file size
            file_size = len(file_bytes)
            is_valid, error = StorageService.validate_file(file_name, file_size)
            if not is_valid:
                return {'success': False, 'error': error}
            
            # Construct storage path
            storage_path = f"{folder}/{file_name}" if folder else file_name
            
            # Detect MIME type if not provided
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(file_name)
            
            # Validate MIME type
            if mime_type and mime_type not in StorageService.ALLOWED_MIME_TYPES:
                return {'success': False, 'error': f"MIME type {mime_type} not allowed"}
            
            # Upload to Supabase
            client = get_supabase_client()
            response = client.storage.from_(StorageService.BUCKET_NAME).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": mime_type or "application/octet-stream"}
            )
            
            # Get public URL
            public_url = client.storage.from_(StorageService.BUCKET_NAME).get_public_url(storage_path)
            
            return {
                'success': True,
                'path': storage_path,
                'url': public_url,
                'size': file_size,
                'mime_type': mime_type
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def download_file(storage_path: str) -> bytes:
        """
        Download a file from storage.
        
        Args:
            storage_path: Path in storage (e.g., "tasks/123/document.pdf")
            
        Returns:
            File bytes or None on error
        """
        try:
            client = get_supabase_client()
            response = client.storage.from_(StorageService.BUCKET_NAME).download(storage_path)
            return response
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    @staticmethod
    def delete_file(storage_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            storage_path: Path in storage
            
        Returns:
            True if deleted successfully
        """
        try:
            client = get_supabase_client()
            client.storage.from_(StorageService.BUCKET_NAME).remove([storage_path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def list_files(folder: str = "") -> List[dict]:
        """
        List files in a folder.
        
        Args:
            folder: Folder path (empty for root)
            
        Returns:
            List of file objects
        """
        try:
            client = get_supabase_client()
            response = client.storage.from_(StorageService.BUCKET_NAME).list(folder)
            return response
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    @staticmethod
    def get_public_url(storage_path: str) -> str:
        """
        Get public URL for a file.
        
        Args:
            storage_path: Path in storage
            
        Returns:
            Public URL string
        """
        client = get_supabase_client()
        return client.storage.from_(StorageService.BUCKET_NAME).get_public_url(storage_path)
    
    @staticmethod
    def create_signed_url(storage_path: str, expires_in: int = 3600) -> str:
        """
        Create a temporary signed URL (for private files).
        
        Args:
            storage_path: Path in storage
            expires_in: URL expiration in seconds (default 1 hour)
            
        Returns:
            Signed URL or None on error
        """
        try:
            client = get_supabase_client()
            response = client.storage.from_(StorageService.BUCKET_NAME).create_signed_url(
                storage_path, 
                expires_in
            )
            return response['signedURL']
        except Exception as e:
            print(f"Error creating signed URL: {e}")
            return None
