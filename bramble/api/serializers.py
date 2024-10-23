# serializers.py
from rest_framework import serializers
from .models import Post, AppUser, User,Follows

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user_id', 'text', 'timestamp', 'likes']
        read_only_fields = ['timestamp', 'user_id', 'likes']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the Django User model."""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']  # Include relevant fields
        extra_kwargs = {
            'password': {'write_only': True}  # Make the password write-only
        }

    def create(self, validated_data):
        """Create a new User instance and set the password properly."""
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

class AppUserSerializer(serializers.ModelSerializer):
    """Serializer for the AppUser model, allowing creation of both User and AppUser."""
    
    user = UserSerializer()  # Allow writable nested user creation
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = ['user', 'bio', 'followers_count', 'following_count', 'post_count']

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # Extract User data from the request
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)  # Create the User instance
        
        # Create the AppUser instance and associate it with the created User
        app_user = AppUser.objects.create(user=user, bio=validated_data.get('bio', ''))
        
        return app_user
    def get_followers_count(self, obj):
        return Follows.objects.filter(followee=obj).count()

    def get_following_count(self, obj):
        return Follows.objects.filter(follower=obj).count()

    def get_post_count(self, obj):
        return Post.objects.filter(user_id=obj).count()

