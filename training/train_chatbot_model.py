import os
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

def train_chatbot_intent_model(
    intents_json_path='data/datasets/chatbot_intents.json',
    model_save_path='ml_models/chatbot_model.pkl',
    metrics_save_path='ml_models/chatbot_metrics.json'
):
    print("=" * 60)
    print("TRAINING CHATBOT INTENT CLASSIFICATION MODEL (TF-IDF + LOGISTIC REGRESSION)")
    print("=" * 60)
    
    if not os.path.exists(intents_json_path):
        raise FileNotFoundError(f"Chatbot intents file not found at: {intents_json_path}")
        
    print(f"[1/4] Loading intents dataset from: {intents_json_path}")
    with open(intents_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    X_samples = []
    y_labels = []
    intents_map = {}
    
    for intent in data.get('intents', []):
        tag = intent['tag']
        patterns = intent.get('patterns', [])
        responses = intent.get('responses', {})
        intents_map[tag] = responses
        
        for pattern in patterns:
            cleaned = pattern.strip().lower()
            if cleaned:
                X_samples.append(cleaned)
                y_labels.append(tag)
                
    print(f"      Total patterns: {len(X_samples)} across {len(intents_map)} intent tags.")
    
    print("[2/4] Constructing TF-IDF Vectorizer and Logistic Regression Pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), min_df=1, sublinear_tf=True)),
        ('clf', LogisticRegression(C=2.0, max_iter=300, random_state=42))
    ])
    
    print("[3/4] Evaluating with 3-Fold Cross Validation...")
    cv_scores = cross_val_score(pipeline, X_samples, y_labels, cv=3)
    mean_cv = cv_scores.mean()
    print(f"      Cross-Validation Accuracy: {mean_cv * 100:.2f}% (Scores: {[round(s, 3) for s in cv_scores]})")
    
    print("[4/4] Fitting final pipeline on all documented sample questions...")
    pipeline.fit(X_samples, y_labels)
    
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    bundle = {
        'pipeline': pipeline,
        'intents_map': intents_map,
        'tags': list(intents_map.keys())
    }
    joblib.dump(bundle, model_save_path)
    
    metrics = {
        'model_name': 'TF-IDF + Logistic Regression Intent Classifier',
        'total_training_patterns': len(X_samples),
        'intent_tags': list(intents_map.keys()),
        'cv_accuracy': round(float(mean_cv), 4),
        'languages_supported': ['en', 'te', 'hi']
    }
    with open(metrics_save_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"[Saved] Chatbot Model: {model_save_path}")
    print(f"[Saved] Chatbot Metrics: {metrics_save_path}")
    print("=" * 60)
    return metrics

if __name__ == '__main__':
    train_chatbot_intent_model()
