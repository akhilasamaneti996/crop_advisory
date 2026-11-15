import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

def train_crop_recommendation_model(
    data_path='data/datasets/Crop_recommendation.csv',
    model_save_path='ml_models/crop_model.pkl',
    encoder_save_path='ml_models/crop_label_encoder.pkl',
    metrics_save_path='ml_models/crop_model_metrics.json'
):
    print("=" * 60)
    print("TRAINING CROP RECOMMENDATION MODEL (RANDOM FOREST)")
    print("=" * 60)
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Crop dataset not found at {data_path}")
        
    print(f"[1/6] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"      Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    print("[2/6] Inspecting and handling missing values...")
    missing_vals = df.isnull().sum().to_dict()
    total_missing = sum(missing_vals.values())
    print(f"      Total missing values: {total_missing}")
    if total_missing > 0:
        df = df.dropna()
        print(f"      Dropped missing rows. New shape: {df.shape}")
        
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    target_col = 'label'
    
    print(f"[3/6] Separating features {features} and target '{target_col}'")
    X = df[features]
    y = df[target_col]
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    classes = list(label_encoder.classes_)
    print(f"      Number of unique crops ({len(classes)}): {classes}")
    
    print("[4/6] Splitting data into 80% train and 20% test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )
    print(f"      Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    
    print("[5/6] Training Random Forest Classifier (100 estimators)...")
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X_train, y_train)
    
    print("[6/6] Evaluating model performance...")
    y_pred = rf_classifier.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    precision_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    recall_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print("\n--- MODEL EVALUATION RESULTS ---")
    print(f"Accuracy:           {accuracy * 100:.2f}%")
    print(f"Precision (Macro):  {precision_macro * 100:.2f}%")
    print(f"Precision (Weight): {precision_weighted * 100:.2f}%")
    print(f"Recall (Macro):     {recall_macro * 100:.2f}%")
    print(f"Recall (Weight):    {recall_weighted * 100:.2f}%")
    print(f"F1-Score (Macro):   {f1_macro * 100:.2f}%")
    print(f"F1-Score (Weight):  {f1_weighted * 100:.2f}%")
    
    report_dict = classification_report(y_test, y_pred, target_names=classes, output_dict=True, zero_division=0)
    
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(rf_classifier, model_save_path)
    joblib.dump(label_encoder, encoder_save_path)
    
    metrics = {
        'model_name': 'Random Forest Classifier',
        'n_estimators': 100,
        'features': features,
        'crops_count': len(classes),
        'crops': classes,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'accuracy': round(float(accuracy), 4),
        'precision_macro': round(float(precision_macro), 4),
        'precision_weighted': round(float(precision_weighted), 4),
        'recall_macro': round(float(recall_macro), 4),
        'recall_weighted': round(float(recall_weighted), 4),
        'f1_macro': round(float(f1_macro), 4),
        'f1_weighted': round(float(f1_weighted), 4),
        'classification_report': report_dict
    }
    
    with open(metrics_save_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"\n[Saved] Model: {model_save_path}")
    print(f"[Saved] Label Encoder: {encoder_save_path}")
    print(f"[Saved] Metrics: {metrics_save_path}")
    print("=" * 60)
    return metrics

if __name__ == '__main__':
    train_crop_recommendation_model()

