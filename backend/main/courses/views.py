from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import (
    Course,
    Module,
    Lesson,
)
from .serializers import (
    CourseSerializer,
    ModuleSerializer,
    LessonSerializer,
)
from django.shortcuts import get_object_or_404
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)  # Add JSONParser

from django.db import transaction
import json
import logging
import time
from rest_framework.views import APIView
from django.conf import settings
import requests
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
    queryset = Course.objects.select_related("author").prefetch_related("modules")
    serializer_class = CourseSerializer
    lookup_field = "slug"
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]  # Add JSONParser for flexibility

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # If user is not authenticated, show only published courses
        if not user.is_authenticated:
            return queryset.filter(is_published=True)

        # If user is admin, show all courses
        if hasattr(user, "role") and user.role == "admin":
            return queryset

        # For students, show only published courses
        return queryset.filter(is_published=True)

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
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            return Response(
                {"detail": f"Failed to create course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_object(self):
        """
        Override to handle case-insensitive slug lookup and improve error handling
        for Cyrillic characters in slugs
        """
        self.filter_queryset(self.get_queryset())

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
            if "thumbnail" in request.data and request.data["thumbnail"] in ["", None]:
                if instance.thumbnail:
                    instance.thumbnail.delete(save=False)
                    instance.thumbnail = None

            self.perform_update(serializer)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Course not found with slug: {kwargs.get('slug')}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            return Response(
                {"detail": f"Failed to update course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
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
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error deleting course: {str(e)}")
            return Response(
                {"detail": f"Failed to delete course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        logger.info(
            f"Fetching courses list. User: {request.user}, Role: {getattr(request.user, 'role', 'unknown')}"
        )
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Found {len(serializer.data)} courses")
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to view modules

    def get_queryset(self):
        return (
            Module.objects.filter(course__slug=self.kwargs["course_slug"])
            .select_related("course")
            .prefetch_related("lessons")
            .order_by("order")
        )

    def perform_create(self, serializer):
        course = get_object_or_404(Course, slug=self.kwargs["course_slug"])
        last_order = Module.objects.filter(course=course).order_by("-order").first()
        new_order = (last_order.order + 1) if last_order else 1
        serializer.save(course=course, order=new_order)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]  # Allow anyone to view lessons

    def get_queryset(self):
        module_id = self.kwargs.get("module_id")
        if not module_id:
            return Lesson.objects.none()
        return (
            Lesson.objects.filter(module_id=module_id)
            .select_related("module")
            .order_by("order")
        )

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
        module_id = self.kwargs.get("module_id")
        module = get_object_or_404(Module, id=module_id)

        # Calculate new order
        last_order = (
            Lesson.objects.filter(module=module).aggregate(models.Max("order"))[
                "order__max"
            ]
            or 0
        )

        # Add module and order to request data
        data = request.data.copy()
        data["module"] = module_id
        data["order"] = last_order + 1

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Handle thumbnail deletion if empty string is passed
        if "thumbnail" in request.data and request.data["thumbnail"] == "":
            if instance.thumbnail:
                instance.thumbnail.delete(save=False)
                instance.thumbnail = None

        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class CodeExecutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def validate_request(self, request_data):
        required_fields = ["source_code", "language_id"]
        for field in required_fields:
            if field not in request_data:
                raise ValidationError(f"{field} is required")
        return request_data

    def post(self, request):
        try:
            data = self.validate_request(request.data)
            source_code = data["source_code"]
            language_id = data["language_id"]
            stdin = data.get("stdin", "")
            content_id = data.get("content_id")

            # Если content_id указан, проверяем доступность урока
            if content_id:
                try:
                    content = LessonContent.objects.get(id=content_id)
                    if not content.lesson.is_available:
                        return Response(
                            {
                                "detail": "Время на выполнение задания истекло. Запуск кода запрещён."
                            },
                            status=status.HTTP_403_FORBIDDEN,
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
                            "completed": True,
                            "max_score": content.max_score,
                            "current_score": 0,
                        },
                    )

                    # Calculate score based on execution result
                    if result.get("status", {}).get("id") == 3:  # Accepted
                        progress.current_score = content.max_score
                    else:
                        progress.current_score = 0

                    progress.completed = True
                    progress.save()

                    result["progress"] = {
                        "content_id": content.id,
                        "completed": True,
                        "max_score": progress.max_score,
                        "current_score": progress.current_score,
                        "completed_at": progress.completed_at,
                    }
                except LessonContent.DoesNotExist:
                    pass

            return Response(result)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return Response(
                {"detail": "Failed to execute code"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def execute_code(self, source_code, language_id, stdin):
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        }

        # Map language_id to Judge0 language ID
        language_map = {
            "javascript": 63,  # Node.js
            "python": 71,  # Python 3
            "java": 62,  # Java
            "cpp": 54,  # C++
            "csharp": 51,  # C#
            "php": 68,  # PHP
            "ruby": 72,  # Ruby
            "swift": 83,  # Swift
            "go": 60,  # Go
            "rust": 73,  # Rust
            "kotlin": 78,  # Kotlin
            "scala": 81,  # Scala
        }

        # Get the correct language ID
        judge0_language_id = language_map.get(
            language_id.lower(), 71
        )  # Default to Python if language not found

        submission_data = {
            "source_code": source_code,
            "language_id": judge0_language_id,
            "stdin": stdin,
            "cpu_time_limit": 5,  # 5 seconds
            "memory_limit": 128000,  # 128MB
            "stack_limit": 128000,  # 128MB
            "max_processes_and_or_threads": 60,
            "enable_per_process_and_thread_time_limit": False,
            "enable_network": False,
        }

        logger.info(f"Sending submission to Judge0: {submission_data}")

        try:
            response = requests.post(
                f"{settings.JUDGE0_API_URL}/submissions?base64_encoded=false&wait=false",
                json=submission_data,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            logger.info(
                f"Judge0 submission response: {response.status_code} {response.text}"
            )

            token = response.json().get("token")
            if not token:
                raise requests.RequestException("No token received from Judge0")

            result = self.poll_submission_result(token, headers)
            return {
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "compile_output": result.get("compile_output", ""),
                "status": result.get("status", {}),
                "time": result.get("time", ""),
                "memory": result.get("memory", ""),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Judge0 API error: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"Response text: {e.response.text}")
            raise

    def poll_submission_result(self, token, headers, max_attempts=10, delay=1):
        for attempt in range(max_attempts):
            time.sleep(delay)
            try:
                result_response = requests.get(
                    f"{settings.JUDGE0_API_URL}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                    timeout=10,
                )
                result_response.raise_for_status()
                result = result_response.json()

                if result.get("status", {}).get("id", 0) > 2:
                    return result
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling submission result: {str(e)}")
                if attempt == max_attempts - 1:
                    raise

        raise requests.RequestException("Submission timeout")

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
        if "image" not in request.FILES and "file" not in request.FILES:
            return Response(
                {"error": "No files found. Please upload an image or file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_type = None
        file_obj = None

        # Check if it's an image upload
        if "image" in request.FILES:
            file_type = "image"
            file_obj = request.FILES["image"]
            # Verify it's an image
            if not file_obj.content_type.startswith("image/"):
                return Response(
                    {"error": "Uploaded file is not an image."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check if it's a file upload
        elif "file" in request.FILES:
            file_type = "file"
            file_obj = request.FILES["file"]

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
        with open(file_path, "wb+") as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        # Path as it would be accessed from client via media URL
        media_path = os.path.join(folder_path, unique_filename).replace("\\", "/")

        return Response(
            {
                "success": True,
                "file_type": file_type,
                "file_name": file_obj.name,
                "file_path": f"/media/{media_path}",
                "image_path": f"/media/{media_path}" if file_type == "image" else None,
            },
            status=status.HTTP_201_CREATED,
        )