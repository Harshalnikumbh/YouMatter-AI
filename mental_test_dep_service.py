import json
import logging
import os
import random
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)


class MentalTestPredictor:
    def __init__(self, test_type: str = "depression"):
        self.test_type = test_type.lower()
        self.questions_file = self.get_questions_file()
        self.questions = {}
        self.options = {}
        self.load_questions()

    def get_questions_file(self) -> str:
        if self.test_type == "depression":
            return "dep-Q.json"
        elif self.test_type == "anxiety":
            return "Anxiety-Q.json"
        elif self.test_type == "stress":
            return "stress-Q.json"
        else:
            logging.error(f"Unknown test type: {self.test_type}")
            return ""

    def load_questions(self):
        if not os.path.exists(self.questions_file):
            logging.error(f"Questions file not found: {self.questions_file}")
            return
        try:
            with open(self.questions_file, "r") as f:
                data = json.load(f)
            key_questions = f"{self.test_type}_questions"
            key_options = f"{self.test_type}_options"
            self.questions = {int(k): v for k, v in data[key_questions].items()}
            self.options = {int(k): v for k, v in data[key_options].items()}
            logging.info(f"{self.test_type.capitalize()} questions loaded successfully")
        except Exception as e:
            logging.error(f"Error loading {self.test_type} questions: {e}")

    def get_random_questions(self, count: int = 20) -> Dict[int, str]:
        if count > len(self.questions):
            logging.warning("Requested count exceeds available questions, returning all questions")
            return self.questions
        return dict(random.sample(list(self.questions.items()), count))

    def compute_score(self, answers: List[Dict]) -> Dict:
        total_score = 0
        yes_count = 0
        no_count = 0
        prefer_not_count = 0
        
        for ans in answers:
            resp = ans.get("response", 0)
            total_score += resp
            if resp == 1:
                yes_count += 1
            elif resp == 0:
                no_count += 1
            else:  # resp == -1
                prefer_not_count += 1

        max_possible_score = len(answers)
        min_possible_score = -len(answers)

        def get_severity(score, test_type):
            """Enhanced severity calculation based on test type and score."""
            if test_type in ["depression", "anxiety"]:
                # For depression and anxiety, use positive scores
                if score <= 2:
                    return "None/Minimal"
                elif score <= 5:
                    return "Very Mild"
                elif score <= 8:
                    return "Mild"
                elif score <= 12:
                    return "Moderate"
                elif score <= 15:
                    return "Severe"
                else:
                    return "Very Severe"
            else:  # stress or other tests
                if score <= 2:
                    return "None/Minimal"
                elif score <= 5:
                    return "Very Mild"
                elif score <= 8:
                    return "Mild"
                elif score <= 12:
                    return "Moderate"
                elif score <= 15:
                    return "Severe"
                else:
                    return "Very Severe"

        severity = get_severity(total_score, self.test_type)

        return {
            "total_score": total_score,
            "severity": severity,
            "category": severity,  # Add category field for frontend compatibility
            "max_possible_score": max_possible_score,
            "min_possible_score": min_possible_score,
            "total_questions": len(answers),
            "yes_count": yes_count,
            "no_count": no_count,
            "prefer_not_count": prefer_not_count,
            "percentage_positive": round((yes_count / len(answers)) * 100, 1) if answers else 0,
            "timestamp": datetime.now().isoformat(),
            "test_type": self.test_type,
        }

    def save_responses(self, answers: List[Dict], filename: str = "responses.json"):
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "test_type": self.test_type,
                "responses": answers,
                "analysis": self.compute_score(answers),
            }
            with open(filename, "a") as f:
                f.write(json.dumps(data) + "\n")
            logging.info(f"{self.test_type.capitalize()} responses saved successfully")
        except Exception as e:
            logging.error(f"Error saving responses: {e}")


# Create global instances for each test
depression_predictor = MentalTestPredictor("depression")
anxiety_predictor = MentalTestPredictor("anxiety")
stress_predictor = MentalTestPredictor("stress")


def get_formatted_questions(test_type: str = "depression", count: int = 20) -> List[Dict]:
    """Get a random subset of questions formatted with options for frontend."""
    try:
        if test_type.lower() == "depression":
            predictor = depression_predictor
        elif test_type.lower() == "anxiety":
            predictor = anxiety_predictor
        elif test_type.lower() == "stress":
            predictor = stress_predictor
        else:
            logging.error(f"Unknown test type: {test_type}")
            return []

        random_questions = predictor.get_random_questions(count)
        formatted_questions = []
        for q_id, question_text in random_questions.items():
            options = [
                {"text": "Yes", "value": 1},
                {"text": "No", "value": 0},
                {"text": "Prefer not to say", "value": -1},
            ]
            formatted_questions.append({"id": q_id, "text": question_text, "options": options})
        
        # Shuffle the questions for randomness
        random.shuffle(formatted_questions)
        return formatted_questions
    except Exception as e:
        logging.error(f"Error formatting {test_type} questions: {e}")
        return []


def process_test_submission(test_type: str, answers: List[Dict]) -> Dict:
    """Process test answers using the appropriate predictor."""
    if not answers:
        return {"success": False, "error": "No answers provided"}
    try:
        if test_type.lower() == "depression":
            predictor = depression_predictor
        elif test_type.lower() == "anxiety":
            predictor = anxiety_predictor
        elif test_type.lower() == "stress":
            predictor = stress_predictor
        else:
            return {"success": False, "error": f"Unknown test type: {test_type}"}

        # Format answers properly for compute_score method
        formatted_answers = []
        for ans in answers:
            formatted_answers.append({
                "question_id": ans.get("question_id", ans.get("id")),  # Handle both formats
                "response": ans.get("response")
            })
        
        results = predictor.compute_score(formatted_answers)
        
        try:
            predictor.save_responses(formatted_answers)
        except Exception as save_error:
            logging.error(f"Error saving responses: {save_error}")
        
        return {"success": True, **results}
    except Exception as e:
        logging.error(f"Error processing {test_type} test submission: {e}")
        return {"success": False, "error": "Failed to process test"}


def get_test_statistics(test_type: str = "depression") -> Dict:
    """Get statistics for a specific test type (optional utility function)."""
    try:
        if test_type.lower() == "depression":
            predictor = depression_predictor
        elif test_type.lower() == "anxiety":
            predictor = anxiety_predictor
        elif test_type.lower() == "stress":
            predictor = stress_predictor
        else:
            return {"error": f"Unknown test type: {test_type}"}
        
        return {
            "test_type": test_type,
            "total_questions": len(predictor.questions),
            "questions_file": predictor.questions_file,
            "loaded_successfully": bool(predictor.questions)
        }
    except Exception as e:
        logging.error(f"Error getting statistics for {test_type}: {e}")
        return {"error": "Failed to get statistics"}