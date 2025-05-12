from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Course, Module, Lesson, LessonContent, Comment, CommentReaction, UserProgress
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer, 
    LessonContentSerializer, CommentSerializer, CommentReactionSerializer,
    UserProgressSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  # Add JSONParser
from django.db import transaction
import json
import logging
import time
from rest_framework.views import APIView
from django.conf import settings
import requests
from django.core.cache import cache
import openai
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ValidationError, PermissionDenied
import os
import uuid
from datetime import datetime
from django.http import Http404
from django.db import models

logger = logging.getLogger(__name__)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('author').prefetch_related('modules')
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Add JSONParser for flexibility

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Override create method to add better error handling
        """
        try:
            logger.info(f"Creating course with data: {request.data}")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            return Response(
                {"detail": f"Failed to create course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    def get_object(self):
        """
        Override to handle case-insensitive slug lookup and improve error handling
        for Cyrillic characters in slugs
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get the slug from the URL
        slug = self.kwargs.get(self.lookup_field)
        if not slug:
            raise Http404("No slug provided")
            
        # Try to find the course using our custom method
        obj = Course.find_by_slug(slug)
        if not obj:
            logger.warning(f"Course with slug '{slug}' not found")
            raise Http404(f"No course found with slug: {slug}")
            
        # Check permissions
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            # Handle thumbnail deletion if empty string is passed
            if 'thumbnail' in request.data and request.data['thumbnail'] in ['', None]:
                if instance.thumbnail:
                    instance.thumbnail.delete(save=False)
                    instance.thumbnail = None

            self.perform_update(serializer)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Course not found with slug: {kwargs.get('slug')}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            return Response(
                {"detail": f"Failed to update course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"Deleting course: {instance.title} (slug: {instance.slug})")
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"detail": f"Course not found with slug: {kwargs.get('slug')}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting course: {str(e)}")
            return Response(
                {"detail": f"Failed to delete course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Module.objects.filter(
            course__slug=self.kwargs['course_slug']
        ).select_related('course').prefetch_related('lessons').order_by('order')
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        last_order = Module.objects.filter(course=course).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 1
        serializer.save(course=course, order=new_order)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    parser_classes = [MultiPartParser, FormParser]  # Unchanged, as it handles file uploads
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self): 
        return Lesson.objects.filter(
            module__id=self.kwargs['module_id']
        ).select_related('module').prefetch_related('contents').order_by('order')
    
    def perform_create(self, serializer):
        module = get_object_or_404(Module, id=self.kwargs['module_id'])
        last_order = Lesson.objects.filter(module=module).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 1
        serializer.save(module=module, order=new_order)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Handle thumbnail deletion if empty string is passed
        if 'thumbnail' in request.data and request.data['thumbnail'] == '':
            instance.thumbnail.delete(save=False)
        
        self.perform_update(serializer)
        return Response(serializer.data)

class LessonContentViewSet(viewsets.ModelViewSet):
    serializer_class = LessonContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Add JSONParser
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        logger.debug(f"Fetching contents for lesson_id: {lesson_id}")
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            logger.debug(f"Lesson found: {lesson.title}")
        except Lesson.DoesNotExist as e:
            logger.warning(f"Lesson not found for lesson_id: {lesson_id}")
            raise ValidationError(f"Lesson with id {lesson_id} does not exist") from e
            
        return LessonContent.objects.filter(lesson__id=lesson_id).order_by('order')
    
    def perform_create(self, serializer):
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
        last_order = LessonContent.objects.filter(lesson=lesson).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 1
        serializer.save(lesson=lesson, order=new_order)
    
    def perform_update(self, serializer):
        instance = self.get_object()
        content_type = serializer.validated_data.get('content_type')

        # Handle file deletion when updating
        if content_type == 'IMAGE' and 'image' in serializer.validated_data:
            if instance.image:
                instance.image.delete(save=False)
        elif content_type == 'FILE' and 'file' in serializer.validated_data:
            if instance.file:
                instance.file.delete(save=False)

        serializer.save()
    
    @action(detail=False, methods=['patch'], url_path='order')
    @transaction.atomic
    def update_order(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
        order_data = request.data.get('order', [])
        
        if not isinstance(order_data, list):
            return Response(
                {'error': 'Order data must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                for item in order_data:
                    if not isinstance(item, dict) or 'id' not in item or 'order' not in item:
                        raise ValidationError('Each item must contain "id" and "order" fields')
                    
                    content = LessonContent.objects.get(
                        id=item['id'],
                        lesson=lesson
                    )
                    content.order = item['order']
                    content.save()
            
            return Response({'status': 'order updated'}, status=status.HTTP_200_OK)
            
        except LessonContent.DoesNotExist as e:
            logger.error(f"Content not found: {str(e)}")
            return Response(
                {'error': 'Invalid content ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def submit_answer(self, request, pk=None):
        content = self.get_object()
        
        if content.content_type not in ['CODE', 'QUIZ']:
            return Response(
                {"error": "This content type doesn't support answer submission"},
                status=status.HTTP_400_BAD_REQUEST
            )

        answer = request.data.get('answer')
        if answer is None:
            return Response(
                {"error": "Answer is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate score based on content type
        score = 0
        if content.content_type == 'CODE':
            # For code exercises, you might want to run tests
            # This is a simplified scoring - you should implement proper test running
            score = content.max_score if answer.strip() else 0
        elif content.content_type == 'QUIZ':
            # For quizzes, check against correct answers
            correct_answer = content.correct_answer  # You'll need to add this field
            score = content.max_score if answer == correct_answer else 0

        # Update user progress
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=content.lesson,
            content=content,
            defaults={'completed': True, 'score': score}
        )
        
        if not progress.completed:
            progress.completed = True
            progress.score = score
            progress.save()

        return Response({
            'score': score,
            'max_score': content.max_score,
            'completed': True
        })

class CodeExecutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def validate_request(self, request_data):
        required_fields = ['source_code', 'language_id']
        missing_fields = [field for field in required_fields if field not in request_data]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
        if len(request_data['source_code']) > 100_000:
            raise ValidationError('Source code is too large (max 100 KB)')
            
        language_id = request_data['language_id']
        if language_id not in settings.JUDGE0_LANGUAGE_IDS:
            raise ValidationError(f'Unsupported language: {language_id}')
            
        interpreter = request_data.get('interpreter', 'default')
        judge0_language_id = settings.JUDGE0_LANGUAGE_IDS[language_id].get(
            interpreter, 
            settings.JUDGE0_LANGUAGE_IDS[language_id].get('default')
        )
        
        if not judge0_language_id:
            raise ValidationError(
                f'Unsupported interpreter: {interpreter} for language: {language_id}'
            )
            
        return judge0_language_id
    
    def post(self, request):
        try:
            judge0_language_id = self.validate_request(request.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        source_code = request.data['source_code']
        stdin = request.data.get('stdin', '')
        cache_key = f"code_execution:{hash(source_code + str(judge0_language_id) + stdin)}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for {cache_key}")
            return Response(cached_result, status=status.HTTP_200_OK)
            
        try:
            result = self.execute_code(
                source_code=source_code,
                language_id=judge0_language_id,
                stdin=stdin
            )
            cache.set(cache_key, result, timeout=3600)
            return Response(result, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            logger.error(f"Judge0 API error: {str(e)}")
            return Response(
                {'error': 'Failed to execute code'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def execute_code(self, source_code, language_id, stdin):
        headers = {
            'Content-Type': 'application/json',
        }
        if hasattr(settings, 'JUDGE0_API_KEY') and settings.JUDGE0_API_KEY:
            headers.update({
                'x-rapidapi-key': settings.JUDGE0_API_KEY,
                'x-rapidapi-host': 'judge0-ce.p.rapidapi.com'
            })

        submission_data = {
            'source_code': source_code,
            'language_id': language_id,
            'stdin': stdin,
        }

        logger.info(f"Sending submission to Judge0: {submission_data}")
        response = requests.post(
            f'{settings.JUDGE0_API_URL}/submissions?base64_encoded=false&wait=false',
            json=submission_data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Judge0 submission response: {response.status_code} {response.text}")

        token = response.json().get('token')
        if not token:
            raise requests.RequestException("No token received from Judge0")

        result = self.poll_submission_result(token, headers)
        return {
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'compile_output': result.get('compile_output', ''),
            'status': result.get('status', {}).get('description', 'Unknown'),
            'time': result.get('time', ''),
            'memory': result.get('memory', '')
        }
    
    def poll_submission_result(self, token, headers, max_attempts=10, delay=1):
        for attempt in range(max_attempts):
            time.sleep(delay)
            result_response = requests.get(
                f'{settings.JUDGE0_API_URL}/submissions/{token}?base64_encoded=false',
                headers=headers,
                timeout=10
            )
            result_response.raise_for_status()
            result = result_response.json()

            if result.get('status', {}).get('id', 0) > 2:
                return result

        raise requests.RequestException("Submission timeout")

class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def validate_request(self, request_data):
        if not request_data.get('prompt'):
            raise ValidationError('Prompt is required')
        return request_data['prompt'], request_data.get('selected_text', '')
    
    def post(self, request):
        try:
            prompt, selected_text = self.validate_request(request.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            response = self.get_ai_response(prompt, selected_text)
            return Response({
                'response': response
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"AI API error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to process AI request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_ai_response(self, prompt, selected_text):
        client = openai.OpenAI(
            base_url='https://api.deepseek.com',
            api_key=settings.DEEPSEEK_API_KEY,
        )
        
        full_prompt = f"{prompt}: \"{selected_text}\"" if selected_text else prompt
        
        chat_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Ты помощник для студентов. Отвечай кратко и понятно."},
                {"role": "user", "content": full_prompt}
            ],
            model="deepseek-chat",
            timeout=10
        )
        
        return chat_response.choices[0].message.content

class MediaUploadView(APIView):
    """
    API view for handling direct media uploads.
    This endpoint allows users to upload images and files directly to the server's media directory.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Handle file upload and save it to the media directory.
        Supported file types: image, file
        """
        if 'image' not in request.FILES and 'file' not in request.FILES:
            return Response({
                'error': 'No files found. Please upload an image or file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file_type = None
        file_obj = None
        
        # Check if it's an image upload
        if 'image' in request.FILES:
            file_type = 'image'
            file_obj = request.FILES['image']
            # Verify it's an image
            if not file_obj.content_type.startswith('image/'):
                return Response({
                    'error': 'Uploaded file is not an image.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if it's a file upload
        elif 'file' in request.FILES:
            file_type = 'file'
            file_obj = request.FILES['file']
        
        # Generate unique filename
        ext = os.path.splitext(file_obj.name)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Create year/month based folder structure
        today = datetime.now()
        folder_path = os.path.join(file_type, str(today.year), str(today.month))
        full_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)
        
        # Ensure the directory exists
        os.makedirs(full_folder_path, exist_ok=True)
        
        # Full path for the file
        file_path = os.path.join(full_folder_path, unique_filename)
        
        # Save the file
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        
        # Path as it would be accessed from client via media URL
        media_path = os.path.join(folder_path, unique_filename).replace('\\', '/')
        
        return Response({
            'success': True,
            'file_type': file_type,
            'file_name': file_obj.name,
            'file_path': f"/media/{media_path}",
            'image_path': f"/media/{media_path}" if file_type == 'image' else None
        }, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check if we're accessing via the lesson route or direct route
        lesson_id = self.kwargs.get('lesson_id')
        
        # If we have a specific comment ID but no lesson ID, we're using direct access
        if 'pk' in self.kwargs and not lesson_id:
            # For direct access to a comment, don't filter by user
            # This allows users to see any comment by ID
            return Comment.objects.all()
        
        # Otherwise, filter by lesson ID if provided
        if not lesson_id:
            return Comment.objects.none()
        
        try:
            lesson_id = int(lesson_id)
            return Comment.objects.filter(
                lesson_id=lesson_id,
                parent=None
            ).select_related('author').prefetch_related('replies', 'reactions')
        except (ValueError, TypeError):
            logger.error(f"Invalid lesson_id: {lesson_id}")
            return Comment.objects.none()

    def perform_create(self, serializer):
        lesson_id = self.kwargs.get('lesson_id')
        if not lesson_id:
            raise ValidationError("lesson_id is required")
        
        try:
            lesson_id = int(lesson_id)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid lesson_id: {lesson_id}")
        
        # Check if lesson exists
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        parent_id = self.request.data.get('parent')
        
        # Handle parent comment
        if parent_id:
            try:
                parent_id = int(parent_id)
                parent = get_object_or_404(Comment, id=parent_id)
                if parent.lesson_id != lesson_id:
                    raise ValidationError("Parent comment must belong to the same lesson")
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid parent_id: {parent_id}")
        
        serializer.save(
            author=self.request.user,
            lesson_id=lesson_id
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        # Check if the user is the author of the comment or an admin
        if instance.author != self.request.user and not self.request.user.is_staff:
            logger.warning(f"User {self.request.user.id} attempted to edit comment {instance.id} by {instance.author.id}")
            raise PermissionDenied("You can only edit your own comments.")
        serializer.save(is_edited=True, lesson=instance.lesson)

    def perform_destroy(self, instance):
        # Check if the user is the author of the comment or an admin
        if instance.author != self.request.user and not self.request.user.is_staff:
            logger.warning(f"User {self.request.user.id} attempted to delete comment {instance.id} by {instance.author.id}")
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()

    @action(detail=False, methods=['GET'])
    def lesson_comments(self, request):
        lesson_id = request.query_params.get('lesson_id')
        if not lesson_id:
            raise ValidationError("lesson_id is required")
        
        try:
            lesson_id = int(lesson_id)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid lesson_id: {lesson_id}")
        
        comment_type = request.query_params.get('type', 'COMMENT')
        
        # Check if lesson exists
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        comments = Comment.objects.filter(
            lesson_id=lesson_id,
            parent=None,
            comment_type=comment_type
        )
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

class CommentReactionViewSet(viewsets.ModelViewSet):
    serializer_class = CommentReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        comment_id = self.kwargs.get('comment_id')
        if comment_id:
            return CommentReaction.objects.filter(
                comment_id=comment_id
            ).select_related('user')
        return CommentReaction.objects.none()

    def perform_create(self, serializer):
        comment_id = self.kwargs.get('comment_id')
        if not comment_id:
            raise ValidationError("comment_id is required")

        # Remove existing reaction if any
        CommentReaction.objects.filter(
            comment_id=comment_id,
            user=self.request.user
        ).delete()

        # Save the new reaction
        reaction = serializer.save(
            comment_id=comment_id,
            user=self.request.user
        )
        
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
        
    @action(detail=False, methods=['DELETE'])
    def delete_user_reaction(self, request, comment_id=None):
        """
        Delete a reaction by user and comment ID.
        This is a custom endpoint to delete a reaction without knowing its specific ID.
        """
        if not comment_id:
            return Response(
                {"error": "comment_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get the comment
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Find and delete the user's reaction
        reaction = CommentReaction.objects.filter(
            comment_id=comment_id,
            user=request.user
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
                {"error": "No reaction found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def course_progress(self, request, course_slug=None):
        # Get course_slug from URL kwargs if not provided directly
        if not course_slug:
            course_slug = request.query_params.get('course_slug')
            
        if not course_slug:
            return Response(
                {"error": "course_slug is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, slug=course_slug)
        
        # Get all lessons in the course
        lessons = Lesson.objects.filter(module__course=course)
        
        # Get user's progress for this course
        progress = UserProgress.objects.filter(
            user=request.user,
            lesson__module__course=course
        )

        # Calculate statistics
        total_lessons = lessons.count()
        completed_lessons = progress.filter(completed=True).values('lesson').distinct().count()
        total_score = progress.aggregate(total=models.Sum('score'))['total'] or 0
        max_possible_score = LessonContent.objects.filter(
            lesson__module__course=course
        ).aggregate(total=models.Sum('max_score'))['total'] or 0

        return Response({
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'total_score': total_score,
            'max_possible_score': max_possible_score,
            'score_percentage': (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        })
        
    @action(detail=False, methods=['GET'])
    def student_progress(self, request):
        """
        Get detailed progress for a specific student across all work items.
        Query params:
        - student_id: ID of the student (required for admins, ignored for students)
        - course_slug: Filter by course (optional)
        """
        # Check if the requesting user is an admin and can view other students' progress
        user_id = request.user.id
        if request.user.role == 'admin' and request.query_params.get('student_id'):
            user_id = request.query_params.get('student_id')
            
        # Filter by course if provided
        course_filter = {}
        if course_slug := request.query_params.get('course_slug'):
            course_filter['lesson__module__course__slug'] = course_slug
            
        # Get all progress records for this user
        progress = UserProgress.objects.filter(
            user_id=user_id, 
            **course_filter
        ).select_related('lesson', 'content')
        
        # Group by lesson for easier consumption by the frontend
        result = {}
        for p in progress:
            lesson_id = p.lesson_id
            content_id = p.content_id if p.content else None
            
            if lesson_id not in result:
                result[lesson_id] = {
                    'lesson_id': lesson_id,
                    'lesson_title': p.lesson.title,
                    'completed': p.completed,
                    'contents': {}
                }
                
            if content_id:
                result[lesson_id]['contents'][content_id] = {
                    'content_id': content_id,
                    'completed': p.completed,
                    'score': p.score,
                    'max_score': p.content.max_score if p.content else 0,
                    'content_type': p.content.content_type if p.content else None,
                    'completed_at': p.completed_at
                }
                
        return Response(result)

    @action(detail=False, methods=['POST'])
    def mark_completed(self, request, lesson_id=None):
        # First check if lesson_id is in URL params
        if lesson_id is None:
            # If not in URL params, try to get from request data
            lesson_id = request.data.get('lesson_id')
            
        if not lesson_id:
            return Response(
                {"error": "lesson_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        content_id = request.data.get('content_id')
        score = request.data.get('score', 1)  # Default score is 1 for non-quiz/code content

        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # If content_id is provided, mark specific content as completed
        if content_id:
            content = get_object_or_404(LessonContent, id=content_id)
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                content=content,
                defaults={'completed': True, 'score': min(score, content.max_score)}
            )
            if not created:
                progress.completed = True
                progress.score = min(score, content.max_score)
                progress.save()
        else:
            # Mark the entire lesson as completed
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={'completed': True, 'score': 1}
            )
            if not created:
                progress.completed = True
                progress.save()

        return Response({'status': 'success'})