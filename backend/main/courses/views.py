from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from registration.models import User
from .models import Course, Module, Lesson, LessonContent, UserCourseProgress
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, LessonContentSerializer, UserCourseProgressSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  # Add JSONParser
from django.db import transaction
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
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count, Q, Case, When, IntegerField, Max, F
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import LessonCompletion

logger = logging.getLogger(__name__)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('author').prefetch_related('modules')
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser]  # Unchanged, as it handles file uploads

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
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
    






class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserCourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCourseProgress.objects.filter(
            user=self.request.user
        ).select_related('course', 'last_lesson').prefetch_related(
            'completed_lessons__lesson__module'
        ).annotate(
            total_lessons_count=Count('course__modules__lessons', distinct=True),
            completed_lessons_count=Count(
                'completed_lessons',
                filter=Q(completed_lessons__is_completed=True),
                distinct=True
            )
        )

    @action(detail=True, methods=['post'], url_path='complete-lesson')
    def complete_lesson(self, request, pk=None):
        """Отметить урок как завершенный"""
        progress = self.get_object()
        lesson_id = request.data.get('lesson_id')
        score = request.data.get('score', 0)

        if not lesson_id:
            return Response(
                {'error': 'lesson_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        completion, created = LessonCompletion.objects.update_or_create(
            progress=progress,
            lesson=lesson,
            defaults={
                'is_completed': True,
                'score': score,
                'last_accessed': timezone.now(),
                'completed_at': timezone.now()
            }
        )
        
        progress.last_lesson = lesson
        progress.last_accessed = timezone.now()
        progress.save()
        
        return Response({
            'status': 'success',
            'progress_id': progress.id,
            'lesson_id': lesson.id,
            'completed_at': completion.completed_at
        })

    @action(detail=True, methods=['post'], url_path='track-access')
    def track_access(self, request, pk=None):
        """Обновить время последнего доступа к уроку"""
        progress = self.get_object()
        lesson_id = request.data.get('lesson_id')
        score = request.data.get('score') 
        
        if not lesson_id:
            return Response(
                {'error': 'lesson_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        lesson = get_object_or_404(Lesson, id=lesson_id)
        LessonCompletion.objects.update_or_create(
            progress=progress,
            lesson=lesson,
            defaults={
                'is_completed': True,
                'score': score,
                'last_accessed': timezone.now(),
                'completed_at': timezone.now()
            }
        )
        
        progress.last_accessed = timezone.now()
        progress.last_lesson = lesson
        progress.save()
        
        return Response({'status': 'access updated'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получить статистику по всем курсам текущего пользователя"""
        stats = self._get_user_stats(request.user)
        return Response(stats)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def admin_stats(self, request):
        """Статистика по всем пользователям (только для админа)"""
        user_stats = []
        for user in User.objects.all():
            stats = self._get_user_stats(user)
            user_stats.append({
                'user_id': user.id,
                'email': user.email,  # Используем email вместо username
                'first_name': user.first_name,
                'last_name': user.last_name,
                **stats
            })
        
        total_stats = UserCourseProgress.objects.aggregate(
            total_courses=Count('id'),
            completed_courses=Count(
                Case(
                    When(is_completed=True, then=1),
                    output_field=IntegerField()
                )
            )
        )
        
        return Response({
            'users': user_stats,
            'total_stats': {
                **total_stats,
                'completion_rate': round(
                    total_stats['completed_courses'] / total_stats['total_courses'] * 100, 2
                ) if total_stats['total_courses'] > 0 else 0
            }
        })

    def _get_user_stats(self, user):
        """Вспомогательный метод для получения статистики пользователя"""
        completed_courses = UserCourseProgress.objects.filter(
            user=user,
            is_completed=True
        ).select_related('course').annotate(
            completion_date=F('completed_at')
        ).values('course__id', 'course__title', 'completion_date')

        stats = UserCourseProgress.objects.filter(
            user=user
        ).aggregate(
            total_courses=Count('id'),
            completed_courses=Count(
                Case(
                    When(is_completed=True, then=1),
                    output_field=IntegerField()
                )
            ),
            last_active=Max('last_accessed')
        )
        
        return {
            **stats,
            'completion_rate': round(
                stats['completed_courses'] / stats['total_courses'] * 100, 2
            ) if stats['total_courses'] > 0 else 0,
            'completed_courses_list': list(completed_courses)
        }