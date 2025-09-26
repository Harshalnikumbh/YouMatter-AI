from flask import Blueprint, render_template, request, redirect, url_for, flash 
from extensions import db
from models import EmotionEntry
from ml_service import predictor
import logging
from flask import jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask import session
from models import User
from datetime import datetime
from mental_test_dep_service import (
    get_formatted_questions, 
    process_test_submission, 
    depression_predictor,
    anxiety_predictor,
    stress_predictor
)
from typing import List, Dict
import json

logging.basicConfig(level=logging.DEBUG)

# Define the Blueprint
routes_bp = Blueprint("routes", __name__)

# Home page
@routes_bp.route('/')
def index():
    return render_template('index.html')

# Resources page
@routes_bp.route('/resources')
def resources():
    return render_template('resources.html')

# Contact page
@routes_bp.route('/contact')
def contact():
    return render_template('contact.html')

# Mental Health Test page
@routes_bp.route('/mental_test')
def mental_test():
    return render_template('mental_test.html')

# Get questions route
@routes_bp.route("/api/get_questions", methods=["GET", "POST"])
def api_get_questions():
    try:
        data = request.get_json() or {}
        test_type = data.get("test_type", "depression")
        count = int(data.get("count", 20))
        
        logging.info(f"Getting {count} questions for {test_type} test")
        questions = get_formatted_questions(test_type, count)
        
        if not questions:
            return jsonify({"success": False, "error": "Failed to load questions"}), 500
            
        return jsonify({"success": True, "questions": questions})
    except Exception as e:
        logging.error(f"Error in /api/get_questions: {e}")
        return jsonify({"success": False, "error": "Failed to load questions"}), 500

# Submit test route - Fixed to handle category calculation properly
@routes_bp.route("/api/submit_test", methods=["POST"])
def api_submit_test():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        test_type = data.get("test_type", "depression")
        answers = data.get("answers", [])
        
        if not answers:
            return jsonify({"success": False, "error": "No answers provided"}), 400

        logging.info(f"Processing {test_type} test with {len(answers)} answers")

        # Choose predictor based on test_type
        if test_type.lower() == "depression":
            predictor = depression_predictor
        elif test_type.lower() == "anxiety":
            predictor = anxiety_predictor
        elif test_type.lower() == "stress":
            predictor = stress_predictor
        else:
            return jsonify({"success": False, "error": "Unknown test type"}), 400

        # Format answers for the predictor - fix the format issue
        formatted_answers = []
        for ans in answers:
            formatted_answers.append({
                "question_id": ans.get('question_id'),
                "response": ans.get('response')
            })

        # Calculate results using the predictor
        results = predictor.compute_score(formatted_answers)
        
        # Save responses (optional, for data collection)
        try:
            predictor.save_responses(formatted_answers)
        except Exception as save_error:
            logging.warning(f"Could not save responses: {save_error}")

        # Return results with category/severity calculated by backend
        response_data = {
            "success": True,
            "total_score": results["total_score"],
            "category": results["severity"],  # Using 'category' as expected by frontend
            "severity": results["severity"],  # Keep both for compatibility
            "max_possible_score": results["max_possible_score"],
            "total_questions": results["total_questions"],
            "percentage_positive": results["percentage_positive"],
            "description": get_category_description(test_type, results["severity"], results["total_score"])
        }
        
        logging.info(f"Test completed: {test_type} - Score: {results['total_score']}, Category: {results['severity']}")
        return jsonify(response_data)
    
    except Exception as e:
        logging.error(f"Error in /api/submit_test: {e}")
        return jsonify({"success": False, "error": "Failed to process test"}), 500

def get_category_description(test_type: str, severity: str, score: int) -> str:
    """Generate a description based on test type, severity, and score."""
    descriptions = {
        "depression": {
            "None/Minimal": f"Your score of {score} suggests minimal or no signs of depression. You appear to be managing well emotionally.",
            "Very Mild": f"Your score of {score} indicates very mild depression symptoms. Consider maintaining healthy lifestyle habits.",
            "Mild": f"Your score of {score} suggests mild depression symptoms. It may be helpful to talk to someone you trust.",
            "Moderate": f"Your score of {score} indicates moderate depression symptoms. Consider speaking with a healthcare professional.",
            "Severe": f"Your score of {score} suggests severe depression symptoms. We strongly recommend consulting with a mental health professional.",
            "Very Severe": f"Your score of {score} indicates very severe depression symptoms. Please seek immediate professional help."
        },
        "anxiety": {
            "None/Minimal": f"Your score of {score} suggests minimal or no signs of anxiety. You appear to be managing stress well.",
            "Very Mild": f"Your score of {score} indicates very mild anxiety symptoms. Practice relaxation techniques when needed.",
            "Mild": f"Your score of {score} suggests mild anxiety symptoms. Consider stress management techniques.",
            "Moderate": f"Your score of {score} indicates moderate anxiety symptoms. Professional guidance may be beneficial.",
            "Severe": f"Your score of {score} suggests severe anxiety symptoms. We recommend consulting with a healthcare professional.",
            "Very Severe": f"Your score of {score} indicates very severe anxiety symptoms. Please seek professional help promptly."
        },
        "stress": {
            "None/Minimal": f"Your score of {score} suggests you're managing stress well. Keep up the good work!",
            "Very Mild": f"Your score of {score} indicates very mild stress levels. Continue your current coping strategies.",
            "Mild": f"Your score of {score} suggests mild stress levels. Consider incorporating stress-relief activities.",
            "Moderate": f"Your score of {score} indicates moderate stress levels. It may help to identify and address stress sources.",
            "Severe": f"Your score of {score} suggests high stress levels. Consider professional stress management techniques.",
            "Very Severe": f"Your score of {score} indicates very high stress levels. Professional support is recommended."
        }
    }
    
    return descriptions.get(test_type, {}).get(severity, f"Your score of {score} has been assessed as {severity}.")

# Google Sign-In Authentication
@routes_bp.route('/auth/google', methods=['POST'])
def google_auth():
    try:
        token = request.json.get('credential')
        if not token:
            return jsonify({'success': False, 'error': 'No credential token provided'}), 400

        CLIENT_ID = "640509902254-0a4l6u5eqmsb2ql8v1af9utork069jaq.apps.googleusercontent.com"
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)

        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            # Create new user
            user = User(username=email, google_id=google_id, email=email, name=name, last_login=datetime.utcnow())
            db.session.add(user)
        else:
            # Update last login and name
            user.last_login = datetime.utcnow()
            user.name = name
        db.session.commit()

        # Store user in session
        session['user'] = {'id': user.id, 'google_id': user.google_id, 'email': user.email, 'name': user.name, 'picture': picture}
        flash("Signed in successfully!", "success")

        return jsonify({'success': True, 'message': 'Authentication successful', 'user': session['user']})

    except ValueError as e:
        return jsonify({'success': False, 'error': 'Invalid authentication token'}), 400
    except Exception as e:
        logging.error(f"Google authentication error: {e}")
        return jsonify({'success': False, 'error': 'Authentication failed. Please try again.'}), 500

# Logout route
@routes_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('routes.index'))

# Submit emotion
@routes_bp.route('/submit_emotion', methods=['POST'])
def submit_emotion():
    content = request.form.get('emotion_content', '').strip()
    min_length = 50

    # Validation check
    if not content or len(content) < min_length:
        flash(f"Please share a bit more about how you're feeling (at least {min_length} Words!)", 'error')
        return redirect(url_for('routes.index'))

    try:
        # Run ML prediction
        prediction_result = predictor.predict_mental_health(content)

        user_info = session.get('user')
        user_id = user_info['id'] if user_info else None

        entry = EmotionEntry(
            user_id=user_id,
            content=content,
            ip_address=request.remote_addr,
            prediction_label=prediction_result.get('prediction', 'Unknown'),
            prediction_confidence=prediction_result.get('confidence', 0),
            model_version="improved_v1"
        )
        db.session.add(entry)
        db.session.commit()

        label = prediction_result.get('prediction', 'Unknown')
        confidence = prediction_result.get('confidence', 0)
        compassion_message = prediction_result.get('analysis', '')
        recommendations = prediction_result.get('recommendations', [])
        resources = prediction_result.get('resources', [])

        # Render template with prediction output + recommendations
        return render_template(
            'index.html',
            user_text=content,
            prediction_label=label,
            prediction_confidence=confidence,
            compassion_message=compassion_message,
            recommendations=recommendations,
            resources=resources,                 
            show_resources=bool(resources)
        )

    except Exception as e:
        logging.error(f"Error processing emotion entry: {e}")
        flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('routes.index'))