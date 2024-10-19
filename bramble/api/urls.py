from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', fetch_user_profile),
    path('register/', CreateUserView.as_view()),
    path('post/',PostAPIView.as_view()),
    path('signup/', signup),
    path('login/', login),
]