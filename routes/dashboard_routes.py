from flask import Blueprint, render_template, jsonify
from models import CropRecommendationHistory, DiseaseDetectionHistory, FarmerQuery, AdvisoryHistory
from database import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        total_crops = db.session.query(func.count(CropRecommendationHistory.id)).scalar() or 0
        total_diseases = db.session.query(func.count(DiseaseDetectionHistory.id)).scalar() or 0
        total_queries = db.session.query(func.count(FarmerQuery.id)).scalar() or 0
        total_advisories = db.session.query(func.count(AdvisoryHistory.id)).scalar() or 0

        # Recent activities (combine recent crops, diseases, advisories)
        recent_activities = []
        
        recent_crops = CropRecommendationHistory.query.order_by(
            CropRecommendationHistory.created_at.desc()
        ).limit(5).all()
        for c in recent_crops:
            recent_activities.append({
                'type': 'crop',
                'title': f"Crop Recommendation: {c.recommended_crop}",
                'subtitle': f"Soil NPK: {int(c.nitrogen)}:{int(c.phosphorus)}:{int(c.potassium)} | pH: {c.ph}",
                'timestamp': c.created_at.strftime('%Y-%m-%d %H:%M'),
                'badge': 'Crop'
            })
            
        recent_diseases = DiseaseDetectionHistory.query.order_by(
            DiseaseDetectionHistory.created_at.desc()
        ).limit(5).all()
        for d in recent_diseases:
            recent_activities.append({
                'type': 'disease',
                'title': f"Leaf Analysis: {d.detected_crop} - {d.predicted_disease}",
                'subtitle': f"Confidence: {d.confidence:.1f}%",
                'timestamp': d.created_at.strftime('%Y-%m-%d %H:%M'),
                'badge': 'Healthy' if 'healthy' in d.predicted_disease.lower() else 'Disease'
            })

        recent_advisories = AdvisoryHistory.query.order_by(
            AdvisoryHistory.created_at.desc()
        ).limit(5).all()
        for a in recent_advisories:
            recent_activities.append({
                'type': 'advisory',
                'title': f"Adaptive Advisory: {a.crop_name} ({a.growth_stage})",
                'subtitle': "Custom irrigation & fertilizer plan generated",
                'timestamp': a.created_at.strftime('%Y-%m-%d %H:%M'),
                'badge': 'Advisory'
            })

        # Sort combined activities by timestamp desc
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = recent_activities[:8]

        # Crop distribution summary for Chart.js
        crop_counts_query = db.session.query(
            CropRecommendationHistory.recommended_crop,
            func.count(CropRecommendationHistory.id)
        ).group_by(CropRecommendationHistory.recommended_crop).limit(6).all()
        
        crop_chart_labels = [row[0] for row in crop_counts_query]
        crop_chart_data = [row[1] for row in crop_counts_query]

        # Disease breakdown for Chart.js
        healthy_count = DiseaseDetectionHistory.query.filter(
            DiseaseDetectionHistory.predicted_disease.ilike('%healthy%')
        ).count()
        infected_count = total_diseases - healthy_count

        return jsonify({
            'status': 'success',
            'stats': {
                'total_crop_recommendations': total_crops,
                'total_disease_analyses': total_diseases,
                'total_farmer_queries': total_queries,
                'total_advisories': total_advisories
            },
            'recent_activities': recent_activities,
            'charts': {
                'crop_distribution': {
                    'labels': crop_chart_labels,
                    'data': crop_chart_data
                },
                'disease_breakdown': {
                    'labels': ['Healthy Leaves', 'Diseased Leaves'],
                    'data': [healthy_count, infected_count]
                }
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Failed to retrieve dashboard statistics: {str(e)}"
        }), 500

