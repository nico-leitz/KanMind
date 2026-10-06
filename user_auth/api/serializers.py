from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        if data.get('email') and User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'email does already exist.'})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password', None)
        fullname = validated_data.pop('fullname')
        
        user = User.objects.create_user(
            username=fullname,
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user_obj = User.objects.filter(email=data.get('email')).first()
        
        if user_obj:
            user = authenticate(username=user_obj.username, password=data.get('password'))
            
            if user:
                data['user'] = user
                return data
                
        raise serializers.ValidationError("Invalid email or password.")