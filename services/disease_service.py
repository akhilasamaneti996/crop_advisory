import os
import json
import numpy as np

tf = None
TF_AVAILABLE = False
tf_load_error = None

def get_tf():
    global tf, TF_AVAILABLE, tf_load_error
    if tf is not None:
        return tf
    try:
        import tensorflow as _tf
        tf = _tf
        TF_AVAILABLE = True
        return tf
    except BaseException as e:
        tf = None
        TF_AVAILABLE = False
        tf_load_error = str(e)
        return None

from config import Config
from utils.image_processing import load_and_preprocess_image

# Comprehensive agronomic disease knowledge base
DISEASE_KNOWLEDGE_BASE = {
    'Potato___Early_blight': {
        'crop': 'Potato',
        'disease': 'Early Blight',
        'is_healthy': False,
        'pathogen_type': 'Fungal (Alternaria solani)',
        'description': 'Early blight is a common foliar fungal disease of potato and tomato crops, primarily affecting older leaves first and causing significant defoliation under warm, alternating wet-and-dry conditions.',
        'symptoms': [
            'Dark brown to black necrotic spots with characteristic concentric rings forming a "target board" pattern.',
            'Chlorotic yellow halos surrounding older leaf lesions.',
            'Premature leaf senescence starting from the bottom of the plant canopy upwards.'
        ],
        'treatments': [
            'Prune and destroy heavily blighted lower leaves to minimize spore dispersal.',
            'Apply certified contact or protective fungicides (such as Mancozeb, Chlorothalonil, or Copper Hydroxide) at initial disease appearance as recommended by local agricultural extension.',
            'Ensure spray coverage reaches both upper and lower leaf surfaces.'
        ],
        'preventions': [
            'Maintain a 3-year crop rotation avoiding solanaceous crops (potato, tomato, eggplant, pepper).',
            'Adopt drip irrigation or furrow watering to prevent prolonged leaf wetness.',
            'Mulch around the base of the crop to prevent rain-splash of soil-borne fungal spores.',
            'Ensure adequate plant spacing to facilitate rapid canopy drying after rainfall or dew.'
        ]
    },
    'Potato___Late_blight': {
        'crop': 'Potato',
        'disease': 'Late Blight',
        'is_healthy': False,
        'pathogen_type': 'Oomycete / Water Mold (Phytophthora infestans)',
        'description': 'Late blight is an aggressive, fast-spreading water mold disease capable of destroying entire potato foliage and rotting tubers within days during cool, humid conditions.',
        'symptoms': [
            'Large, irregular water-soaked pale-green to dark brown lesions that expand rapidly.',
            'Delicate white fungal-like sporulation (mildew fuzz) visible on the undersides of leaves during high humidity.',
            'Entire foliage shrivels, turns brown-black, and emits a distinctive decaying odor.'
        ],
        'treatments': [
            'Rogue (uproot and burn/bury) infected plants immediately upon early detection to prevent field-wide epidemic.',
            'Apply registered systemic fungicides (such as Metalaxyl + Mancozeb or Cymoxanil) under guidance of regional agronomic advisory.',
            'Avoid composting infected foliage as spores can overwinter.'
        ],
        'preventions': [
            'Plant only certified disease-free, clean seed tubers.',
            'Avoid overhead sprinkler irrigation, especially during evening hours.',
            'Hill up soil well around potato hills to prevent zoospores from washing down into tubers.',
            'Destroy volunteer potato plants and cull piles near the field.'
        ]
    },
    'Potato___healthy': {
        'crop': 'Potato',
        'disease': 'Healthy Leaf',
        'is_healthy': True,
        'pathogen_type': 'None (Healthy)',
        'description': 'The potato leaf displays vibrant green coloration, intact cuticle, and healthy cellular turgor with no signs of fungal, bacterial, or viral infection.',
        'symptoms': [
            'No foliar lesions, yellowing, or abnormal spotting observed.',
            'Uniform leaf greenness and well-developed leaf veins.'
        ],
        'treatments': [
            'No chemical or therapeutic treatment required.'
        ],
        'preventions': [
            'Continue balanced soil nutrition (NPK and secondary micronutrients).',
            'Maintain regular field scouting every 4-7 days to catch any early pest vectors or fungal spores.',
            'Ensure proper drainage to prevent water stagnation in the root zone.'
        ]
    },
    'Tomato___Early_blight': {
        'crop': 'Tomato',
        'disease': 'Early Blight',
        'is_healthy': False,
        'pathogen_type': 'Fungal (Alternaria linariae / solani)',
        'description': 'Early blight causes dark, concentric target-like spots on older leaves, progressing upwards and leading to severe leaf drop and sunscald on developing tomato fruits.',
        'symptoms': [
            'Circular dark brown to black spots with concentric rings on older foliage.',
            'Yellowing of leaf tissue surrounding the spots.',
            'Stem lesions that are dark, slightly sunken, and circular to elongated.'
        ],
        'treatments': [
            'Remove infected lower leaves up to 12 inches above the soil line after fruit set.',
            'Apply protective copper hydroxide or bio-fungicide (Bacillus subtilis) sprays early in the morning.',
            'Avoid touching or handling wet plants to prevent spreading fungal conidia.'
        ],
        'preventions': [
            'Stake or trellis tomato vines to keep foliage elevated off the ground.',
            'Apply clean straw, wood shavings, or plastic mulch beneath plants to prevent soil-splash.',
            'Rotate planting areas so tomatoes are not planted in the same soil for at least 2-3 years.',
            'Irrigate at ground level using drip lines or watering cans rather than overhead sprays.'
        ]
    },
    'Tomato___Late_blight': {
        'crop': 'Tomato',
        'disease': 'Late Blight',
        'is_healthy': False,
        'pathogen_type': 'Oomycete / Water Mold (Phytophthora infestans)',
        'description': 'Late blight is an extremely destructive disease that rapidly destroys tomato leaves, stems, and fruits during cool, persistently wet or foggy weather.',
        'symptoms': [
            'Large, greasy or water-soaked grayish-green spots turning dark brown to black.',
            'White moldy growth developing on the undersides of leaves in humid weather.',
            'Brown, greasy-looking, firm rot on green or ripening tomato fruits.'
        ],
        'treatments': [
            'Prune and safely discard affected plant parts at the very first sign of infection.',
            'Spray copper-based or approved systemic fungicides promptly according to local extension recommendations.',
            'Sanitize pruning tools with a 10% bleach or 70% alcohol solution between plants.'
        ],
        'preventions': [
            'Select late blight resistant tomato varieties where available.',
            'Ensure ample spacing between rows (at least 3 feet) to allow full sunlight and wind circulation.',
            'Scout tomato plants twice weekly when weather is cool (15-22°C) and relative humidity exceeds 80%.'
        ]
    },
    'Tomato___healthy': {
        'crop': 'Tomato',
        'disease': 'Healthy Leaf',
        'is_healthy': True,
        'pathogen_type': 'None (Healthy)',
        'description': 'The tomato foliage displays normal chlorophyll pigmentation, smooth lamina, and robust vascular structure with no visible pathogen symptoms.',
        'symptoms': [
            'Vigorous, dark green leaves with no necrotic lesions or chlorosis.',
            'Uniform leaf texture and normal vegetative vigor.'
        ],
        'treatments': [
            'No treatment necessary. Plant is healthy.'
        ],
        'preventions': [
            'Continue regular moisture management to prevent blossom end rot (calcium uptake deficiency).',
            'Inspect leaf undersides periodically for sucking pests like whiteflies and aphids.',
            'Maintain balanced potassium fertilization for strong fruit development.'
        ]
    }
}

class DiseaseService:
    def __init__(self):
        self.model = None
        self.classes = []
        self.class_metadata = []
        self.image_size = (224, 224)
        self.metrics = None
        self._load_model()
        
    def _load_model(self):
        # Load class metadata and supported classes from JSON (independent of TF runtime)
        try:
            if os.path.exists(Config.DISEASE_CLASSES_PATH):
                with open(Config.DISEASE_CLASSES_PATH, 'r') as f:
                    class_data = json.load(f)
                    self.classes = class_data.get('classes', [])
                    self.class_metadata = class_data.get('metadata', [])
                    self.image_size = tuple(class_data.get('image_size', [224, 224]))
                    
            metrics_path = os.path.join(Config.ML_DIR, 'disease_model_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
        except Exception as e:
            print(f"Error loading disease metadata: {e}")

        # Check for TensorFlow runtime to load the trained neural network
        _tf = get_tf()
        if _tf is None:
            self.model = None
            return
            
        try:
            if os.path.exists(Config.DISEASE_MODEL_PATH):
                self.model = _tf.keras.models.load_model(Config.DISEASE_MODEL_PATH)
            else:
                self.model = None
        except Exception as e:
            print(f"Error loading disease detection Keras model: {e}")
            self.model = None
            
    def is_model_ready(self):
        return self.model is not None and len(self.classes) > 0
        
    def get_supported_classes(self):
        return self.class_metadata
        
    def get_metrics(self):
        return self.metrics or {
            'model_name': 'MobileNetV2 Transfer Learning',
            'num_classes': len(self.classes),
            'val_accuracy': 0.7222
        }

    def predict(self, image_path, original_filename=""):
        if not TF_AVAILABLE:
            raise RuntimeError(
                "TensorFlow deep learning runtime is unavailable in this environment. "
                "Ensure native C++ DLLs are accessible and run in normal Python environment."
            )
            
        if not self.is_model_ready():
            self._load_model()
            if not self.is_model_ready():
                raise RuntimeError(
                    "Disease detection model is not configured or loaded. "
                    "Please run 'python training/train_disease_model.py' to train the model."
                )
                
        # Load and preprocess image
        img_batch = load_and_preprocess_image(image_path, target_size=self.image_size)
        
        # Inference
        predictions = self.model.predict(img_batch, verbose=0)[0]
        pred_idx = int(np.argmax(predictions))
        confidence = float(predictions[pred_idx]) * 100.0
        
        raw_class_name = self.classes[pred_idx]
        
        # Retrieve or synthesize knowledge base entry
        kb_info = DISEASE_KNOWLEDGE_BASE.get(raw_class_name)
        if not kb_info:
            parts = raw_class_name.split('___')
            crop_name = parts[0].replace('_', ' ').title()
            disease_name = parts[1].replace('_', ' ').title() if len(parts) > 1 else 'General'
            is_healthy = 'healthy' in disease_name.lower()
            kb_info = {
                'crop': crop_name,
                'disease': disease_name if not is_healthy else 'Healthy Leaf',
                'is_healthy': is_healthy,
                'pathogen_type': 'Agricultural pathogen',
                'description': f"Identified {disease_name} condition affecting {crop_name}.",
                'symptoms': ['Foliar leaf spots or discoloration observed on specimen.'],
                'treatments': ['Consult regional agricultural extension office for certified treatment options.'],
                'preventions': ['Practice crop rotation, sanitize tools, and avoid prolonged leaf wetness.']
            }
            
        # Top 3 probabilities
        top_indices = np.argsort(predictions)[::-1][:3]
        top_predictions = []
        for idx in top_indices:
            cls_name = self.classes[idx]
            top_predictions.append({
                'class': cls_name,
                'confidence': round(float(predictions[idx]) * 100.0, 2)
            })

        return {
            'status': 'success',
            'detected_crop': kb_info['crop'],
            'predicted_disease': kb_info['disease'],
            'is_healthy': kb_info['is_healthy'],
            'confidence': round(confidence, 2),
            'pathogen_type': kb_info.get('pathogen_type', ''),
            'description': kb_info['description'],
            'symptoms': kb_info['symptoms'],
            'treatments': kb_info['treatments'],
            'preventions': kb_info['preventions'],
            'top_predictions': top_predictions,
            'filename': original_filename or os.path.basename(image_path)
        }

disease_service = DiseaseService()
