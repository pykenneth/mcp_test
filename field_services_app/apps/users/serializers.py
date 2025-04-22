from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    
    Provides serialization for user details, with password write-only
    and proper handling for user creation and updates.
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'date_joined', 'is_active', 'is_staff', 'is_superuser',
            'role', 'profile_picture', 'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

    def validate(self, data):
        """
        Validate that passwords match when creating a new user.
        """
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
            data.pop('confirm_password')
        return data

    def create(self, validated_data):
        """
        Create and return a new user with encrypted password.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data.pop('password'),
            **{k: v for k, v in validated_data.items() if k != 'password'}
        )
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing user, setting the password correctly.
        """
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
