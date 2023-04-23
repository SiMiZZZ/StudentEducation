from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User, Competence, Trajectory




class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    password = serializers.CharField(
        max_length=40,
        min_length=6,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "token",
            "email",
            "password",
            "name",
            "role",
            "sex",
            "image",
            "birth_date",
            "phone_number",
            "about_self",
            "learning_trajectory",
            "course_number",
            "education_stage",
        ]

    def create(self, validated_data):

        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email is None:
            raise serializers.ValidationError(
                "Ожидается Email"
            )

        if password is None:
            raise serializers.ValidationError(
                "Ожидается пароль"
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Пользователь с таким паролем не найден"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Данного пользователя не существует или он удален."
            )

        return {
            "email": user.email,
            "token": user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """ Ощуществляет сериализацию и десериализацию объектов User. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'token',)

        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """ Выполняет обновление User. """

        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class CompetenceSerializer(serializers.ModelSerializer):

    name = serializers.CharField(max_length=30)

    class Meta:
        model = Competence


class TrajectorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30)

    class Meta:
        model = Trajectory
        fields = ["name"]

