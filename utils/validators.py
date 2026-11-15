from utils.image_processing import allowed_file

def validate_crop_inputs(data):
    """
    Validates numeric agronomic parameters for crop recommendation.
    Returns (is_valid, errors_dict, cleaned_data)
    """
    errors = {}
    cleaned = {}
    
    fields = {
        'nitrogen': (0.0, 300.0, 'Nitrogen (N) must be between 0 and 300 kg/ha.'),
        'phosphorus': (0.0, 300.0, 'Phosphorus (P) must be between 0 and 300 kg/ha.'),
        'potassium': (0.0, 300.0, 'Potassium (K) must be between 0 and 300 kg/ha.'),
        'temperature': (-10.0, 60.0, 'Temperature must be between -10°C and 60°C.'),
        'humidity': (0.0, 100.0, 'Humidity must be between 0% and 100%.'),
        'ph': (0.0, 14.0, 'Soil pH must be between 0.0 and 14.0.'),
        'rainfall': (0.0, 1500.0, 'Rainfall must be between 0 and 1500 mm.')
    }
    
    for field, (min_v, max_v, msg) in fields.items():
        val = data.get(field)
        if val is None or val == '':
            # check alternative name (e.g. n, p, k)
            short_key = field[0] if field in ['nitrogen', 'phosphorus', 'potassium'] else field
            val = data.get(short_key)
            
        if val is None or val == '':
            errors[field] = f"{field.title()} is required."
            continue
            
        try:
            f_val = float(val)
            if not (min_v <= f_val <= max_v):
                errors[field] = msg
            else:
                cleaned[field] = f_val
        except (ValueError, TypeError):
            errors[field] = f"{field.title()} must be a valid number."
            
    # Contextual fields
    cleaned['location'] = str(data.get('location', '')).strip()[:100]
    cleaned['soil_type'] = str(data.get('soil_type', 'Loamy')).strip()[:50]
    cleaned['season'] = str(data.get('season', 'Kharif')).strip()[:50]
    cleaned['growth_stage'] = str(data.get('growth_stage', 'Vegetative')).strip()[:50]

    return len(errors) == 0, errors, cleaned

def validate_image_upload(file_storage, max_size_mb=16):
    """
    Validates uploaded image file object.
    Returns (is_valid, error_message)
    """
    if not file_storage or file_storage.filename == '':
        return False, "No file was selected for upload."
        
    if not allowed_file(file_storage.filename):
        return False, "Unsupported file format. Please upload a JPG, JPEG, or PNG image."
        
    # Check size if available via content_length
    if file_storage.content_length and file_storage.content_length > max_size_mb * 1024 * 1024:
        return False, f"File size exceeds maximum allowed limit of {max_size_mb} MB."
        
    return True, None

