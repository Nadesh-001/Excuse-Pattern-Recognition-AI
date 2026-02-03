from datetime import datetime

def calculate_time_status(status, created_at, estimated_minutes):
    """
    Returns (status_text, color_code)
    """
    if not estimated_minutes:
        return None, None
        
    if isinstance(created_at, str):
        try:
             created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except:
             return None, None
             
    elapsed_minutes = int((datetime.now() - created_at).total_seconds() / 60)
    
    if status == 'Completed':
        if elapsed_minutes <= estimated_minutes:
            return f"✅ Done in {elapsed_minutes}m (On Time)", "#10b981"
        else:
            return f"⚠️ Done +{elapsed_minutes - estimated_minutes}m late", "#f59e0b"
            
    # Pending or Delayed
    if elapsed_minutes > estimated_minutes:
        return f"🔴 Over by {elapsed_minutes - estimated_minutes}m", "#ef4444"
    else:
        return f"⏳ {estimated_minutes - elapsed_minutes}m remaining", "#3b82f6"

def get_elapsed_str(created_at):
    if isinstance(created_at, str):
        try:
             created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except:
             return "N/A"
             
    delta = datetime.now() - created_at
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    
    return " ".join(parts)

def parse_time_input(hours, minutes):
    """
    Convert hours and minutes into total minutes.
    Returns total minutes as integer.
    """
    total_minutes = 0
    if hours:
        try:
            total_minutes += int(hours) * 60
        except (ValueError, TypeError):
            pass
    if minutes:
        try:
            total_minutes += int(minutes)
        except (ValueError, TypeError):
            pass
    return total_minutes

