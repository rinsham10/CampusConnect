# users/api_views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
import joblib
import pandas as pd
import os
from .serializers import RegisterSerializer, PredictionInputSerializer

class RegisterAPI(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Account created. Awaiting admin approval."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 2. Login API ---
class LoginAPI(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if not user.is_active:
                return Response({"error": "Account pending approval."}, status=status.HTTP_401_UNAUTHORIZED)
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'role': user.role
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# --- 3. Prediction API (The Upgrade) ---
class PredictAPI(APIView):
    def post(self, request):
        serializer = PredictionInputSerializer(data=request.data)
        if serializer.is_valid():
            # Extract data
            d = serializer.validated_data
            internship_encoded = 1 if d['internship_experience'].lower() == 'yes' else 0
            
            # Prepare for model
            input_df = pd.DataFrame({
                'CGPA': [d['cgpa']],
                'Academic_Performance': [d['academic_performance']],
                'Internship_Experience': [internship_encoded],
                'Communication_Skills': [d['communication_skills']],
                'Projects_Completed': [d['projects_completed']]
            })

            # Load Model and Predict
            model_path = os.path.join(settings.BASE_DIR, 'placement_model_v2.pkl')
            model = joblib.load(model_path)
            
            probabilities = model.predict_proba(input_df)[0]
            prob_placed = probabilities[1]

            return Response({
                "probability_placed": round(prob_placed * 100, 2),
                "status": "High Chance" if prob_placed >= 0.5 else "Low Chance",
                "message": f"You have a {prob_placed:.0%} chance of placement."
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)