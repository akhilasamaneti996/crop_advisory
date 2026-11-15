import os
import json
import argparse
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2

def train_plant_disease_model(
    data_dir='data/datasets/plant_village_sample',
    model_save_path='ml_models/disease_model.keras',
    classes_save_path='ml_models/disease_classes.json',
    metrics_save_path='ml_models/disease_model_metrics.json',
    epochs=6,
    batch_size=8,
    img_size=(224, 224)
):
    print("=" * 60)
    print("TRAINING PLANT DISEASE DETECTION MODEL (MOBILENETV2)")
    print("=" * 60)
    
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Image dataset directory not found at: {data_dir}")
        
    print(f"[1/6] Scanning image dataset from: {data_dir}")
    train_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=img_size,
        batch_size=batch_size
    )
    
    val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=img_size,
        batch_size=batch_size
    )
    
    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"      Identified {num_classes} classes: {class_names}")
    
    # Cache and prefetch for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(100).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    print("[2/6] Building MobileNetV2 Transfer Learning Architecture...")
    # Data augmentation pipeline
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.15),
        layers.RandomZoom(0.1),
    ], name="data_augmentation")
    
    # Preprocessing layer for MobileNetV2: scales pixels to [-1, 1]
    preprocess_input = keras.applications.mobilenet_v2.preprocess_input
    
    # Base pretrained model
    base_model = MobileNetV2(
        input_shape=(img_size[0], img_size[1], 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base layers for transfer learning
    
    inputs = keras.Input(shape=(img_size[0], img_size[1], 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.25)(x)
    x = layers.Dense(128, activation='relu')(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = keras.Model(inputs, outputs, name="CropDiseaseMobileNetV2")
    
    print("[3/6] Compiling Model...")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"[4/6] Training model for {epochs} epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        verbose=1
    )
    
    print("[5/6] Evaluating on validation dataset...")
    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    print(f"\n--- EVALUATION RESULTS ---")
    print(f"Validation Loss:     {val_loss:.4f}")
    print(f"Validation Accuracy: {val_acc * 100:.2f}%")
    
    print("[6/6] Saving trained model and class labels...")
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    model.save(model_save_path)
    
    # Format class metadata dictionary
    class_metadata = []
    for idx, name in enumerate(class_names):
        # Format crop and disease from standard naming convention (e.g. Tomato___Early_blight)
        parts = name.split('___')
        crop = parts[0].replace('_', ' ')
        disease = parts[1].replace('_', ' ') if len(parts) > 1 else 'General'
        class_metadata.append({
            'index': idx,
            'raw_name': name,
            'crop': crop.title(),
            'disease': disease.title() if disease.lower() != 'healthy' else 'Healthy Leaf',
            'is_healthy': 'healthy' in disease.lower()
        })
        
    with open(classes_save_path, 'w') as f:
        json.dump({
            'classes': class_names,
            'metadata': class_metadata,
            'image_size': list(img_size)
        }, f, indent=2)
        
    metrics = {
        'model_name': 'MobileNetV2 Transfer Learning',
        'input_size': list(img_size),
        'epochs': epochs,
        'batch_size': batch_size,
        'num_classes': num_classes,
        'classes': class_names,
        'val_loss': round(float(val_loss), 4),
        'val_accuracy': round(float(val_acc), 4),
        'history': {
            'loss': [float(x) for x in history.history['loss']],
            'accuracy': [float(x) for x in history.history['accuracy']],
            'val_loss': [float(x) for x in history.history.get('val_loss', [])],
            'val_accuracy': [float(x) for x in history.history.get('val_accuracy', [])]
        }
    }
    with open(metrics_save_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"[Saved] Disease Model: {model_save_path}")
    print(f"[Saved] Disease Classes: {classes_save_path}")
    print(f"[Saved] Disease Metrics: {metrics_save_path}")
    print("=" * 60)
    return metrics

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train Plant Disease Detection Model")
    parser.add_argument('--data_dir', type=str, default='data/datasets/plant_village_sample')
    parser.add_argument('--epochs', type=int, default=6)
    parser.add_argument('--batch_size', type=int, default=8)
    args = parser.parse_args()
    
    train_plant_disease_model(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size
    )

