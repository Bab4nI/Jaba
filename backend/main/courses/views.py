from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Course, Module, Lesson, LessonContent
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, LessonContentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import json
import logging
import time
from rest_framework.views import APIView
from django.conf import settings
import requests
from django.core.cache import cache

# Set up logging
logger = logging.getLogger(__name__)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Automatically set the author to the authenticated user
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Serializer validation failed: {str(e)}")
            logger.error(f"Request data: {dict(request.data)}")
            raise

        # Handle thumbnail deletion
        if 'thumbnail' in request.data and request.data['thumbnail'] in ['', None]:
            if instance.thumbnail:
                instance.thumbnail.delete(save=False)
                instance.thumbnail = None

        self.perform_update(serializer)
        return Response(serializer.data)

class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Module.objects.filter(
            course__slug=self.kwargs['course_slug']
        ).order_by('order')
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        last_order = Module.objects.filter(course=course).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 1
        serializer.save(course=course, order=new_order)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self): 
        return Lesson.objects.filter(
            module__id=self.kwargs['module_id']
        ).order_by('order')
    
    def perform_create(self, serializer):
        module = get_object_or_404(Module, id=self.kwargs['module_id'])
        last_order = Lesson.objects.filter(module=module).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 1
        serializer.save(module=module, order=new_order)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if 'thumbnail' in request.data and request.data['thumbnail'] == '':
            instance.thumbnail.delete(save=False)
        
        self.perform_update(serializer)
        return Response(serializer.data)

class LessonContentViewSet(viewsets.ModelViewSet):
    serializer_class = LessonContentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return LessonContent.objects.filter(
            lesson__id=self.kwargs['lesson_id']
        ).order_by('order')
    
    def perform_create(self, serializer):
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
        last_order = LessonContent.objects.filter(lesson=lesson).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 1
        
        serializer.save(lesson=lesson, order=new_order)
    
    def perform_update(self, serializer):
        instance = self.get_object()
        content_type = serializer.validated_data.get('content_type')

        if content_type == 'IMAGE' and 'image' in serializer.validated_data:
            if instance.image:
                instance.image.delete(save=False)
        elif content_type == 'FILE' and 'file' in serializer.validated_data:
            if instance.file:
                instance.file.delete(save=False)

        serializer.save()
    
    @transaction.atomic
    def update_order(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
        order_data = request.data.get('order', '[]')
        
        try:
            # Десериализуем JSON-строку в список объектов
            if isinstance(order_data, str):
                order_data = json.loads(order_data)
                
            for item in order_data:
                content = LessonContent.objects.get(
                    id=item['id'],
                    lesson=lesson
                )
                content.order = item['order']
                content.save()
            
            return Response({'status': 'order updated'}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON format in order data'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error': f'Missing key in order data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except LessonContent.DoesNotExist:
            return Response({'error': 'Invalid content ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CodeExecutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        source_code = request.data.get('source_code')
        language_id = request.data.get('language_id')
        interpreter = request.data.get('interpreter', 'default')
        stdin = request.data.get('stdin', '')

        if not source_code or not language_id:
            return Response(
                {'error': 'Source code and language ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(source_code) > 100_000:
            return Response(
                {'error': 'Source code is too large (max 100 KB)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        language_map = settings.JUDGE0_LANGUAGE_IDS.get(language_id, {})
        if not language_map:
            return Response(
                {'error': f'Unsupported language: {language_id}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        judge0_language_id = language_map.get(interpreter, language_map.get('default'))
        if not judge0_language_id:
            return Response(
                {'error': f'Unsupported interpreter: {interpreter} for language: {language_id}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"code_execution:{hash(source_code + str(judge0_language_id) + stdin)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for {cache_key}")
            return Response(cached_result, status=status.HTTP_200_OK)

        try:
            headers = {
                'Content-Type': 'application/json',
            }
            # Если используешь RapidAPI (публичный сервер Judge0)
            if hasattr(settings, 'JUDGE0_API_KEY') and settings.JUDGE0_API_KEY:
                headers.update({
                    'x-rapidapi-key': settings.JUDGE0_API_KEY,
                    'x-rapidapi-host': 'judge0-ce.p.rapidapi.com'
                })

            submission_data = {
                'source_code': source_code,
                'language_id': judge0_language_id,
                'stdin': stdin,
            }

            logger.info(f"Sending submission to Judge0: {submission_data}")
            response = requests.post(
                f'{settings.JUDGE0_API_URL}/submissions?base64_encoded=false&wait=false',
                json=submission_data,
                headers=headers
            )
            response.raise_for_status()
            logger.info(f"Judge0 submission response: {response.status_code} {response.text}")

            token = response.json().get('token')
            if not token:
                logger.error(f"No token received from Judge0: {response.text}")
                return Response(
                    {'error': 'Failed to create submission'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Ожидание завершения выполнения
            for attempt in range(10):
                time.sleep(1)
                result_response = requests.get(
                    f'{settings.JUDGE0_API_URL}/submissions/{token}?base64_encoded=false',
                    headers=headers
                )
                result_response.raise_for_status()
                result = result_response.json()

                if result.get('status', {}).get('id', 0) > 2:  # 1-2: In queue / Processing
                    output = {
                        'stdout': result.get('stdout', ''),
                        'stderr': result.get('stderr', ''),
                        'compile_output': result.get('compile_output', ''),
                        'status': result.get('status', {}).get('description', 'Unknown'),
                        'time': result.get('time', ''),
                        'memory': result.get('memory', '')
                    }
                    cache.set(cache_key, output, timeout=3600)
                    logger.info(f"Submission completed: {output}")
                    return Response(output, status=status.HTTP_200_OK)

            return Response(
                {'error': 'Submission timeout'},
                status=status.HTTP_408_REQUEST_TIMEOUT
            )

        except requests.RequestException as e:
            logger.error(f"Judge0 API error: {str(e)}")
            return Response(
                {'error': 'Failed to execute code'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )