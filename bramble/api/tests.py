from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import AppUser, User, Post, Follows
from rest_framework.authtoken.models import Token

class SignupLoginAPITest(APITestCase):
    def test_signup_user(self):
        # Test user signup
        url = reverse('signup')  # Replace with your actual signup URL name
        signup_data = {
            'user': {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'testpassword'
            },
            'bio': 'This is a test bio.'
        }
        response = self.client.post(url, signup_data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertIn('token', response.data)

    def test_login_user(self):
        # Create a user to test login
        user = User.objects.create_user(username='testuser', password='testpassword')
        AppUser.objects.create(user=user, bio='Test bio')

        url = reverse('login')  # Replace with your actual login URL name
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['bio'], 'Test bio')

    def test_login_invalid_credentials(self):
        # Test login with invalid credentials
        user = User.objects.create_user(username='testuser', password='testpassword')
        AppUser.objects.create(user=user, bio='Test bio')

        url = reverse('login')  # Replace with your actual login URL name
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class FetchUserProfileAPITest(APITestCase):
    def setUp(self):
        # Create a user and AppUser for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.app_user = AppUser.objects.create(user=self.user, bio='Test bio')
        self.token = Token.objects.create(user=self.user)

    def test_fetch_user_profile(self):
        # Test fetching user profile
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('fetch-user-profile')  # Replace with your actual fetch user profile URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Test bio')


class FeedAPITest(APITestCase):
    def setUp(self):
        # Create a user and some posts for testing
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        self.app_user1 = AppUser.objects.create(user=self.user1, bio='User 1 bio')
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.app_user2 = AppUser.objects.create(user=self.user2, bio='User 2 bio')

        # Create follow relationship
        Follows.objects.create(follower=self.app_user1, followee=self.app_user2)

        # Create posts for the user being followed
        self.post = Post.objects.create(user_id=self.app_user2, text='Post by testuser2', likes=5)

    def test_fetch_feed(self):
        # Test fetching feed for a user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('feed')  # Replace with your actual feed API URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Post by testuser2')


class PostAPITest(APITestCase):
    def setUp(self):
        # Create a user and token for authenticated requests
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.app_user = AppUser.objects.create(user=self.user, bio='Test bio')
        self.token = Token.objects.create(user=self.user)

        # Create a post for testing
        self.post = Post.objects.create(user_id=self.app_user, text='Test Post', likes=10)

    def test_create_post(self):
        # Test creating a post
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = '/post/'  # URL path for creating and deleting posts
        post_data = {
            'text': 'New post text.'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['post']['text'], 'New post text.')

    def test_delete_post(self):
        # Test deleting a post by sending a DELETE request to the same URL
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = f'/post/{self.post.id}/'  # URL path for deleting posts with post_id in the URL
        # Send a DELETE request, passing the post ID in the request body
        response = self.client.delete(url, {'post_id': self.post.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

class PostLikeAPITest(APITestCase):
    def setUp(self):
        # Create a user and token for authenticated requests
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.app_user = AppUser.objects.create(user=self.user, bio='Test bio')
        self.token = Token.objects.create(user=self.user)

        # Create a post for testing
        self.post = Post.objects.create(user_id=self.app_user, text='Test Post', likes=0)

    def test_like_post(self):
        # Test liking a post
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = f'/post/{self.post.id}/'
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, 1)

class FollowAPITest(APITestCase):
    def setUp(self):
        # Create two users: one for following and one to be followed
        self.user1 = User.objects.create_user(username='follower', password='testpassword1')
        self.app_user1 = AppUser.objects.create(user=self.user1, bio='Follower bio')
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username='followee', password='testpassword2')
        self.app_user2 = AppUser.objects.create(user=self.user2, bio='Followee bio')
        self.token2 = Token.objects.create(user=self.user2)

        # Create posts for user2 (followee) to check post count
        Post.objects.create(user_id=self.app_user2, text="First post by followee", likes=10)
        Post.objects.create(user_id=self.app_user2, text="Second post by followee", likes=5)

    def test_follow_user(self):
        # Test following a user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('follow-user', kwargs={'user_id': self.app_user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follows.objects.filter(follower=self.app_user1, followee=self.app_user2).exists())

    def test_unfollow_user(self):
        # Test unfollowing a user
        Follows.objects.create(follower=self.app_user1, followee=self.app_user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('follow-user', kwargs={'user_id': self.app_user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Follows.objects.filter(follower=self.app_user1, followee=self.app_user2).exists())

    def test_follow_user_already_following(self):
        # Test following a user who is already followed
        Follows.objects.create(follower=self.app_user1, followee=self.app_user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('follow-user', kwargs={'user_id': self.app_user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are already following this user.')

    def test_unfollow_user_not_following(self):
        # Test unfollowing a user who is not being followed
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('follow-user', kwargs={'user_id': self.app_user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are not following this user.')

    def test_fetch_user_profile(self):
        """Test fetching a user's profile with follower, following, and post counts"""
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        # User1 follows User2
        Follows.objects.create(follower=self.app_user1, followee=self.app_user2)
        Follows.objects.create(follower=self.app_user2, followee=self.app_user1)

        # Fetch user2's profile
        url = reverse('fetch-user-profile')  # Assuming this is the endpoint for fetching the profile
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the profile data
        self.assertEqual(response.data['user']['username'], 'follower')
        self.assertEqual(response.data['bio'], "Follower bio")

        # Verify the counts
        self.assertEqual(response.data['followers_count'], 1)  # One follower (User2)
        self.assertEqual(response.data['following_count'], 1)  # Following one user (User2)
        self.assertEqual(response.data['post_count'], 0)  # No posts by User1

    def test_fetch_followee_profile_with_counts(self):
        """Test fetching the followee's profile and verify post, follower, and following counts"""
        # Authenticate user1 (follower)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)

        # User1 follows User2
        Follows.objects.create(follower=self.app_user1, followee=self.app_user2)
        url = reverse('fetch-user-profile')  # Assuming this is the endpoint for fetching the profile
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the profile data
        self.assertEqual(response.data['user']['username'], 'followee')
        self.assertEqual(response.data['bio'], "Followee bio")

        # Verify the counts
        self.assertEqual(response.data['followers_count'], 1)  # One follower (User1)
        self.assertEqual(response.data['following_count'], 0)  # Followee isn't following anyone
        self.assertEqual(response.data['post_count'], 2)  # Followee has 2 posts

class UserSearchAPITest(APITestCase):
    def setUp(self):
        # Create some users for the test
        self.user1 = User.objects.create_user(username='john_doe', email='john@example.com', first_name='John', last_name='Doe', password='testpassword')
        self.app_user1 = AppUser.objects.create(user=self.user1, bio='Just a regular John.')

        self.user2 = User.objects.create_user(username='johnny', email='johnny@example.com', first_name='Johnny', last_name='Smith', password='testpassword')
        self.app_user2 = AppUser.objects.create(user=self.user2, bio="Johnny's bio")
        self.token = Token.objects.create(user=self.user1)

    def test_search_user(self):
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Perform a search for "john"
        url = reverse('user-search') + '?q=john'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two users match the query "john"
        self.assertEqual(response.data[0]['user']['username'], 'john_doe')
        self.assertEqual(response.data[1]['user']['username'], 'johnny')

    def test_search_empty_query(self):
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Perform a search with an empty query
        url = reverse('user-search') + '?q='
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Search query is required.')
