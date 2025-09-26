import joblib
import logging
import os
from typing import Dict
import random

class MentalHealthPredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_models()
    
    def load_models(self):
        """Load the pre-trained model and vectorizer"""
        try:
            model_path = 'mental_health_model.joblib'
            vectorizer_path = 'tfidf_vectorizer.joblib'
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                logging.info("ML models loaded successfully")
            else:
                logging.warning("ML model files not found, using fallback prediction")
        except Exception as e:
            logging.error(f"Error loading ML models: {e}")
            self.model = None
            self.vectorizer = None
    
    def predict_mental_health(self, text: str) -> Dict:
        """Predict mental health status from text input"""
        min_length = 200
        if not text or len(text.strip()) < min_length:
            return {
                'status': 'error',
            }
        try:
            if self.model is not None and self.vectorizer is not None:
                text_vectorized = self.vectorizer.transform([text])
                prediction = self.model.predict(text_vectorized)[0]
                
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(text_vectorized)[0]
                    confidence = max(probabilities) * 100
                else:
                    confidence = 80.0  # fallback default
                
                return self._format_prediction_result(prediction, confidence)
            else:
                return self._fallback_prediction(text)
        except Exception as e:
            logging.error(f"Error in prediction: {e}")
            return self._fallback_prediction(text)
    
    def _format_prediction_result(self, prediction, confidence: float) -> Dict:
        """Format the prediction result with actual model label and compassionate analysis"""
        label = str(prediction).strip().lower()
        
        return {
            'status': 'success',
            'prediction': label,
            'confidence': round(confidence, 2),
            'analysis': self._get_analysis_message(label),  
            'recommendations': self._get_recommendations(label),
            'resources': self._get_resources(label),
            'show_resources': bool(self._get_resources(label)),
        }
    
    def _fallback_prediction(self, text: str) -> Dict:
        """No fallback - be honest about limitations"""
        return {
            'status': 'error',
            'message': 'Model unavailable - please try again later'
        }
    
    def _get_analysis_message(self, label: str) -> str:
        """Generate a warm, compassionate message based on the predicted label"""
        if label == "suicidal ideation":
            return random.choice([
                "I'm deeply concerned about what you're going through. Please know that you matter and your life has value.",
                "Your life is precious and you are not alone. Please reach out to someone you trust or a crisis line.",
                "I'm worried about you. Please contact a mental health professional or crisis helpline immediately."
            ])
        
        elif label == "depression/sadness/loneliness/bipolar":
            return random.choice([
                "I hear the weight in your words—you are not alone. Be gentle with yourself.",
                "These feelings are valid, and it takes courage to express them.",
                "You’re going through a tough time, but support is always available."
            ])
        
        elif label == "anxiety disorders":
            return random.choice([
                "I understand anxiety can feel overwhelming. Take one breath at a time.",
                "You are not alone—grounding techniques may help you.",
                "Your courage in acknowledging anxiety shows strength."
            ])
        
        elif label == "personality/psychotic disorders":
            return random.choice([
                "Your experiences are valid. You deserve compassion and professional support.",
                "What you’re experiencing matters—support can make a big difference.",
                "Please consider connecting with a mental health professional."
            ])
        
        elif label == "positive mood":
            return random.choice([
                "Your words radiate positivity—keep nurturing these feelings.",
                "Beautiful energy! Celebrate the joy in your life.",
                "Your positive spirit shines through—keep smiling."
            ])
        
        elif label == "normal":
            return random.choice([
                "Thank you for sharing. Your emotions are valid.",
                "Opening up takes courage—be kind to yourself today.",
                "Your self-awareness is a strength. Take care of yourself."
            ])
        
        else:
            return "Thank you for sharing. If you need support, please reach out to a professional or someone you trust."


    def _get_recommendations(self, label: str) -> list:
        """Return personalized recommendations based on the label"""

        if "positive" in label:
            recs_1 = [
                "Keep nurturing your positive mindset—it’s your strength.",
                "Share your joy with others; kindness multiplies.",
                "Write down what went well today and celebrate it."
            ]
            recs_2 = [
                "Spend time in nature to refresh your mind.",
                "Express gratitude by noting 3 good things daily.",
                "Do something creative—paint, sing, or play guitar."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

        elif "normal" in label:
            recs_1 = [
                "Maintain balance by taking short mindful breaks.",
                "Stay connected with your hobbies and routines.",
                "Reflect daily on what keeps you grounded."
            ]
            recs_2 = [
                "Keep your sleep cycle consistent.",
                "Stay hydrated and eat nourishing meals.",
                "Enjoy light physical activity like walking."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

        elif "anxiety" in label:
            recs_1 = [
                "Practice deep breathing or meditation daily.",
                "Limit excessive screen or news time.",
                "Talk about your feelings with a trusted friend."
            ]
            recs_2 = [
                "Try grounding exercises—like naming 5 things around you.",
                "Stretch your body to release built-up tension.",
                "Make a calming evening routine before bed."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

        elif any(word in label for word in ["depression", "sadness", "loneliness", "bipolar"]):
            recs_1 = [
                "Consider journaling to gently release emotions.",
                "Reach out to someone you trust for connection.",
                "Engage in a small, enjoyable activity each day."
            ]
            recs_2 = [
                "Listen to uplifting or calming music.",
                "Take short walks outside to reset your mood.",
                "Remind yourself that healing is gradual, and that’s okay."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

        elif any(word in label for word in ["personality", "psychotic"]):
            recs_1 = [
                "Stay consistent with your self-care routines.",
                "Engage with support groups or therapy sessions.",
                "Remind yourself you are not alone in this journey."
            ]
            recs_2 = [
                "Keep a daily structure—it helps ground you.",
                "Practice relaxation techniques before sleep.",
                "Note small victories and give yourself credit."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

        elif "suicidal" in label:
            recs_1 = [
                "Please reach out immediately to a trusted friend or family member.",
                "Contact a crisis helpline for immediate support.",
                "You are not alone—help is available right now."
            ]
            recs_2 = [
                "Keep a list of supportive contacts nearby.",
                "Avoid being alone—stay close to someone you trust.",
                "Write down reasons to hold on when times are hard."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

        else:
            recs_1 = [
                "Consider speaking with a mental health professional.",
                "Reach out to crisis support services if needed.",
                "Connect with trusted friends, family, or support groups."
            ]
            recs_2 = [
                "Engage in light exercise or meditation.",
                "Maintain healthy eating and sleeping patterns.",
                "Stay open to new activities that bring joy."
            ]
            return [random.choice(recs_1), random.choice(recs_2)]

    def _get_resources(self, label: str) -> list:
        """Return crisis resources based on the label"""
        resources = []

        if "suicidal" in label:
            available_resources = [
                {
                    "name": "Our Side of Suicide",
                    "url": "https://www.oursideofsuicide.com/",
                },
                {   
                    "name": "Suicide Prevention - Mayo Clinic",
                    "url": "https://www.mayoclinic.org/diseases-conditions/suicide/symptoms-causes/syc-20378048",
                },
                {
                    "name": "Speaking of Suicide",
                    "url": "https://speakingofsuicide.com/",
                }   
            ]
            resources.append(random.choice(available_resources))

        elif any(word in label for word in ["personality", "psychotic"]):
            available_resources = [
                {
                    "name": "Psychotic Disorder Blog - WebMD",
                    "url": "https://www.webmd.com/schizophrenia/mental-health-psychotic-disorders",
                },
                {
                    "name": "Personality Disorder Blog - MentalHealth",
                    "url": "https://www.mentalhealth.com/library/personality-disorders",
                }
            ]
            resources.append(random.choice(available_resources))

        elif any(word in label for word in ["depression", "sadness", "loneliness", "bipolar"]):
            available_resources = [
                {
                    "name": "Postpartum Progress",
                    "url": "https://postpartumprogress.com/",
                },
                {
                    "name": "Top 10 Depression Blogs - Mind Diagnostics",
                    "url": "https://www.mind-diagnostics.org/blog/depression/10-must-read-depression-blogs",
                }
            ]
            resources.append(random.choice(available_resources))

        elif "anxiety" in label:
            available_resources = [
                {
                    "name": "The Anxiety Blog",
                    "url": "http://theanxietyblog.com/",
                },
                {
                    "name": "Choosing Therapy - Anxiety Blogs",
                    "url": "https://www.choosingtherapy.com/anxiety-blogs/",
                }
            ]
            resources.append(random.choice(available_resources))

        return resources
# Global predictor instance 
predictor = MentalHealthPredictor()
