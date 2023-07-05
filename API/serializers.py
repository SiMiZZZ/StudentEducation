from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User, Competence, Trajectory, Order, Reply




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
    role = serializers.CharField(max_length=30, read_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        fields = ["email", "password", "role"]

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
            "token": user.token,
            "role": user.role,
            "id": user.id
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
        fields = fields = [
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
        fields = ["name"]


class TrajectorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30)

    class Meta:
        model = Trajectory
        fields = ["name"]

class ExpertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "sex", "learning_trajectory", "education_stage", "course_number", "about_self", "image"]


class OrderSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=200)
    id = serializers.ReadOnlyField()
    price = serializers.IntegerField()
    learning_type = serializers.CharField(max_length=100)
    class Meta:
        model = Order
        fields = ["id", "name", "description", "price", "student", "learning_type"]

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class OrdersSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=200)
    price = serializers.IntegerField()
    learning_type = serializers.CharField(max_length=10)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ["id", "name", "description", "student", "price", "learning_type"]

class ReplySerializer(serializers.ModelSerializer):
    # order = serializers.ReadOnlyField(read_only=True)
    # comment = serializers.CharField(max_length=200, write_only=True)
    # expert = serializers.ReadOnlyField()
    # status = serializers.CharField(max_length=20, write_only=True)
    class Meta:
        model = Reply
        fields = ["id", "comment", "order", "expert", "status"]


    def create(self, validated_data):
        return Reply.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
