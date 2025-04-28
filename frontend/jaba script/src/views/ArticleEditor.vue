<template>
  <div class="article-editor-container" :class="{ 'preview-mode': mode === 'preview' }">
    <div class="editor-header">
      <h1>{{ article.title }}</h1>
      <div class="header-controls">
        <button @click="toggleMode" class="mode-toggle-button">
          {{ mode === 'edit' ? 'Предпросмотр' : 'Редактировать' }}
        </button>
        <button @click="goBack" class="back-button">← Назад к модулям</button>
      </div>
    </div>
    
    <div class="contents-list">
      <draggable 
        v-if="mode === 'edit'"
        v-model="contents" 
        item-key="id"
        handle=".drag-handle"
        group="contents"
        :animation="200"
        :force-fallback="true"
        :drag-options="{ multiDrag: false, swapThreshold: 0.5 }"
        @end="saveOrder"
      >
        <template #item="{element, index}">
          <div class="content-item">
            <div class="content-toolbar">
              <span class="drag-handle" aria-label="Перетащить элемент">☰</span>
              <span class="content-type">{{ getContentTypeName(element.type) }}</span>
              <button @click="removeContent(index)" class="remove-content-btn">×</button>
            </div>
            
            <component 
              :is="getContentComponent(element.type)"
              :content="element"
              :lessonId="article.id"
              :readOnly="mode === 'preview'"
              @update:content="handleContentUpdate(index, $event)"
            />
          </div>
        </template>
      </draggable>
      <div v-else class="preview-content">
        <div v-for="(element, index) in contents" :key="element.id || index" class="content-item">
          <component 
            :is="getContentComponent(element.type)"
            :content="element"
            :lessonId="article.id"
            :readOnly="true"
            @update:content="handleContentUpdate(index, $event)"
          />
        </div>
      </div>
    </div>
    
    <div v-if="mode === 'edit'" class="editor-toolbar">
      <select v-model="selectedContentType" class="content-type-select">
        <option value="">Добавить элемент...</option>
        <option value="text">Текст</option>
        <option value="image">Изображение</option>
        <option value="video">Видео</option>
        <option value="code">Код</option>
        <option value="quiz">Тест</option>
        <option value="table">Таблица</option>
        <option value="file">Файл</option>
      </select>
      
      <button 
        @click="addContent" 
        class="add-content-btn"
        :disabled="!selectedContentType"
      >
        Добавить
      </button>
    </div>
    
    <div v-if="mode === 'edit'" class="editor-footer">
      <button @click="saveAllChanges" class="save-button">Сохранить работу</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import draggable from 'vuedraggable';
import TextElement from '@/components/article/TextElement.vue';
import ImageElement from '@/components/article/ImageElement.vue';
import VideoElement from '@/components/article/VideoElement.vue';
import CodeElement from '@/components/article/CodeElement.vue';
import QuizElement from '@/components/article/QuizElement.vue';
import TableElement from '@/components/article/TableElement.vue';
import FileElement from '@/components/article/FileElement.vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';

const CONTENT_TYPES = {
  text: 'TEXT',
  image: 'IMAGE',
  video: 'VIDEO',
  code: 'CODE',
  quiz: 'QUIZ',
  table: 'TABLE',
  file: 'FILE',
};

const DEFAULT_CONTENT = {
  text: { text: '' },
  image: { image: null },
  video: { video_url: '' },
  code: { code: '', language: 'javascript' },
  quiz: { question: '', answers: ['', ''], correct_answer: null },
  table: { headers: ['Заголовок 1', 'Заголовок 2'], data: [['', ''], ['', '']] },
  file: { file: null },
};

export default {
  components: {
    draggable,
    TextElement,
    ImageElement,
    VideoElement,
    CodeElement,
    QuizElement,
    TableElement,
    FileElement,
  },

  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useRefreshStore();

    const api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    });

    api.interceptors.request.use(
      (config) => {
        const token = authStore.accessToken || localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            await authStore.refreshToken();
            originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
            return api(originalRequest);
          } catch (refreshError) {
            console.error('❌ Не удалось обновить токен:', refreshError);
            authStore.logout();
            router.push({ name: 'SignIn' });
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );

    const article = ref({
      id: route.params.lessonId,
      title: route.query.title || 'Новая работа',
      type: route.query.type || 'article',
    });

    const selectedContentType = ref('');
    const contents = ref([]);
    const pendingUpdates = ref(new Map());
    const mode = ref('edit'); // 'edit' or 'preview'

    const getContentTypeName = (type) => {
      const types = {
        text: 'Текст',
        image: 'Изображение',
        video: 'Видео',
        code: 'Код',
        quiz: 'Тест',
        table: 'Таблица',
        file: 'Файл',
      };
      return types[type] || type;
    };

    const getContentComponent = (type) => {
      const components = {
        text: 'TextElement',
        image: 'ImageElement',
        video: 'VideoElement',
        code: 'CodeElement',
        quiz: 'QuizElement',
        table: 'TableElement',
        file: 'FileElement',
      };
      return components[type] || 'TextElement';
    };

    const getVueContentType = (djangoType) => {
      const typeMap = {
        TEXT: 'text',
        IMAGE: 'image',
        VIDEO: 'video',
        FILE: 'file',
        CODE: 'code',
        QUIZ: 'quiz',
        TABLE: 'table',
      };
      return typeMap[djangoType] || 'text';
    };

    const convertFromDjangoFormat = (djangoContent) => {
      const type = getVueContentType(djangoContent.content_type);
      const base = {
        id: djangoContent.id,
        type,
        order: djangoContent.order || 0,
      };

      switch (type) {
        case 'text':
          return { ...base, text: djangoContent.text || '' };
        case 'code':
          return {
            ...base,
            code: djangoContent.text || '',
            language: djangoContent.code_language || 'javascript',
          };
        case 'quiz':
          return {
            ...base,
            question: djangoContent.quiz_data?.question || '',
            answers: djangoContent.quiz_data?.answers || ['', ''],
            correct_answer: djangoContent.quiz_data?.correct_answer || null,
          };
        case 'table':
          return {
            ...base,
            headers: djangoContent.table_data?.headers || ['Заголовок 1', 'Заголовок 2'],
            data: djangoContent.table_data?.data || [['', ''], ['', '']],
          };
        case 'image':
          return { ...base, image: djangoContent.image ? djangoContent.image : null };
        case 'video':
          return { ...base, video_url: djangoContent.video_url || '' };
        case 'file':
          return {
            ...base,
            file: djangoContent.file ? djangoContent.file : null,
            filename: djangoContent.filename || (djangoContent.file ? djangoContent.file.split('/').pop() : null),
          };
        default:
          return base;
      }
    };

    const convertToDjangoFormat = (content) => {
      const payload = {
        content_type: CONTENT_TYPES[content.type],
        order: content.order || 0,
      };

      switch (content.type) {
        case 'text':
          payload.text = content.text || '';
          break;
        case 'code':
          payload.text = content.code || '';
          payload.code_language = content.language || 'javascript';
          break;
        case 'quiz':
          payload.quiz_data = {
            question: content.question || '',
            answers: content.answers || [],
            correct_answer: content.correct_answer ?? null,
          };
          break;
        case 'table':
          payload.table_data = {
            headers: content.headers || [],
            data: content.data || [],
          };
          break;
        case 'image':
          payload.image = content.image || null;
          break;
        case 'video':
          payload.video_url = content.video_url || '';
          break;
        case 'file':
          payload.file = content.file || null;
          break;
      }

      return payload;
    };

    const validateContent = (content) => {
      const errors = [];
      switch (content.type) {
        case 'text':
          if (!content.text) errors.push('Текст обязателен для типа "Текст".');
          break;
        case 'code':
          if (!content.code) errors.push('Код обязателен для типа "Код".');
          if (!content.language) errors.push('Язык программирования обязателен для типа "Код".');
          break;
        case 'quiz':
          if (!content.question) errors.push('Вопрос обязателен для типа "Тест".');
          if (!content.answers || content.answers.length < 2) errors.push('Необходимо минимум два ответа для теста.');
          if (content.correct_answer === null || content.correct_answer === undefined) errors.push('Правильный ответ обязателен для теста.');
          break;
        case 'table':
          if (!content.headers || !content.headers.length) errors.push('Заголовки таблицы обязательны.');
          if (!content.data || !content.data.length) errors.push('Данные таблицы обязательны.');
          break;
        case 'image':
          if (!content.image) errors.push('Изображение обязательно для типа "Изображение".');
          break;
        case 'video':
          if (!content.video_url) errors.push('URL видео обязателен для типа "Видео".');
          break;
        case 'file':
          if (!content.file) errors.push('Файл обязателен для типа "Файл".');
          break;
      }
      return errors;
    };

    const loadArticle = async () => {
      try {
        const response = await api.get(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`);
        contents.value = response.data.map(item => convertFromDjangoFormat(item)).sort((a, b) => a.order - b.order);
      } catch (error) {
        console.error('Ошибка загрузки содержимого:', error.response?.data || error);
        contents.value = [];
      }
    };

    const addContent = () => {
      if (!selectedContentType.value) return;

      const newContent = {
        id: null,
        type: selectedContentType.value,
        order: contents.value.length + 1,
        ...JSON.parse(JSON.stringify(DEFAULT_CONTENT[selectedContentType.value])),
      };

      contents.value.push(newContent);
      pendingUpdates.value.set(contents.value.length - 1, true);
      selectedContentType.value = '';
    };

    const handleContentUpdate = (index, updatedContent) => {
      if (mode.value === 'preview') return; // Prevent updates in preview mode
      contents.value[index] = { ...contents.value[index], ...updatedContent };
      pendingUpdates.value.set(index, true);
    };

    const updateContent = async (index) => {
      const content = contents.value[index];
      const validationErrors = validateContent(content);
      if (validationErrors.length) {
        throw new Error(validationErrors.join(' '));
      }

      const payload = convertToDjangoFormat(content);
      const formData = new FormData();

      Object.entries(payload).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          if (key === 'quiz_data' || key === 'table_data') {
            formData.append(key, JSON.stringify(value));
          } else if (key === 'image' || key === 'file') {
            if (value instanceof File) {
              formData.append(key, value);
            }
          } else {
            formData.append(key, value);
          }
        }
      });

      try {
        if (content.id) {
          const response = await api({
            method: 'put',
            url: `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/${content.id}/`,
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          contents.value[index] = convertFromDjangoFormat(response.data);
        } else {
          const response = await api({
            method: 'post',
            url: `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`,
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          contents.value[index] = convertFromDjangoFormat(response.data);
        }
        pendingUpdates.value.delete(index);
      } catch (error) {
        console.error('Ошибка сохранения контента:', error.response?.data || error);
        throw error;
      }
    };

    const removeContent = async (index) => {
      if (!confirm('Вы уверены, что хотите удалить этот элемент?')) return;

      const content = contents.value[index];
      if (content.id) {
        try {
          await api.delete(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/${content.id}/`);
        } catch (error) {
          console.error('Ошибка удаления контента:', error.response?.data || error);
          throw error;
        }
      }
      contents.value.splice(index, 1);
      pendingUpdates.value.delete(index);
      contents.value.forEach((item, i) => (item.order = i + 1));
      await saveOrder();
    };

    const saveOrder = async () => {
      const orderedIds = contents.value
        .filter(content => content.id)
        .map((content, index) => ({
          id: content.id,
          order: index + 1,
        }));

      if (orderedIds.length === 0) return;

      const formData = new FormData();
      formData.append('order', JSON.stringify(orderedIds));

      try {
        await api({
          method: 'patch',
          url: `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/order/`,
          data: formData,
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        contents.value.forEach((content, index) => (content.order = index + 1));
      } catch (error) {
        console.error('Ошибка сохранения порядка:', error.response?.data || error);
        throw error;
      }
    };

    const saveAllChanges = async () => {
      try {
        // Сохраняем урок
        const lessonFormData = new FormData();
        lessonFormData.append('title', article.value.title);
        lessonFormData.append('type', article.value.type.toUpperCase());

        await api({
          method: 'put',
          url: `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/`,
          data: lessonFormData,
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        // Сохраняем все измененные элементы
        const updatePromises = [];
        pendingUpdates.value.forEach((_, index) => {
          updatePromises.push(updateContent(index));
        });

        await Promise.all(updatePromises);
        await saveOrder();

        alert('Все изменения успешно сохранены!');
      } catch (error) {
        console.error('Ошибка сохранения работы:', error.response?.data || error);
        let errorMessage = 'Неизвестная ошибка';
        if (error.response?.data) {
          errorMessage = error.response.data.detail || JSON.stringify(error.response.data);
        } else if (error.message) {
          errorMessage = error.message;
        }
        alert(`Ошибка при сохранении работы: ${errorMessage}`);
      }
    };

    const goBack = () => {
      router.push({
        name: 'CourseDetail',
        params: { slug: route.params.courseSlug },
      });
    };

    const toggleMode = () => {
      mode.value = mode.value === 'edit' ? 'preview' : 'edit';
    };

    onMounted(() => {
      loadArticle();
    });

    return {
      article,
      selectedContentType,
      contents,
      mode,
      getContentTypeName,
      getContentComponent,
      addContent,
      handleContentUpdate,
      removeContent,
      saveAllChanges,
      goBack,
      toggleMode,
    };
  },
};
</script>

<style scoped>
.article-editor-container {
  max-width: 800px; /* Reduced max-width to match Stepik's narrower content area */
  margin: 0 auto;
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.editor-header h1 {
  font-size: 24px; /* Adjusted font size to match Stepik */
  font-weight: 700;
  text-align: left; /* Align title to the left */
}

.header-controls {
  display: flex;
  gap: 10px;
}

.mode-toggle-button {
  background: #6b7280;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.mode-toggle-button:hover {
  background: #4b5563;
}

.back-button {
  background: #a094b8;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.editor-toolbar {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.content-type-select {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-content-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.add-content-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.contents-list {
  margin: 20px 0;
}

/* Edit Mode Styles */
.article-editor-container:not(.preview-mode) .contents-list {
  display: flex;
  flex-direction: column; /* Stack items vertically in edit mode */
  gap: 15px;
}

.article-editor-container:not(.preview-mode) .content-item {
  border: none; /* Remove border as per Stepik style */
  padding: 15px 0; /* Adjust padding for a cleaner look */
  background: transparent; /* Remove background */
  min-height: 100px;
  box-sizing: border-box;
}

/* Specific styles for text, file, and quiz elements in edit mode */
.article-editor-container:not(.preview-mode) .content-item:has(> text-element),
.article-editor-container:not(.preview-mode) .content-item:has(> file-element),
.article-editor-container:not(.preview-mode) .content-item:has(> quiz-element) {
  border: none; /* Explicitly remove borders */
  box-shadow: none; /* Remove any potential shadows */
  background: transparent; /* Ensure no background */
}

.article-editor-container:not(.preview-mode) .content-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #ddd;
}

.article-editor-container:not(.preview-mode) .drag-handle {
  cursor: move;
  margin-right: 10px;
  font-size: 18px;
}

.article-editor-container:not(.preview-mode) .content-type {
  flex-grow: 1;
  font-weight: bold;
  color: #555;
}

.article-editor-container:not(.preview-mode) .remove-content-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

/* Preview Mode Styles */
.article-editor-container.preview-mode .contents-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-editor-container.preview-mode .preview-content {
  max-width: 800px;
  margin: 0; /* Align content to the left */
  text-align: left; /* Ensure text is left-aligned */
}

.article-editor-container.preview-mode .content-item {
  border: none; /* Remove border as per Stepik style */
  padding: 10px 0; /* Adjust padding for a cleaner look */
  background: transparent; /* Remove background */
  box-shadow: none; /* Remove shadow */
  min-height: auto;
  box-sizing: border-box;
}

/* Specific styles for text, file, and quiz elements in preview mode */
.article-editor-container.preview-mode .content-item:has(> text-element),
.article-editor-container.preview-mode .content-item:has(> file-element),
.article-editor-container.preview-mode .content-item:has(> quiz-element) {
  border: none; /* Explicitly remove borders */
  box-shadow: none; /* Remove any potential shadows */
  background: transparent; /* Ensure no background */
}

.article-editor-container.preview-mode .content-toolbar {
  display: none; /* Hide toolbar in preview mode */
}

.editor-footer {
  margin-top: 30px;
  text-align: center;
}

.save-button {
  background: #a094b8;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
</style>