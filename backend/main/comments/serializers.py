from rest_framework import serializers
from .models import Comment, CommentReaction
from courses.models import Course, Lesson
from rest_framework.exceptions import ValidationError
import logging
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

logger = logging.getLogger(__name__)



class CommentReactionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CommentReaction
        fields = ["id", "user", "reaction_type", "created_at"]

    def get_user(self, obj):
        avatar_url = None
        if hasattr(obj.user, "avatar_base64") and obj.user.avatar_base64:
            avatar_url = obj.user.avatar_base64

        return {
            "id": obj.user.id,
            "username": f"{obj.user.first_name} {obj.user.last_name}",
            "avatar": avatar_url,
        }


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reactions = CommentReactionSerializer(many=True, read_only=True)
    current_user_reaction = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    reply_to_author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "lesson",
            "author",
            "parent",
            "text",
            "comment_type",
            "created_at",
            "updated_at",
            "is_edited",
            "replies",
            "reactions",
            "likes_count",
            "dislikes_count",
            "current_user_reaction",
            "is_author",
            "reply_to_author",
        ]
        read_only_fields = ["author", "created_at", "updated_at", "is_edited"]

    def get_author(self, obj):
        avatar_url = None
        if hasattr(obj.author, "avatar_base64") and obj.author.avatar_base64:
            avatar_url = obj.author.avatar_base64

        return {
            "id": obj.author.id,
            "username": f"{obj.author.first_name} {obj.author.last_name}",
            "avatar": avatar_url,
        }

    def get_reply_to_author(self, obj):
        """
        Get information about the author of the parent comment if this is a reply
        """
        if obj.parent and obj.parent.author:
            parent_author = obj.parent.author
            avatar_url = None
            if hasattr(parent_author, "avatar_base64") and parent_author.avatar_base64:
                avatar_url = parent_author.avatar_base64

            return {
                "id": parent_author.id,
                "username": f"{parent_author.first_name} {parent_author.last_name}",
                "avatar": avatar_url,
            }
        return None

    def get_replies(self, obj):
        """
        Get direct replies to this comment, sorted by creation date
        """
        if hasattr(obj, "replies"):
            # Get direct replies only
            direct_replies = obj.replies.all().order_by("-created_at")

            # Use a separate serializer for replies to avoid infinite recursion
            serializer_context = {"request": self.context.get("request")}
            return CommentSerializer(
                direct_replies, many=True, context=serializer_context
            ).data
        return []

    def get_current_user_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None

    def get_is_author(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

    def get_likes_count(self, obj):
        return obj.reactions.filter(reaction_type="LIKE").count()

    def get_dislikes_count(self, obj):
        return obj.reactions.filter(reaction_type="DISLIKE").count()

    def validate(self, data):
        # Validate comment_type
        comment_type = data.get("comment_type", "COMMENT")
        if comment_type not in dict(Comment.COMMENT_TYPES):
            raise ValidationError(
                {
                    "comment_type": f"Invalid comment type. Choices are: {dict(Comment.COMMENT_TYPES).keys()}"
                }
            )
        return data

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)