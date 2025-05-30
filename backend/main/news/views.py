from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
import logging
from .models import News
from .serializers import NewsSerializer

# Configure logging
logger = logging.getLogger(__name__)

# Create your views here.


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=False, methods=["post"])
    def upload_media(self, request):
        try:
            # Get the image file from request
            image_file = request.FILES.get("image")
            if not image_file:
                logger.error("No image file provided in request")
                return Response(
                    {"error": "No image file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate a unique filename
            filename = f"news_images/{image_file.name}"

            # Save the file
            path = default_storage.save(filename, image_file)

            # Get the URL for the saved file
            url = default_storage.url(path)

            logger.info(f"Image uploaded successfully. Path: {path}, URL: {url}")
            return Response(
                {"success": True, "image_path": path, "url": url},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Creating news with data: {request.data}")
            response = super().create(request, *args, **kwargs)
            logger.info(f"News created successfully: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error creating news: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"Updating news {kwargs.get('pk')} with data: {request.data}")
            response = super().update(request, *args, **kwargs)
            logger.info(f"News updated successfully: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error updating news: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
