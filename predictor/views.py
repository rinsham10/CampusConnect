import os
import joblib
from django.conf import settings
from django.shortcuts import render

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
