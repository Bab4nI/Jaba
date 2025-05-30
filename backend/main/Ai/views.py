from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
import openai
from rest_framework.views import APIView
from django.core.exceptions import ValidationError, PermissionDenied
from django.conf import settings
import time
from .models import (
    AIChatState,
)
from .serializers import (
    AIChatStateSerializer,
)


import logging

from rest_framework.decorators import action


logger = logging.getLogger(__name__)

# Create your views here.
class AIChatStateViewSet(viewsets.ModelViewSet):
    serializer_class = AIChatStateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIChatState.objects.filter(lesson_id=self.kwargs.get("lesson_id"))

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["GET"])
    def get_state(self, request, lesson_id=None):
        """Get the AI chat state for the lesson"""
        state, created = AIChatState.objects.get_or_create(
            lesson_id=lesson_id, defaults={"is_enabled": False}
        )
        serializer = self.get_serializer(state)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"])
    def toggle_state(self, request, lesson_id=None):
        """Toggle the AI chat state for the lesson"""
        state, created = AIChatState.objects.get_or_create(
            lesson_id=lesson_id, defaults={"is_enabled": False}
        )
        state.is_enabled = not state.is_enabled
        state.save()
        serializer = self.get_serializer(state)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"])
    def set_state(self, request, lesson_id=None):
        """Set the AI chat state to a specific value for the lesson"""
        state, created = AIChatState.objects.get_or_create(
            lesson_id=lesson_id, defaults={"is_enabled": False}
        )
        state.is_enabled = request.data.get("is_enabled", False)
        state.save()
        serializer = self.get_serializer(state)
        return Response(serializer.data)

class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def validate_request(self, request_data):
        if not request_data.get("prompt"):
            raise ValidationError("Prompt is required")
        return request_data["prompt"], request_data.get("selected_text", "")

    def post(self, request):
        try:
            prompt, selected_text = self.validate_request(request.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = self.get_ai_response(prompt, selected_text)
            return Response({"response": response}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"AI API error: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to process AI request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_ai_response(self, prompt, selected_text):
        client = openai.OpenAI(
            base_url="https://api.deepseek.com",
            api_key=settings.DEEPSEEK_API_KEY,
            timeout=30.0,  # Set a longer timeout
        )

        full_prompt = f'{prompt}: "{selected_text}"' if selected_text else prompt

        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                chat_response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты помощник для студентов. Отвечай кратко и понятно.",
                        },
                        {"role": "user", "content": full_prompt},
                    ],
                    model="deepseek-chat",
                    timeout=30,  # Set timeout for the request
                )
                return chat_response.choices[0].message.content

            except openai.APITimeoutError as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(
                        f"AI API timeout after {max_retries} attempts: {str(e)}"
                    )
                    raise Exception(
                        "Превышено время ожидания ответа от AI. Пожалуйста, попробуйте позже."
                    )
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

            except Exception as e:
                logger.error(f"AI API error: {str(e)}")
                raise Exception(
                    "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."
                )