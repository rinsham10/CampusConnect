import os
import joblib
import pandas as pd
from django.conf import settings
from django.shortcuts import redirect, render

def predict_view(request):
    result = None

    if request.method == 'POST':
        try:
            ssc_p = float(request.POST['ssc_p'])
            hsc_p = float(request.POST['hsc_p'])
            degree_p = float(request.POST['degree_p'])

            # Convert "Yes"/"No" to 1/0
            workex_input = request.POST['workex'].strip().lower()
            if workex_input == 'yes':
                workex = 1
            elif workex_input == 'no':
                workex = 0
            else:
                raise ValueError("Work experience must be 'Yes' or 'No'.")

            etest_p = float(request.POST['etest_p'])
            mba_p = float(request.POST['mba_p'])

            features = [[ssc_p, hsc_p, degree_p, workex, etest_p, mba_p]]

            model_path = os.path.join(settings.BASE_DIR, 'svm_model.pkl')
            model = joblib.load(model_path)
            prediction = model.predict(features)[0]
            result = "Placed ✅" if prediction == 1 else "Not Placed ❌"

        except Exception as e:
            result = f"Error: {e}"

    return render(request, 'predictor/predictor.html', {'result': result})

# The NEW V2 Predictor Logic - ADD THIS SECTION
# ------------------------------------------------------------------

MODEL_V2_PATH = os.path.join(settings.BASE_DIR, 'placement_model_v2.pkl')
try:
    MODEL_V2 = joblib.load(MODEL_V2_PATH)
except FileNotFoundError:
    raise RuntimeError(f"Model file not found at {MODEL_V2_PATH}. Please run the training script.")


def predict_v2_view(request):
    """
    Handles the enhanced placement predictor with the Post/Redirect/Get pattern
    and detailed, multi-tiered recommendations.
    """
    # This handles the initial page load and the load after a redirect
    if request.method == 'GET':
        context = request.session.pop('prediction_context', {}) # Use a default empty dict
        return render(request, 'predictor/predictor_v2.html', context)

    # This handles the form submission
    if request.method == 'POST':
        # We will build the context here and save it to the session
        context_to_save = {
            'prediction': None,
            'recommendations': [],
            'error_message': None
        }
        try:
            # --- 1. Get and Validate Inputs ---
            cgpa = float(request.POST['cgpa'])
            academic_performance = int(request.POST['academic_performance'])
            internship_experience = request.POST['internship_experience']
            communication_skills = int(request.POST['communication_skills'])
            projects_completed = int(request.POST['projects_completed'])

            if not (0.0 <= cgpa <= 10.0):
                raise ValueError("CGPA must be between 0.0 and 10.0.")
            if not (1 <= academic_performance <= 10):
                raise ValueError("Academic Performance must be between 1 and 10.")
            if not (1 <= communication_skills <= 10):
                raise ValueError("Communication Skills must be between 1 and 10.")
            if projects_completed < 0:
                raise ValueError("Number of projects cannot be negative.")

            # --- 2. Preprocess and Predict ---
            internship_encoded = 1 if internship_experience.lower() == 'yes' else 0
            input_data = pd.DataFrame({
                'CGPA': [cgpa],
                'Academic_Performance': [academic_performance],
                'Internship_Experience': [internship_encoded],
                'Communication_Skills': [communication_skills],
                'Projects_Completed': [projects_completed]
            })
            probabilities = MODEL_V2.predict_proba(input_data)[0]
            prob_placed = probabilities[1]
            prob_not_placed = probabilities[0]

            # --- 3. Generate Prediction String ---
            if prob_placed >= 0.5:
                context_to_save['prediction'] = f"You have a {prob_placed:.0%} chance of getting placed."
            else:
                context_to_save['prediction'] = f"You have a {prob_not_placed:.0%} chance of not getting placed."

            # --- 4. FULL RECOMMENDATION LOGIC ---
            recommendations = []
            
            # Tier 1: Critical advice for profiles with low placement probability
            if prob_placed < 0.60:
                if cgpa < 7.0:
                    recommendations.append("Focus on raising your CGPA. This is a critical first step as many companies have a strict academic cutoff.")
                if internship_encoded == 0:
                    recommendations.append("Actively seek an internship. Practical experience is one of the most important factors for recruiters.")
                if projects_completed == 0:
                    recommendations.append("Start building a portfolio by completing at least one or two significant projects in your field of interest.")
                if communication_skills < 6:
                    recommendations.append("Work on your communication skills. Join a public speaking club or take a course to build confidence.")

            # Tier 2: Advice for profiles that are good but could be great
            if 0.50 <= prob_placed < 0.85:
                if academic_performance < 8:
                    recommendations.append("While your CGPA is good, elevating your overall academic performance can help you stand out from other qualified candidates.")
                if projects_completed <= 2:
                    recommendations.append("Expand your portfolio with a diverse range of projects, perhaps collaborating with a team to showcase teamwork skills.")
                if communication_skills < 8:
                    recommendations.append("Refine your communication. Practice mock interviews to improve how you articulate your technical skills and experiences.")
                if internship_encoded == 1 and projects_completed < 2:
                    recommendations.append("Leverage your internship experience by creating a detailed project report or presentation based on your work. This powerfully connects theory with practice.")

            # Tier 3: Advice for strong profiles aiming for top-tier companies
            if prob_placed >= 0.75:
                recommendations.append("Your profile is strong! To aim for top-tier companies, consider getting a professional certification in a high-demand area (e.g., Cloud Computing, Data Science, AI/ML).")
                recommendations.append("Start networking strategically. Connect with alumni and professionals from your dream companies on LinkedIn and attend industry-specific webinars.")
                recommendations.append("Create a 'master resume' and tailor it for each specific job application, highlighting the projects and skills that perfectly match the job description.")

            context_to_save['recommendations'] = recommendations

        except Exception as e:
            # Save any error message to be displayed
            context_to_save['error_message'] = f"An error occurred: {e}"

        # --- 5. Save results to session and redirect ---
        request.session['prediction_context'] = context_to_save
        return redirect('predict_v2') # This name comes from your urls.py