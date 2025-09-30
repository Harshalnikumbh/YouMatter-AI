YouMatter AI – Full Web Application

YouMatter AI is a complete web application that helps users understand their mental health through text analysis. It combines a user-friendly frontend, a backend API, and a Logistic Regression-based ML model to predict emotional states and provide actionable insights.

🔹 Features

User Input & Text Analysis

Users submit text describing their feelings or experiences.

Text is processed and analyzed in real-time.

Mental Health Prediction

Uses a Logistic Regression ML model with TF-IDF features.

Trained on over 600,000 labeled text entries.

Achieves 79% accuracy in predicting mental health labels such as depression, anxiety, stress, or neutral state.

Actionable Recommendations

Based on predictions, users receive suggestions like meditation, breathing exercises, or grounding techniques.

Interactive Web Interface

Friendly UI for input and displaying results.

Responsive design for desktop and mobile use.

🔹 How It Works

Input

Users enter text describing their emotions or mental state.

Processing

Text is preprocessed (cleaned, lowercased, tokenized).

TF-IDF (Term Frequency–Inverse Document Frequency) converts text into numerical features suitable for ML.

Prediction

Logistic Regression model evaluates TF-IDF features.

Produces a mental health label with 79% accuracy.

Output

Returns classification results (e.g., depression, anxiety, stress, neutral).

Provides recommendations to improve mental well-being.

🔹 Tech Stack

Frontend: HTML / CSS / JavaScript

Backend: Python Flask 

Machine Learning: Logistic Regression (scikit-learn)

Text Feature Extraction: TF-IDF (scikit-learn)

Deployment: Render (frontend and backend)

Text Processing: NLTK / Custom preprocessing

🔹 Architecture

Frontend

Provides a form for users to submit mental health text.

Dynamically displays prediction results.

Backend

Receives user text from the frontend.

Processes text and sends it to the ML model.

Returns prediction results and recommendations.

ML Model

Logistic Regression model trained on 600,000+ entries.

Features extracted using TF-IDF from user text are fed into the model for prediction.

🔹 Usage

Open the web app in your browser.

Enter your text describing your emotions.

Click Submit.

See your mental health prediction along with suggested actions.

🔹 License

This project is open-source under the MIT License.
