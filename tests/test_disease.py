import pytest
import os
from utils.image_processing import allowed_file
from utils.validators import validate_image_upload
from services.disease_service import disease_service

def test_allowed_file_extensions():
    assert allowed_file('leaf.jpg') is True
    assert allowed_file('LEAF.JPEG') is True
    assert allowed_file('sample.png') is True
    assert allowed_file('script.exe') is False
    assert allowed_file('notes.txt') is False
    assert allowed_file('noextension') is False

def test_disease_supported_classes():
    classes = disease_service.get_supported_classes()
    assert len(classes) >= 6
    class_names = [c['raw_name'] for c in classes]
    assert 'Tomato___Early_blight' in class_names
    assert 'Potato___Early_blight' in class_names

def test_disease_inference_on_sample():
    sample_dir = 'data/datasets/plant_village_sample/Tomato___Early_blight'
    if os.path.exists(sample_dir) and disease_service.is_model_ready():
        img_name = os.listdir(sample_dir)[0]
        img_path = os.path.join(sample_dir, img_name)
        res = disease_service.predict(img_path, img_name)
        assert res['status'] == 'success'
        assert 'detected_crop' in res
        assert 'predicted_disease' in res
        assert 'confidence' in res
        assert len(res['symptoms']) > 0
        assert len(res['treatments']) > 0

