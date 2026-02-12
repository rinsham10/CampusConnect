from rest_framework import serializers
from .models import CustomUser, Profile, Job 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'full_name']

    def create(self, validated_data):
        # Extract full_name and split it just like your register_view
        full_name_parts = validated_data.pop('full_name').split()
        first_name = full_name_parts[0]
        last_name = " ".join(full_name_parts[1:]) if len(full_name_parts) > 1 else ""

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            role='STUDENT',
            is_active=False  # Keep the Admin Approval logic!
        )
        return user

class PredictionInputSerializer(serializers.Serializer):
    # This validates the 5 inputs required by your V2 model
    cgpa = serializers.FloatField(min_value=0.0, max_value=10.0)
    academic_performance = serializers.FloatField(min_value=0.0, max_value=10.0)
    internship_experience = serializers.ChoiceField(choices=['Yes', 'No', 'yes', 'no'])
    communication_skills = serializers.IntegerField(min_value=1, max_value=10)
    projects_completed = serializers.IntegerField(min_value=0)

