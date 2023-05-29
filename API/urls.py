from django.contrib import admin
from django.urls import path, include

from .views import RegistrationAPIView, LoginApiView, UserRetrieveUpdateAPIView,\
    CompetenceAPIView, TrajectoryAPIView, ExpertsAPIView,\
    UserApiView, OrderApiView, UserOrdersApiView, OrdersApiView, ReplyApiView, RepliesApiView, UserRepliesAPIView

urlpatterns = [
    path("auth/registration", RegistrationAPIView.as_view()), # POST
    path("auth/login", LoginApiView.as_view()), # POST
    path("user", UserRetrieveUpdateAPIView.as_view()), # GET, PATCH
    path("user/<int:user_id>", UserApiView.as_view()), #GET
    path("competencies", CompetenceAPIView.as_view()), # GET
    path("trajectories", TrajectoryAPIView.as_view()), # GET
    path("experts", ExpertsAPIView.as_view()),# GET
    path("order", OrderApiView.as_view()), # POST
    path("order/<int:order_id>", OrderApiView.as_view()), # GET
    path("user/orders", UserOrdersApiView.as_view()),
    path("orders", OrdersApiView.as_view()),
    path("reply", ReplyApiView.as_view()),
    path("replies", RepliesApiView.as_view()),
    path("user/replies", UserRepliesAPIView.as_view())
]