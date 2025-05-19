import Course from '@/views/Course.vue';
import ArticleEditor from '@/views/ArticleEditor.vue';
import CourseEditor from '@/views/CourseEditor.vue';

export const courseRoutes = [
  {
    path: '/courses',
    name: 'CourseEditor',
    component: CourseEditor,
    props: true,
  },
  {
    path: '/courses/:slug',
    name: 'CourseDetail',
    component: Course
  },
  {
    path: '/courses/:courseSlug/modules/:moduleId/lessons/:lessonId',
    name: 'ArticleEditor',
    component: ArticleEditor,
    props: true,
  },
  { path: '/Course', component: Course },
]; 