from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', fetch_user_profile,name='fetch-user-profile'),
    path('post/<int:post_id>/', PostAPIView.as_view()),
    path('post/',PostAPIView.as_view(),name='post'),
    path('feed/', FeedAPIView.as_view(),name='feed'),
    path('follow/<int:user_id>/', FollowAPIView.as_view(), name='follow-user'),
    path('search/users/', UserSearchAPIView.as_view(), name='user-search'),
    path('signup/', signup,name='signup'),
    path('login/', login,name='login'),
]