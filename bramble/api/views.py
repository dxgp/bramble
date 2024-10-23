from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import AppUser,Post,Follows
from .serializers import AppUserSerializer,PostSerializer
from rest_framework.generics import CreateAPIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.db.models import Q

# Create your views here.
@api_view(['GET'])
def fetch_user_profile(request):
    if request.method == 'GET':
        appuser = AppUser.objects.get(user=request.user)
        serializer = AppUserSerializer(appuser)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if request.method == 'POST':
        serializer = AppUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = AppUser.objects.get(user__username=request.data['user']['username'])
            token = Token.objects.create(user=user.user)
            user.user.set_password(request.data['user']['password'])
            user.user.save()
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        app_user = get_object_or_404(AppUser, user__username=request.data['username'])
        if not app_user.user.check_password(request.data['password']):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        token,created = Token.objects.get_or_create(user=app_user.user)
        serializer = AppUserSerializer(app_user)
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)
    

class FeedAPIView(APIView):
    def get(self, request):
        app_user = AppUser.objects.get(user=request.user)
        following = Follows.objects.filter(follower=app_user).values_list('followee', flat=True)
        posts = Post.objects.filter(user_id__in=following).order_by('-timestamp')
        post_list = [
            {
                'user': post.user_id.user.username,
                'text': post.text,
                'timestamp': post.timestamp,
                'likes': post.likes,
            }
            for post in posts
        ]
        return Response(post_list)
    
class PostAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        app_user = AppUser.objects.get(user=request.user)
        text = request.data.get('text', '')
        if not text:
            return Response({'error': 'Text field cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
        post = Post.objects.create(user_id=app_user, text=text, likes=0)
        return Response({
            'message': 'Post created successfully.',
            'post': {
                'id': post.id,
                'text': post.text,
                'timestamp': post.timestamp,
                'likes': post.likes
            }
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        app_user = AppUser.objects.get(user=request.user)
        post = get_object_or_404(Post, id=post_id, user_id=app_user)
        post.delete()
        return Response({'message': 'Post deleted successfully.'}, status=status.HTTP_200_OK)

    def patch(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.likes += 1
        post.save()
        return Response({
            'message': 'Post liked successfully.',
            'likes': post.likes
        }, status=status.HTTP_200_OK)

class FollowAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        """Follow a user."""
        follower = AppUser.objects.get(user=request.user)
        followee = get_object_or_404(AppUser, id=user_id)

        if Follows.objects.filter(follower=follower, followee=followee).exists():
            return Response({'message': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        Follows.objects.create(follower=follower, followee=followee)
        return Response({'message': f'You are now following {followee.user.username}'}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Unfollow a user."""
        follower = AppUser.objects.get(user=request.user)
        followee = get_object_or_404(AppUser, id=user_id)

        follow_relationship = Follows.objects.filter(follower=follower, followee=followee)

        if not follow_relationship.exists():
            return Response({'message': 'You are not following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        follow_relationship.delete()
        return Response({'message': f'You have unfollowed {followee.user.username}'}, status=status.HTTP_200_OK)

class UserSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Allow only authenticated users to search

    def get(self, request):
        # Get the search query parameter from the request
        query = request.query_params.get('q', '')

        if not query:
            return Response({'message': 'Search query is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Search for users by username, email, or bio (which is in AppUser)
        users = AppUser.objects.filter(
            Q(user__username__icontains=query) | 
            Q(user__email__icontains=query) | 
            Q(bio__icontains=query)
        )

        # Serialize the results using the AppUserSerializer
        serializer = AppUserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

