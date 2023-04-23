from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, CompetenceSerializer, TrajectorySerializer
)
from django.views.decorators.csrf import csrf_exempt

from .models import Competence, User, User_competence, Trajectory


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get("user", {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "competencies" in user:
            self.save_competences(user["email"], user["competencies"].split(" "))


        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def save_competences(self, email, competences):
        user = User.objects.filter(email=email).first()
        for competence_name in competences:
            competence = Competence.objects.filter(name=competence_name).first()
            user_competence = User_competence(user_id=user, competence_id=competence)
            user_competence.save()

class LoginApiView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get("user", {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetenceAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = CompetenceSerializer

    def get(self, request):
        competences = Competence.objects.all()
        serializer = self.serializer_class(competences, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TrajectoryAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = TrajectorySerializer

    def get(self, request):
        trajectories = Trajectory.objects.all()
        serializer = self.serializer_class(trajectories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


