from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class LoginSerializer(TokenObtainPairSerializer):

    username_field = "login"

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        try:
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email__iexact=login)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Invalid username/email or password."
                )

        if not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid username/email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled."
            )

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }