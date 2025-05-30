from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ContentProgress
from content.models import Content
from courses.models import Lesson, Course
from .serializers import ContentProgressSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ContentProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ContentProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ContentProgress.objects.filter(user=self.request.user)
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            queryset = queryset.filter(content__lesson_id=lesson_id)
        return queryset

    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        content_id = request.data.get('content_id')
        score = request.data.get('score', 0)
        user_answer = request.data.get('user_answer', {})

        if not content_id:
            return Response(
                {'error': 'content_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        content = get_object_or_404(Content, id=content_id)
        
        progress, created = ContentProgress.objects.get_or_create(
            user=request.user,
            content=content,
            defaults={'score': score, 'user_answer': user_answer}
        )

        if not created:
            progress.score = score
            progress.user_answer = user_answer
            progress.save()

        return Response({
            'score': progress.score,
            'completed': progress.completed
        })

    @action(detail=False, methods=['post'])
    def reset_progress(self, request):
        lesson_id = request.data.get('lesson_id')
        
        if not lesson_id:
            return Response(
                {'error': 'lesson_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        lesson = get_object_or_404(Lesson, id=lesson_id)
        contents = Content.objects.filter(lesson=lesson)
        
        # Delete all progress for this lesson's contents
        ContentProgress.objects.filter(
            user=request.user,
            content__in=contents
        ).delete()

        return Response({'status': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_statistics(request):
    course_slug = request.GET.get('course_slug')
    group = request.GET.get('group')

    # Найти курс
    try:
        course = Course.objects.get(slug=course_slug)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=404)

    # Найти все уроки курса
    lessons = Lesson.objects.filter(module__course=course)
    lessons_data = [{'id': l.id, 'title': l.title, 'max_score': l.max_score} for l in lessons]

    # Найти пользователей группы
    if group == 'admins':
        users = User.objects.filter(is_staff=True)
    else:
        users = User.objects.filter(groups__name=group)

    users_data = []
    for user in users:
        fio = f'{getattr(user, "last_name", "").strip()} {getattr(user, "first_name", "").strip()} {getattr(user, "middle_name", "").strip()}'.strip()
        if not fio or fio == '':
            fio = getattr(user, 'email', f'User {user.id}')
        progress = ContentProgress.objects.filter(user=user, content__lesson__in=lessons)
        progress_map = {p.content.lesson.id: {
            'score': p.score,
            'completed': p.completed,
            'max_score': p.content.lesson.max_score
        } for p in progress}
        users_data.append({
            'id': user.id,
            'full_name': fio,
            'progress': progress_map
        })

    return Response({
        'course': {'title': course.title},
        'lessons': lessons_data,
        'users': users_data
    }) 