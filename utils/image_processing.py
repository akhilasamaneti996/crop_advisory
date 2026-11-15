import os
import uuid
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file_storage, upload_folder):
    os.makedirs(upload_folder, exist_ok=True)
    orig_filename = secure_filename(file_storage.filename)
    extension = orig_filename.rsplit('.', 1)[1].lower() if '.' in orig_filename else 'jpg'
    unique_filename = f"{uuid.uuid4().hex}_{orig_filename}"
    file_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(file_path)
    return unique_filename, file_path

def load_and_preprocess_image(image_path, target_size=(224, 224)):
    """
    Loads an image from image_path, ensures RGB mode, resizes to target_size,
    and returns a numpy array with shape (1, target_size[0], target_size[1], 3).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")
        
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        img_array = np.array(img, dtype=np.float32)
        # Add batch dimension: (1, 224, 224, 3)
        img_batch = np.expand_dims(img_array, axis=0)
        return img_batch

