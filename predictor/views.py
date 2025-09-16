import os
import joblib
import pandas as pd
from django.conf import settings
from django.shortcuts import redirect, render

def predict_old_view(request):
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

    return render(request, 'predictor/predictor_old.html', {'result': result})

# The NEW V2 Predictor Logic - ADD THIS SECTION
# ------------------------------------------------------------------

MODEL_V2_PATH = os.path.join(settings.BASE_DIR, 'placement_model_v2.pkl')
try:
    MODEL_V2 = joblib.load(MODEL_V2_PATH)
except FileNotFoundError:
    raise RuntimeError(f"Model file not found at {MODEL_V2_PATH}. Please run the training script.")


def predict_view(request):
    """
    Handles the enhanced placement predictor with the Post/Redirect/Get pattern
    and detailed, multi-tiered recommendations.
    """
    # This handles the initial page load and the load after a redirect
    if request.method == 'GET':
        context = request.session.pop('prediction_context', {}) # Use a default empty dict
        return render(request, 'predictor/predictor.html', context)

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

            # --- 4. NEW COMPREHENSIVE RECOMMENDATION LOGIC ---
            critical_advice = []
            improvement_advice = []
            next_level_advice = []

            # Analyze each feature independently
            if cgpa < 7.0:
                critical_advice.append("Raise your CGPA above 7.0. This is a critical first step as many companies have a strict academic cutoff.")
            elif cgpa < 8.5:
                improvement_advice.append("Your CGPA is good, but pushing it above 8.5 can open doors to more top-tier companies.")

            if internship_encoded == 0:
                critical_advice.append("Gain internship experience. Practical industry experience is a massive advantage and often a mandatory requirement.")
            
            if projects_completed < 2:
                critical_advice.append("Build a project portfolio. Aim for at least 2 significant projects to demonstrate your practical skills to recruiters.")
            elif projects_completed < 4:
                improvement_advice.append("Expand your portfolio with a more complex or team-based project to showcase collaboration and advanced skills.")

            if communication_skills < 7:
                critical_advice.append("Improve communication skills. This is crucial for interviews. Join a public speaking club or practice mock interviews.")
            elif communication_skills < 9:
                improvement_advice.append("You communicate well. To excel, focus on storytelling—clearly articulating the 'what, how, and why' of your projects.")

            if academic_performance < 7:
                improvement_advice.append("Boost your academic performance score by actively participating in class and consistently preparing for assessments.")

            # Now, assemble the final recommendations based on priority
            final_recommendations = []
            if prob_placed < 0.50:
                # If the chance is low, critical advice comes first
                final_recommendations.extend(critical_advice)
                final_recommendations.extend(improvement_advice)
            else:
                # If the chance is decent, improvement advice is more relevant
                final_recommendations.extend(improvement_advice)
                final_recommendations.extend(critical_advice) # Still show critical advice if any applies

            # Add next-level advice for strong candidates
            if prob_placed >= 0.75:
                next_level_advice.append("Aim Higher: Your profile is strong! To target the best companies, consider these advanced steps:")
                next_level_advice.append("Pursue a professional certification in a high-demand field.")
                next_level_advice.append("Engage in strategic networking by connecting with alumni on LinkedIn.")
                next_level_advice.append("Tailor your resume for each specific job application to match their requirements perfectly.")
                final_recommendations.extend(next_level_advice)

            # The final fallback: ensure no one leaves empty-handed
            if not final_recommendations:
                final_recommendations.append("Your profile is well-balanced and strong! Your main focus should now be on thorough interview preparation and researching specific companies.")

            context_to_save['recommendations'] = final_recommendations

        except Exception as e:
         context_to_save['error_message'] = f"An error occurred: {e}"
        request.session['prediction_context'] = context_to_save
        return redirect('predict')