from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Course, Module, Lesson, LessonContent, Comment, CommentReaction, UserProgress, CustomForm
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer, 
    LessonContentSerializer, CommentSerializer, CommentReactionSerializer,
    UserProgressSerializer, CustomFormSerializer
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
from django.views.decorators.cache import cache_page, cache_control
from django.core.exceptions import ValidationError, PermissionDenied
import os
import uuid
from datetime import datetime
from django.http import Http404
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

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
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Add JSONParser
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        if not module_id:
            return Lesson.objects.none()
        return Lesson.objects.filter(module_id=module_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Разрешаем просмотр всегда, даже если is_available == False
        # if not instance.is_available:
        #     return Response({
        #         'error': 'Урок недоступен',
        #         'title': instance.title,
        #         'start_datetime': instance.start_datetime,
        #         'end_datetime': instance.end_datetime,
        #         'time_until_start': self.get_serializer(instance).get_time_until_start(instance),
        #         'time_remaining': self.get_serializer(instance).get_time_remaining(instance)
        #     }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        module_id = self.kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id)
        
        # Calculate new order
        last_order = Lesson.objects.filter(module=module).aggregate(
            models.Max('order'))['order__max'] or 0
        
        # Add module and order to request data
        data = request.data.copy()
        data['module'] = module_id
        data['order'] = last_order + 1
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Handle thumbnail deletion if empty string is passed
        if 'thumbnail' in request.data and request.data['thumbnail'] == '':
            if instance.thumbnail:
                instance.thumbnail.delete(save=False)
                instance.thumbnail = None
        
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

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
        # Блокируем отправку, если урок недоступен (например, время истекло)
        if not content.lesson.is_available:
            return Response(
                {"detail": "Время на выполнение задания истекло. Отправка ответов запрещена."},
                status=status.HTTP_403_FORBIDDEN
            )
        if content.content_type not in ['QUIZ', 'CODE']:
            return Response(
                {"detail": "This content type does not support answer submission"},
                status=status.HTTP_400_BAD_REQUEST
            )

        answer = request.data.get('answer')
        if not answer:
            return Response(
                {"detail": "Answer is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=content.lesson,
            content=content,
            defaults={
                'completed': True,
                'max_score': content.max_score,
                'current_score': 0
            }
        )

        # Calculate score based on content type
        if content.content_type == 'QUIZ':
            correct_answer = content.quiz_data.get('correct_answer')
            if answer == correct_answer:
                progress.current_score = content.max_score
            else:
                progress.current_score = 0
        elif content.content_type == 'CODE':
            # For code exercises, the score is determined by the code execution result
            # This is handled by the CodeExecutionView
            pass

        progress.completed = True
        progress.save()

        return Response({
            'content_id': content.id,
            'completed': True,
            'max_score': progress.max_score,
            'current_score': progress.current_score,
            'completed_at': progress.completed_at
        })

class CodeExecutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def validate_request(self, request_data):
        required_fields = ['source_code', 'language_id']
        for field in required_fields:
            if field not in request_data:
                raise ValidationError(f"{field} is required")
        return request_data

    def post(self, request):
        try:
            data = self.validate_request(request.data)
            source_code = data['source_code']
            language_id = data['language_id']
            stdin = data.get('stdin', '')
            content_id = data.get('content_id')

            # Если content_id указан, проверяем доступность урока
            if content_id:
                try:
                    content = LessonContent.objects.get(id=content_id)
                    if not content.lesson.is_available:
                        return Response(
                            {"detail": "Время на выполнение задания истекло. Запуск кода запрещён."},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except LessonContent.DoesNotExist:
                    pass

            # Execute the code
            result = self.execute_code(source_code, language_id, stdin)

            # If content_id is provided, update user progress
            if content_id:
                try:
                    content = LessonContent.objects.get(id=content_id)
                    progress, created = UserProgress.objects.get_or_create(
                        user=request.user,
                        lesson=content.lesson,
                        content=content,
                        defaults={
                            'completed': True,
                            'max_score': content.max_score,
                            'current_score': 0
                        }
                    )

                    # Calculate score based on execution result
                    if result.get('status', {}).get('id') == 3:  # Accepted
                        progress.current_score = content.max_score
                    else:
                        progress.current_score = 0

                    progress.completed = True
                    progress.save()

                    result['progress'] = {
                        'content_id': content.id,
                        'completed': True,
                        'max_score': progress.max_score,
                        'current_score': progress.current_score,
                        'completed_at': progress.completed_at
                    }
                except LessonContent.DoesNotExist:
                    pass

            return Response(result)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return Response(
                {"detail": "Failed to execute code"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def execute_code(self, source_code, language_id, stdin):
        headers = {
            'Content-Type': 'application/json',
            'X-RapidAPI-Key': settings.JUDGE0_API_KEY,
            'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
        }

        # Map language_id to Judge0 language ID
        language_map = {
            'javascript': 63,  # Node.js
            'python': 71,      # Python 3
            'java': 62,        # Java
            'cpp': 54,         # C++
            'csharp': 51,      # C#
            'php': 68,         # PHP
            'ruby': 72,        # Ruby
            'swift': 83,       # Swift
            'go': 60,          # Go
            'rust': 73,        # Rust
            'kotlin': 78,      # Kotlin
            'scala': 81        # Scala
        }

        # Get the correct language ID
        judge0_language_id = language_map.get(language_id.lower(), 71)  # Default to Python if language not found

        submission_data = {
            'source_code': source_code,
            'language_id': judge0_language_id,
            'stdin': stdin,
            'cpu_time_limit': 5,  # 5 seconds
            'memory_limit': 128000,  # 128MB
            'stack_limit': 128000,  # 128MB
            'max_processes_and_or_threads': 60,
            'enable_per_process_and_thread_time_limit': False,
            'enable_network': False
        }

        logger.info(f"Sending submission to Judge0: {submission_data}")
        
        try:
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
                'status': result.get('status', {}),
                'time': result.get('time', ''),
                'memory': result.get('memory', '')
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Judge0 API error: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
            raise
    
    def poll_submission_result(self, token, headers, max_attempts=10, delay=1):
        for attempt in range(max_attempts):
            time.sleep(delay)
            try:
                result_response = requests.get(
                    f'{settings.JUDGE0_API_URL}/submissions/{token}?base64_encoded=false',
                    headers=headers,
                    timeout=10
                )
                result_response.raise_for_status()
                result = result_response.json()

                if result.get('status', {}).get('id', 0) > 2:
                    return result
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling submission result: {str(e)}")
                if attempt == max_attempts - 1:
                    raise

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

    @method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True))
    def list(self, request, *args, **kwargs):
        course_slug = request.query_params.get('course_slug')
        group = request.query_params.get('group')
        
        if not course_slug or not group:
            return Response({'error': 'Missing required parameters'}, status=400)
            
        try:
            # Получаем курс с предзагрузкой модулей и уроков
            course = Course.objects.prefetch_related(
                Prefetch(
                    'modules',
                    queryset=Module.objects.prefetch_related(
                        Prefetch(
                            'lessons',
                            queryset=Lesson.objects.select_related('content_type')
                        )
                    )
                )
            ).get(slug=course_slug)
            
            # Получаем всех пользователей группы
            if group == 'admins':
                users = User.objects.filter(is_staff=True)
            else:
                users = User.objects.filter(groups__name=group)
            
            # Получаем прогресс пользователей с предзагрузкой
            progress = UserProgress.objects.filter(
                user__in=users,
                lesson__module__course=course
            ).select_related('user', 'lesson')
            
            # Формируем ответ
            response_data = {
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug
                },
                'lessons': [],
                'users': []
            }
            
            # Собираем все уроки
            for module in course.modules.all():
                for lesson in module.lessons.all():
                    response_data['lessons'].append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'type': lesson.content_type.model if lesson.content_type else 'ARTICLE',
                        'max_score': lesson.max_score or 5
                    })
            
            # Собираем данные пользователей
            for user in users:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'progress': {}
                }
                
                # Добавляем прогресс по каждому уроку
                for lesson in response_data['lessons']:
                    lesson_progress = progress.filter(user=user, lesson_id=lesson['id']).first()
                    user_data['progress'][lesson['id']] = {
                        'current_score': lesson_progress.current_score if lesson_progress else 0,
                        'max_score': lesson['max_score'],
                        'completed': lesson_progress.completed if lesson_progress else False
                    }
                
                response_data['users'].append(user_data)
            
            return Response(response_data)
            
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['GET'])
    def course_progress(self, request, course_slug=None):
        # Get course_slug from URL kwargs if not provided directly
        course_slug = course_slug or request.query_params.get('course_slug')
        if not course_slug:
            return Response(
                {"detail": "Course slug is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all lessons in the course
        lessons = Lesson.objects.filter(module__course=course)
        
        # Get progress for all lessons
        progress_data = []
        total_max_score = 0
        total_current_score = 0
        
        for lesson in lessons:
            progress = UserProgress.objects.filter(
                user=request.user,
                lesson=lesson
            ).first()
            
            if progress:
                total_max_score += progress.max_score
                total_current_score += progress.current_score
                
            progress_data.append({
                'lesson_id': lesson.id,
                'lesson_title': lesson.title,
                'completed': bool(progress and progress.completed),
                'max_score': progress.max_score if progress else 0,
                'current_score': progress.current_score if progress else 0,
                'completed_at': progress.completed_at if progress else None
            })

        return Response({
            'course_id': course.id,
            'course_title': course.title,
            'total_lessons': len(lessons),
            'completed_lessons': sum(1 for p in progress_data if p['completed']),
            'total_max_score': total_max_score,
            'total_current_score': total_current_score,
            'progress_percentage': (total_current_score / total_max_score * 100) if total_max_score > 0 else 0,
            'lessons': progress_data
        })

    @action(detail=False, methods=['GET'])
    def student_progress(self, request):
        # Get all courses the student is enrolled in
        courses = Course.objects.filter(
            modules__lessons__user_progress__user=request.user
        ).distinct()

        progress_data = []
        for course in courses:
            # Get all lessons in the course
            lessons = Lesson.objects.filter(module__course=course)
            
            # Calculate course progress
            total_max_score = 0
            total_current_score = 0
            completed_lessons = 0
            
            for lesson in lessons:
                progress = UserProgress.objects.filter(
                    user=request.user,
                    lesson=lesson
                ).first()
                
                if progress:
                    total_max_score += progress.max_score
                    total_current_score += progress.current_score
                    if progress.completed:
                        completed_lessons += 1

            progress_data.append({
                'course_id': course.id,
                'course_title': course.title,
                'total_lessons': len(lessons),
                'completed_lessons': completed_lessons,
                'total_max_score': total_max_score,
                'total_current_score': total_current_score,
                'progress_percentage': (total_current_score / total_max_score * 100) if total_max_score > 0 else 0
            })

        return Response(progress_data)

    @action(detail=False, methods=['GET'])
    def lesson_progress(self, request, lesson_id=None):
        """
        Get progress for a specific lesson
        """
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            progress = UserProgress.objects.filter(
                user=request.user,
                lesson=lesson
            ).first()

            if not progress:
                return Response({
                    'lesson_id': lesson_id,
                    'completed': False,
                    'current_score': 0,
                    'max_score': 0,
                    'completed_at': None
                })

            serializer = self.get_serializer(progress)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting lesson progress: {str(e)}")
            return Response(
                {"detail": f"Failed to get lesson progress: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['POST'])
    def mark_completed(self, request, lesson_id=None):
        # First check if lesson_id is in URL params
        lesson_id = lesson_id or request.data.get('lesson_id')
        if not lesson_id:
            return Response(
                {"detail": "Lesson ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get max_score and current_score from request data
        max_score = request.data.get('max_score', 0)
        current_score = request.data.get('current_score', 0)

        # Get or create progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={
                'completed': True,
                'max_score': max_score,
                'current_score': current_score
            }
        )

        if not created:
            progress.completed = True
            progress.max_score = max_score
            progress.current_score = current_score
            progress.save()

        return Response({
            'lesson_id': lesson.id,
            'completed': True,
            'max_score': progress.max_score,
            'current_score': progress.current_score,
            'completed_at': progress.completed_at
        })

    @action(detail=False, methods=['POST'])
    def reset_progress(self, request, lesson_id=None):
        lesson_id = lesson_id or request.data.get('lesson_id')
        if not lesson_id:
            return Response(
                {"detail": "Lesson ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete all progress for this lesson
        UserProgress.objects.filter(
            user=request.user,
            lesson=lesson
        ).delete()

        return Response({
            'lesson_id': lesson.id,
            'message': 'Progress reset successfully'
        })

    @action(detail=False, methods=['GET'])
    def groups(self, request):
        """Get list of all groups in the system"""
        User = get_user_model()
        
        # Get all unique groups from users
        groups = User.objects.exclude(groups__isnull=True).values_list('groups__name', flat=True).distinct()
        
        # Add 'admins' group if user is staff
        if request.user.is_staff:
            groups = list(groups) + ['admins']
            
        return Response(list(groups))

    @action(detail=False, methods=['GET'])
    def group_statistics(self, request):
        """Get statistics for a specific group in a course"""
        try:
            User = get_user_model()
            DEFAULT_MAX_SCORE = 5  # Default maximum score for lessons
            
            course_slug = request.query_params.get('course_slug')
            group_name = request.query_params.get('group')
            
            if not course_slug or not group_name:
                return Response(
                    {'error': 'Both course_slug and group parameters are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                course = Course.objects.get(slug=course_slug)
            except Course.DoesNotExist:
                return Response(
                    {'error': f'Course with slug {course_slug} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Get all lessons in the course
            lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
            
            # Get users in the group
            if group_name == 'admins':
                # Get users with role 'admin'
                users = User.objects.filter(role='admin')
            else:
                users = User.objects.filter(groups__name=group_name)
                
            # Prepare response data
            response_data = {
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug
                },
                'lessons': [],
                'users': []
            }
            
            # Add lessons data
            for lesson in lessons:
                response_data['lessons'].append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'type': getattr(lesson, 'type', 'ARTICLE'),
                    'max_score': DEFAULT_MAX_SCORE
                })
                
            # Add users data with their progress
            for user in users:
                try:
                    user_data = {
                        'id': user.id,
                        'full_name': (f'{user.first_name} {user.last_name}'.strip() or user.email),
                        'progress': {}
                    }
                    
                    # Get progress for each lesson
                    for lesson in lessons:
                        # Get all progress records for this lesson (both lesson-level and content-level)
                        progress_records = UserProgress.objects.filter(
                            user=user,
                            lesson=lesson
                        )
                        
                        # Calculate total scores
                        total_score = 0
                        total_max_score = 0
                        is_completed = False
                        
                        for progress in progress_records:
                            if progress.content:  # Content-level progress
                                total_score += progress.current_score or 0
                                total_max_score += progress.max_score or DEFAULT_MAX_SCORE
                            else:  # Lesson-level progress
                                total_score = max(total_score, progress.current_score or 0)
                                total_max_score = max(total_max_score, progress.max_score or DEFAULT_MAX_SCORE)
                            
                            is_completed = is_completed or progress.completed
                        
                        # If no progress records found, use default values
                        if not progress_records:
                            total_score = 0
                            total_max_score = DEFAULT_MAX_SCORE
                            is_completed = False
                        
                        user_data['progress'][str(lesson.id)] = {
                            'completed': is_completed,
                            'max_score': total_max_score,
                            'current_score': total_score
                        }
                            
                    response_data['users'].append(user_data)
                except Exception as e:
                    logger.error(f"Error processing user {user.id}: {str(e)}", exc_info=True)
                    continue  # Skip this user and continue with others
                
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error in group_statistics: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomFormViewSet(viewsets.ModelViewSet):
    serializer_class = CustomFormSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not lesson_id:
            return CustomForm.objects.none()
        return CustomForm.objects.filter(lesson_id=lesson_id).order_by('order')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                # Return empty list with proper structure
                return Response([{
                    'id': None,
                    'lesson': None,
                    'title': '',
                    'contents': [],
                    'order': 0,
                    'created_at': None,
                    'updated_at': None,
                    'total': 0
                }])
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error listing forms: {str(e)}")
            return Response([{
                'id': None,
                'lesson': None,
                'title': '',
                'contents': [],
                'order': 0,
                'created_at': None,
                'updated_at': None,
                'total': 0
            }], status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving form: {str(e)}")
            # Return empty form structure
            return Response({
                'id': None,
                'lesson': None,
                'title': '',
                'contents': [],
                'order': 0,
                'created_at': None,
                'updated_at': None,
                'total': 0
            }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        if not lesson_id:
            return Response(
                {"detail": "Lesson ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the last order number
        last_order = CustomForm.objects.filter(lesson_id=lesson_id).aggregate(
            models.Max('order'))['order__max'] or 0

        # Add lesson and order to request data
        data = request.data.copy()
        data['lesson'] = lesson_id
        data['order'] = last_order + 1

        # Ensure contents is a list
        if 'contents' in data and not isinstance(data['contents'], list):
            data['contents'] = []

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Ensure contents is a list
        data = request.data.copy()
        if 'contents' in data and not isinstance(data['contents'], list):
            data['contents'] = []

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        last_order = CustomForm.objects.filter(lesson=lesson).aggregate(
            models.Max('order'))['order__max'] or 0
        
        # Handle contents if it's a string
        data = serializer.validated_data.copy()
        if 'contents' in data and isinstance(data['contents'], str):
            try:
                data['contents'] = json.loads(data['contents'])
            except json.JSONDecodeError:
                data['contents'] = {'fields': []}
        
        serializer.save(lesson=lesson, order=last_order + 1, **data)

    def perform_destroy(self, instance):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info(f"CustomForm deleted: id={instance.id}, lesson={instance.lesson_id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting form: {str(e)}")
            return Response({
                'detail': f'Failed to delete form: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)