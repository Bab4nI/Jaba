import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

# Import models and serializers
from courses.models import Comment, CommentReaction
from courses.serializers import CommentSerializer
from rest_framework.renderers import JSONRenderer

# Get a comment
try:
    comment = Comment.objects.first()
    if comment:
        print(f"Found comment with ID: {comment.id}")
        print(f"Author: {comment.author.first_name} {comment.author.last_name}")
        
        # Create a context with a mock request
        class MockRequest:
            def __init__(self):
                self.user = comment.author
        
        context = {'request': MockRequest()}
        
        # Serialize the comment
        serializer = CommentSerializer(comment, context=context)
        data = serializer.data
        
        # Print the serialized data
        print("\nSerialized data:")
        for key, value in data.items():
            if key == 'author':
                print(f"author: {value}")
            elif key == 'replies':
                print(f"replies: {len(value)} items")
            elif key == 'reactions':
                print(f"reactions: {len(value)} items")
            else:
                print(f"{key}: {value}")
                
        # Test JSON rendering
        json_data = JSONRenderer().render(data)
        print("\nJSON data length:", len(json_data))
        
    else:
        print("No comments found in the database")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 