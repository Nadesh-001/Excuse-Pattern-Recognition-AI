"""
Secure File Upload Service
Handles validated file uploads to Supabase Storage
"""

from utils.file_validation import validate_file, get_safe_filename
from services.supabase_client import get_supabase_client


STORAGE_BUCKET = "ai files"  # Supabase Storage bucket name


def upload_file(file, custom_filename=None, folder=""):
    """
    Upload file to Supabase Storage with validation.
    
    Args:
        file: Flask file object from request.files
        custom_filename: Optional custom filename (will be sanitized)
        folder: Optional folder path (e.g., "tasks/123")
        
    Returns:
        dict with 'success', 'url', 'path', or 'error'
        
    Raises:
        ValueError: If file validation fails
        
    Example:
        file = request.files['file']
        result = upload_file(file, folder="tasks/42")
        if result['success']:
            print(f"Uploaded: {result['url']}")
    """
    try:
        # Validate file security
        validate_file(file)
        
        # Generate safe filename
        if custom_filename:
            safe_filename = get_safe_filename(custom_filename)
        else:
            safe_filename = get_safe_filename(file.filename)
        
        # Construct storage path
        if folder:
            storage_path = f"{folder}/{safe_filename}"
        else:
            storage_path = safe_filename
        
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset for potential reuse
        
        # Upload to Supabase Storage
        supabase = get_supabase_client()
        
        response = supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
        
        return {
            'success': True,
            'url': public_url,
            'path': storage_path,
            'filename': safe_filename,
            'size': len(file_content),
            'mime_type': file.content_type
        }
        
    except ValueError as e:
        # Validation error
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        # Upload error
        return {
            'success': False,
            'error': f"Upload failed: {str(e)}"
        }


def delete_file(storage_path):
    """
    Delete file from Supabase Storage.
    
    Args:
        storage_path: Full path in storage (e.g., "tasks/123/file.pdf")
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        supabase = get_supabase_client()
        supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False


def get_file_url(storage_path):
    """
    Get public URL for a file.
    
    Args:
        storage_path: Full path in storage
        
    Returns:
        str: Public URL
    """
    supabase = get_supabase_client()
    return supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
