# users/api_views.py
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import joblib
from users import api_views
import pandas as pd
import os
from .serializers import ApplicationSerializer, JobDetailSerializer, NotificationSerializer, ProfileSerializer, RegisterSerializer, PredictionInputSerializer, JobSerializer, ResumeSerializer
from .models import Job, Notification, Profile, Resume, StudentApplication

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
    @extend_schema( 
        request=PredictionInputSerializer,
        responses={200: {"example": {"probability_placed": 85.0, "status": "High Chance"}}},
        description="Submit student stats to get a placement probability prediction."
    )
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
    

# --- 4. Job Listings API (Bonus) ---
class JobListAPI(generics.ListAPIView):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'job_type']
    search_fields = ['title', 'company', 'description']
    ordering_fields = ['salary_min', 'created_at']

class JobDetailAPI(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobDetailSerializer

class ApplyJobAPI(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
class MyApplicationsAPI(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentApplication.objects.filter(student=self.request.user).order_by('-applied_date')
    

class UserProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
class ResumeUploadAPI(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Resume.objects.filter(student=self.request.user)
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class NotificationListAPI(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)

class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # Invalidate the token
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)