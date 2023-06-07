from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    CompetenceSerializer, TrajectorySerializer, ExpertsSerializer,
    OrderSerializer, OrdersSerializer, ReplySerializer
)
from django.views.decorators.csrf import csrf_exempt

from .models import Competence, User, User_competence, Trajectory, Order, Reply


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer
   # renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get("user", {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "competencies" in user and user["competencies"] != "":
            self.save_competences(user["email"], user["competencies"])

        if "learning_trajectory" in user:
            self.save_trajectory(user["email"], user["learning_trajectory"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def save_trajectory(self, email, trajectory):
        user = User.objects.filter(email=email).first()
        trajectory = Trajectory.objects.filter(name=trajectory).first()
        user.learning_trajectory = trajectory
        print(user.learning_trajectory)

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
        return_data = dict(serializer.data)
        competencies = list(map(lambda x: x.competence_id.name, User_competence.objects.filter(user_id=request.user).all()))
        return_data["competencies"] = competencies

        return Response(return_data, status=status.HTTP_200_OK)

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



class ExpertsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExpertsSerializer

    def get(self, request):
        experts = User.objects.filter(role="expert").all()
        serializer = self.serializer_class(experts, many=True)

        return_data = list(serializer.data)

        for user in return_data:
            user_competencies = User_competence.objects.filter(user_id=user["id"]).all()
            competencies = list(map(lambda x: x.competence_id.name, user_competencies))
            user["competencies"] = competencies

        return Response(return_data, status=status.HTTP_200_OK)

class UserApiView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderApiView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def post(self, request):
        request_data = dict(request.data)
        request_data["student"] = request.user.id
        serialiser = self.serializer_class(data=request_data)
        serialiser.is_valid(raise_exception=True)
        serialiser.save()
        return Response(serialiser.data, status=status.HTTP_200_OK)

    def get(self, request, order_id):
        serializer_data = Order.objects.get(id=order_id)
        serializer = self.serializer_class(serializer_data)

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserOrdersApiView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrdersSerializer

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(student=user).all()
        serializer = self.serializer_class(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class OrdersApiView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrdersSerializer

    def get(self, request):
        orders_on_page = 10
        page = int(request.query_params.get("page"))-1
        orders_count = Order.objects.count()
        if orders_count > (orders_on_page * page + orders_on_page):
            orders = Order.objects.all()[page*orders_on_page:page*orders_on_page+orders_on_page]
        else:
            orders = Order.objects.all()[page*orders_on_page:]

        replies_orders = Reply.objects.filter(expert_id=request.user.id).values_list("order_id")
        if len(replies_orders) > 0:
            replies_orders = list(map(lambda x: x[0], replies_orders))
            true_orders = []

            for order in orders:
                print(order.id)
                if order.id not in replies_orders:
                    true_orders.append(order)

            print(replies_orders)
            serializer = self.serializer_class(true_orders, many=True)
        else:
            serializer = self.serializer_class(orders, many=True)

        return_data = list(serializer.data)

        for order in return_data:
            student = Order.objects.get(id=order["id"]).student
            order["student"] = {"course": student.course_number,
                                "learning_trajectory": student.learning_trajectory,
                                "student_id": student.id}

        return Response(serializer.data, status=status.HTTP_200_OK)


class ReplyApiView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReplySerializer

    def post(self, request):
        request_data = dict(request.data)
        request_data["expert"] = request.user.id
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        instance_reply = Reply.objects.get(id=pk)
        serializer = self.serializer_class(instance_reply, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if instance_reply.status == "accepted":
            replies = Reply.objects.filter(order=instance_reply.order)
            for reply in replies:
                if reply.id != instance_reply.id:
                    reply.status = "rejected"
                    print(reply.status)
                    reply.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class RepliesApiView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReplySerializer
    def get(self, request):
        order_id = request.query_params.get("order")
        if order_id != None:
            order_id = int(order_id)
            serializer_data = Reply.objects.filter(order_id=order_id)
            serializer = self.serializer_class(serializer_data, many=True)
            return_data = list(serializer.data)
            for item in return_data:
                expert = User.objects.get(id=item["expert"])
                item["expert"] = {"id": expert.id, "name": expert.name, "image": expert.image,
                                  "learning_trajectory": expert.learning_trajectory}
        else:
            raise ValidationError("Не указан order_id")

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRepliesAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReplySerializer

    def get(self, request):
        user = request.user
        serializer_data = Reply.objects.filter(expert_id=user.id)
        serializer = self.serializer_class(serializer_data, many=True)

        return_data = list(serializer.data)
        for item in return_data:
            order = Order.objects.get(id=item["order"])
            item["order"] = {"id": order.id, "name": order.name,
                             "learning_type": order.learning_type, "price": order.price,
                             "description": order.description}

        return Response(return_data, status=status.HTTP_200_OK)