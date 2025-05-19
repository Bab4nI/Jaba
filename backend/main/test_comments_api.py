import os
import django
import sys
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

# Import necessary modules
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Comment, CommentReaction
from courses.serializers import CommentSerializer
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

def test_comments_api():
    print("Starting Comments API Test")
    
    # Check if we have users in the database
    users = User.objects.all()
    if not users.exists():
        print("No users found in the database. Creating a test user...")
        user = User.objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )
    else:
        user = users.first()
        print(f"Using existing user: {user.first_name} {user.last_name} ({user.email})")
    
    # Check if we have courses and lessons
    lessons = Lesson.objects.all()
    if not lessons.exists():
        print("No lessons found in the database. Please create a course and lesson first.")
        return
    
    lesson = lessons.first()
    print(f"Using lesson: {lesson.title} (ID: {lesson.id})")
    
    # Create a test client
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Test GET comments
    url = f"/api/courses/{lesson.module.course.slug}/modules/{lesson.module.id}/lessons/{lesson.id}/comments/"
    print(f"Testing GET request to {url}")
    response = client.get(url)
    print(f"GET Response status: {response.status_code}")
    if response.status_code == 200:
        comments = response.json()
        print(f"Found {len(comments)} comments")
    
    # Test POST comment
    print(f"\nTesting POST request to {url}")
    data = {
        "text": "This is a test comment",
        "comment_type": "COMMENT",
        "lesson": lesson.id
    }
    response = client.post(url, data, format='json')
    print(f"POST Response status: {response.status_code}")
    if response.status_code == 201:
        comment = response.json()
        print(f"Created comment with ID: {comment['id']}")
        comment_id = comment['id']
        
        # Test PUT (update) comment
        update_url = f"{url}{comment_id}/"
        print(f"\nTesting PATCH request to {update_url}")
        update_data = {
            "text": "This is an updated test comment"
        }
        response = client.patch(update_url, update_data, format='json')
        print(f"PATCH Response status: {response.status_code}")
        if response.status_code == 200:
            updated_comment = response.json()
            print(f"Updated comment text: {updated_comment['text']}")
            print(f"Is edited flag: {updated_comment['is_edited']}")
        else:
            print(f"PATCH Error: {response.content}")
        
        # Test DELETE comment
        print(f"\nTesting DELETE request to {update_url}")
        response = client.delete(update_url)
        print(f"DELETE Response status: {response.status_code}")
    else:
        print(f"POST Error: {response.content}")

if __name__ == "__main__":
    # Make sure SECRET_KEY is set
    from django.conf import settings
    if not settings.SECRET_KEY:
        print("ERROR: SECRET_KEY is not set in Django settings!")
        # Set a temporary key for testing
        from django.core.management.utils import get_random_secret_key
        settings.SECRET_KEY = get_random_secret_key()
        print("Set temporary SECRET_KEY for testing")
    
    test_comments_api() 