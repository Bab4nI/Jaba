from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import (
    Lesson,
    Comment,
    CommentReaction,
)
from .serializers import (

    CommentSerializer,
    CommentReactionSerializer,
)
from django.shortcuts import get_object_or_404

import logging
from rest_framework.decorators import action
from django.core.exceptions import ValidationError, PermissionDenied

logger = logging.getLogger(__name__)

# Create your views here.
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check if we're accessing via the lesson route or direct route
        lesson_id = self.kwargs.get("lesson_id")

        # If we have a specific comment ID but no lesson ID, we're using direct access
        if "pk" in self.kwargs and not lesson_id:
            # For direct access to a comment, don't filter by user
            # This allows users to see any comment by ID
            return Comment.objects.all()

        # Otherwise, filter by lesson ID if provided
        if not lesson_id:
            return Comment.objects.none()

        try:
            lesson_id = int(lesson_id)
            return (
                Comment.objects.filter(lesson_id=lesson_id, parent=None)
                .select_related("author")
                .prefetch_related("replies", "reactions")
            )
        except (ValueError, TypeError):
            logger.error(f"Invalid lesson_id: {lesson_id}")
            return Comment.objects.none()

    def perform_create(self, serializer):
        lesson_id = self.kwargs.get("lesson_id")
        if not lesson_id:
            raise ValidationError("lesson_id is required")

        try:
            lesson_id = int(lesson_id)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid lesson_id: {lesson_id}")

        # Check if lesson exists
        get_object_or_404(Lesson, id=lesson_id)

        parent_id = self.request.data.get("parent")

        # Handle parent comment
        if parent_id:
            try:
                parent_id = int(parent_id)
                parent = get_object_or_404(Comment, id=parent_id)
                if parent.lesson_id != lesson_id:
                    raise ValidationError(
                        "Parent comment must belong to the same lesson"
                    )
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid parent_id: {parent_id}")

        serializer.save(author=self.request.user, lesson_id=lesson_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        # Check if the user is the author of the comment or an admin
        if instance.author != self.request.user and not self.request.user.is_staff:
            logger.warning(
                f"User {self.request.user.id} attempted to edit comment {instance.id} by {instance.author.id}"
            )
            raise PermissionDenied("You can only edit your own comments.")
        serializer.save(is_edited=True, lesson=instance.lesson)

    def perform_destroy(self, instance):
        # Check if the user is the author of the comment or an admin
        if instance.author != self.request.user and not self.request.user.is_staff:
            logger.warning(
                f"User {self.request.user.id} attempted to delete comment {instance.id} by {instance.author.id}"
            )
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()

    @action(detail=False, methods=["GET"])
    def lesson_comments(self, request):
        lesson_id = request.query_params.get("lesson_id")
        if not lesson_id:
            raise ValidationError("lesson_id is required")

        try:
            lesson_id = int(lesson_id)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid lesson_id: {lesson_id}")

        comment_type = request.query_params.get("type", "COMMENT")

        # Check if lesson exists
        get_object_or_404(Lesson, id=lesson_id)

        comments = Comment.objects.filter(
            lesson_id=lesson_id, parent=None, comment_type=comment_type
        )
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class CommentReactionViewSet(viewsets.ModelViewSet):
    serializer_class = CommentReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        comment_id = self.kwargs.get("comment_id")
        if comment_id:
            return CommentReaction.objects.filter(comment_id=comment_id).select_related(
                "user"
            )
        return CommentReaction.objects.none()

    def perform_create(self, serializer):
        comment_id = self.kwargs.get("comment_id")
        if not comment_id:
            raise ValidationError("comment_id is required")

        # Remove existing reaction if any
        CommentReaction.objects.filter(
            comment_id=comment_id, user=self.request.user
        ).delete()

        # Save the new reaction
        reaction = serializer.save(comment_id=comment_id, user=self.request.user)

        # Update likes count
        reaction.comment.update_likes_count()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only remove your own reactions.")

        # Store the comment before deleting the reaction
        comment = instance.comment

        # Delete the reaction
        instance.delete()

        # Update likes count
        comment.update_likes_count()

    @action(detail=False, methods=["DELETE"])
    def delete_user_reaction(self, request, comment_id=None):
        """
        Delete a reaction by user and comment ID.
        This is a custom endpoint to delete a reaction without knowing its specific ID.
        """
        if not comment_id:
            return Response(
                {"error": "comment_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get the comment
        comment = get_object_or_404(Comment, id=comment_id)

        # Find and delete the user's reaction
        reaction = CommentReaction.objects.filter(
            comment_id=comment_id, user=request.user
        ).first()

        if reaction:
            # Store the comment before deleting
            comment = reaction.comment

            # Delete the reaction
            reaction.delete()

            # Update likes count
            comment.update_likes_count()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "No reaction found"}, status=status.HTTP_404_NOT_FOUND
            )