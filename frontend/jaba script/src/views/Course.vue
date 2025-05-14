<template>
  <div>
    <div class="main-content-container">
      <div class="main-content-section">
        <div class="module-card-container">
          <div class="module-title-container">
            <div class="svg-container">
              <svg viewBox="0 0 24 24" x="0" y="0" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g id="Group 65" xmlns="http://www.w3.org/2000/svg">
                  <circle id="Ellipse 7" cx="11" cy="9.5" r="8" stroke="currentColor" />
                  <line id="Line 12" x1="15.879999999999995" y1="15.675000000000011" x2="21.879999999999995" y2="22.67500000000001" stroke="currentColor" />
                </g>
              </svg>
            </div>
            <input 
              v-model="searchQuery"
              class="search-input" 
              placeholder="Поиск по модулям и работам"
              @input="searchModules"
            />
          </div>
          <button class="search-button" @click="searchModules">Поиск</button>
        </div>

        <div class="main-content-container1">
          <div 
            v-for="(module, moduleIndex) in filteredModules" 
            :key="module.id" 
            class="module-container4"
          >
            <div class="save-button-container">
              <button class="save-button" @click="saveModule(moduleIndex)">Сохранить</button>
              <button class="delete-button" @click="deleteModule(moduleIndex)">Удалить</button>
            </div>
            <div class="module-container3">
              <div class="module-container2">
                <input 
                  v-model="module.title" 
                  class="module-title-input"
                  placeholder="Название модуля"
                  @change="updateModuleTitle(moduleIndex, $event)"
                />
              </div>
              
              <div class="articles-wrapper">
                <div 
                  v-for="(lesson, lessonIndex) in module.lessons" 
                  :key="lesson.id" 
                  class="article-card"
                  @click="openArticleEditor(moduleIndex, lessonIndex)"
                >
                  <img 
                    class="article-thumbnail" 
                    :src="getImageUrl(lesson.thumbnail)" 
                  />
                  <div class="article-content">
                    <h3>{{ lesson.title }}</h3>
                    <p>{{ lesson.description || 'Без описания' }}</p>
                    <div class="article-meta">
                      <span>{{ formatDate(lesson.created_at) }}</span>
                      <span class="lesson-type">{{ getTypeLabel(lesson.type) }}</span>
                      <div class="article-actions">
                        <button @click.stop="editLesson(moduleIndex, lessonIndex)">
                          <img src="@/assets/images/pencil_4211918_1.png" />
                        </button>
                        <button @click.stop="deleteLesson(moduleIndex, lessonIndex)">
                          <img src="@/assets/images/delete_16596354_1.png" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div 
                  class="add-article-card" 
                  @click="addLesson(moduleIndex)"
                >
                  <img 
                    src="@/assets/images/image_5f285c02.png" 
                    class="add-article-image" 
                    alt="Добавить работу"
                  />
                </div>
              </div>
            </div>
          </div>

          <p 
            class="add-module-btn" 
            @click="addModule"
          >
            + Добавить модуль
          </p>
        </div>
      </div>
    </div>
    
    <div v-if="editingLesson" class="modal-overlay">
      <div class="modal-content">
        <h3>Редактирование работы</h3>
        <div class="form-group">
          <label>Название:</label>
          <input 
            v-model="editingLesson.title" 
            placeholder="Введите название" 
            name="title"
            class="title-input"
          />
        </div>
        
        <div class="form-group">
          <label>Описание:</label>
          <textarea 
            v-model="editingLesson.description" 
            placeholder="Введите описание"
            class="fixed-textarea"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>Тип работы:</label>
          <select v-model="editingLesson.type" @change="updateDefaultThumbnail">
            <option value="ARTICLE">Статья</option>
            <option value="LAB">Лабораторная работа</option>
            <option value="PRACTICE">Практика</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Длительность (минуты):</label>
          <input 
            type="number" 
            v-model.number="editingLesson.duration"
            placeholder="Введите длительность"
            min="0"
          />
        </div>
        
        <div class="form-group">
          <label>Порядок:</label>
          <input 
            type="number" 
            v-model.number="editingLesson.order"
            placeholder="Введите порядок"
            min="0"
          />
        </div>
        
        <div class="form-group">
          <label>Изображение:</label>
          <div class="image-upload-container">
            <label for="image-upload" class="image-upload-label">
              <span v-if="!editingLesson.thumbnail">Выберите изображение</span>
              <span v-else>Изменить изображение</span>
              <input 
                id="image-upload" 
                type="file" 
                accept="image/*" 
                @change="handleImageUpload"
                class="image-upload-input"
              />
            </label>
            <div v-if="editingLesson.thumbnail" class="image-preview">
              <img :src="getImageUrl(editingLesson.thumbnail)" class="preview-image" />
              <button @click="removeImage" class="remove-image-btn">×</button>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="saveEditedLesson" class="save-btn">Сохранить</button>
          <button @click="cancelEdit" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';
import articleImg from '@/assets/images/article.png';
import labImg from '@/assets/images/lab.png';
import pracImg from '@/assets/images/prac.png';

export default {
  name: 'CourseEditor',

  setup() {
    const router = useRouter();
    const route = useRoute();
    const authStore = useRefreshStore();

    const api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
      headers: {
        'Content-Type': 'application/json',
      },
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

    return {
      router,
      route,
      api,
      authStore,
    };
  },

  data() {
    return {
      searchQuery: '',
      modules: [],
      filteredModules: [],
      editingLesson: null,
      editingModuleIndex: null,
      editingLessonIndex: null,
      isLoading: false,
    };
  },

  computed: {
    courseSlug() {
      return this.route.params.slug;
    },
  },

  methods: {
    getImageUrl(imagePath) {
      if (!imagePath) return '';
      if (typeof imagePath === 'object') {
        return URL.createObjectURL(imagePath);
      }
      if (imagePath.startsWith('http')) return imagePath;
      return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${imagePath}`;
    },

    formatDate(date) {
      if (!date) return '';
      const d = new Date(date);
      return d.toLocaleDateString('ru-RU');
    },

    getTypeLabel(type) {
      const typeMap = {
        ARTICLE: 'Статья',
        LAB: 'Лабораторная работа',
        PRACTICE: 'Практика',
      };
      return typeMap[type] || 'Статья';
    },

    async getDefaultImage(type) {
      const imageMap = {
        ARTICLE: { src: articleImg, name: 'article.png' },
        LAB: { src: labImg, name: 'lab.png' },
        PRACTICE: { src: pracImg, name: 'prac.png' },
      };
      const { src, name } = imageMap[type] || imageMap.ARTICLE;

      try {
        const response = await fetch(src);
        const blob = await response.blob();
        return new File([blob], name, { type: blob.type });
      } catch (error) {
        console.error(`❌ Ошибка загрузки изображения для ${type}:`, error);
        return null;
      }
    },

    async updateDefaultThumbnail() {
      if (this.editingLesson) {
        const defaultImage = await this.getDefaultImage(this.editingLesson.type || 'ARTICLE');
        if (defaultImage) {
          this.editingLesson.thumbnail = defaultImage;
        } else {
          this.editingLesson.thumbnail = '';
        }
      }
    },

    async loadModules() {
      this.isLoading = true;
      try {
        const response = await this.api.get(`/courses/${this.courseSlug}/modules/`);
        this.modules = Array.isArray(response.data) ? response.data : [];
        this.filteredModules = [...this.modules];
        console.log('✅ Модули загружены:', this.modules);
      } catch (error) {
        console.error('❌ Ошибка загрузки модулей:', error);
        this.modules = [];
        this.filteredModules = [];
        if (error.response?.status === 401) {
          this.authStore.logout();
          this.router.push({ name: 'SignIn' });
        }
      } finally {
        this.isLoading = false;
      }
    },

    searchModules() {
      const query = this.searchQuery.toLowerCase().trim();
      if (!query) {
        this.filteredModules = [...this.modules];
        return;
      }
      this.filteredModules = this.modules
        .map((module) => ({
          ...module,
          lessons: module.lessons.filter(
            (lesson) =>
              lesson.title?.toLowerCase().includes(query) ||
              lesson.description?.toLowerCase().includes(query)
          ),
        }))
        .filter(
          (module) =>
            module.title?.toLowerCase().includes(query) || module.lessons.length > 0
        );
    },

    generateUniqueModuleTitle(baseTitle, existingTitles) {
      let title = baseTitle;
      let counter = 1;
      while (existingTitles.includes(title)) {
        title = `${baseTitle} ${counter}`;
        counter++;
      }
      return title;
    },

    async addModule() {
      const baseTitle = 'Новый модуль';
      const existingTitles = this.modules.map((module) => module.title);
      const uniqueTitle = this.generateUniqueModuleTitle(baseTitle, existingTitles);

      try {
        const response = await this.api.post(`/courses/${this.courseSlug}/modules/`, {
          title: uniqueTitle,
          course: this.courseSlug,
          description: '',
          order: this.modules.length,
        });
        this.modules.push({ ...response.data, lessons: [] });
        this.searchModules();
        console.log('✅ Модуль создан:', response.data);
      } catch (error) {
        console.error('❌ Ошибка создания модуля:', error);
        const errorMessage = error.response?.data?.title || error.response?.data?.detail || 'Неизвестная ошибка';
        alert('Не удалось создать модуль: ' + errorMessage);
      }
    },

    async saveModule(moduleIndex) {
      const module = this.modules[moduleIndex];
      try {
        await this.api.put(`/courses/${this.courseSlug}/modules/${module.id}/`, {
          title: module.title,
          course: this.courseSlug,
          description: module.description || '',
          order: module.order || 0,
        });
        console.log('✅ Модуль сохранен:', module);
        alert('Модуль успешно сохранен');
      } catch (error) {
        console.error('❌ Ошибка сохранения модуля:', error);
        const errorMessage = error.response?.data?.title || error.response?.data?.detail || 'Неизвестная ошибка';
        alert('Не удалось сохранить модуль: ' + errorMessage);
      }
    },

    async deleteModule(moduleIndex) {
      const module = this.modules[moduleIndex];
      if (!confirm('Вы уверены, что хотите удалить этот модуль?')) return;
      try {
        await this.api.delete(`/courses/${this.courseSlug}/modules/${module.id}/`);
        this.modules.splice(moduleIndex, 1);
        this.searchModules();
        console.log('✅ Модуль удален:', module.id);
      } catch (error) {
        console.error('❌ Ошибка удаления модуля:', error);
        alert('Не удалось удалить модуль: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
      }
    },

    updateModuleTitle(moduleIndex, event) {
      this.modules[moduleIndex].title = event.target.value;
    },

    generateUniqueLessonTitle(baseTitle, existingTitles) {
      let title = baseTitle;
      let counter = 1;
      while (existingTitles.includes(title)) {
        title = `${baseTitle} ${counter}`;
        counter++;
      }
      return title;
    },

    async addLesson(moduleIndex) {
      const module = this.modules[moduleIndex];
      const baseTitle = 'Новая работа';
      const existingTitles = module.lessons ? module.lessons.map((lesson) => lesson.title) : [];
      const uniqueTitle = this.generateUniqueLessonTitle(baseTitle, existingTitles);
      const lessonType = 'ARTICLE'; // Default type

      const formData = new FormData();
      formData.append('title', uniqueTitle);
      formData.append('description', '');
      formData.append('type', lessonType);
      formData.append('duration', '0');
      formData.append('order', module.lessons ? module.lessons.length : 0);

      // Add default image based on type
      const defaultImage = await this.getDefaultImage(lessonType);
      if (defaultImage) {
        formData.append('thumbnail', defaultImage);
      } else {
        formData.append('thumbnail', '');
      }

      try {
        const response = await this.api.post(
          `/courses/${this.courseSlug}/modules/${module.id}/lessons/`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );
        if (!module.lessons) module.lessons = [];
        module.lessons.push(response.data);
        this.modules[moduleIndex] = { ...module };
        this.searchModules();
        console.log('✅ Работа создана:', response.data);
      } catch (error) {
        console.error('❌ Ошибка создания работы:', error);
        const errorMessage = error.response?.data?.title || error.response?.data?.detail || 'Неизвестная ошибка';
        alert('Не удалось создать работу: ' + errorMessage);
      }
    },

    editLesson(moduleIndex, lessonIndex) {
      const module = this.modules[moduleIndex];
      const lesson = module.lessons[lessonIndex];
      this.editingLesson = {
        ...lesson,
        moduleIndex,
        lessonIndex,
      };
      this.editingModuleIndex = moduleIndex;
      this.editingLessonIndex = lessonIndex;
    },

    openArticleEditor(moduleIndex, lessonIndex) {
      const module = this.modules[moduleIndex];
      const lesson = module.lessons[lessonIndex];
      this.router.push({
        name: 'ArticleEditor',
        params: {
          courseSlug: this.courseSlug,
          moduleId: module.id,
          lessonId: lesson.id,
        },
        query: {
          title: lesson.title,
          type: lesson.type.toLowerCase(),
        },
      });
    },

    async deleteLesson(moduleIndex, lessonIndex) {
      const module = this.modules[moduleIndex];
      const lesson = module.lessons[lessonIndex];
      if (!confirm('Вы уверены, что хотите удалить эту работу?')) return;
      try {
        await this.api.delete(
          `/courses/${this.courseSlug}/modules/${module.id}/lessons/${lesson.id}/`
        );
        module.lessons.splice(lessonIndex, 1);
        this.modules[moduleIndex] = { ...module };
        this.searchModules();
        console.log('✅ Работа удалена:', lesson.id);
      } catch (error) {
        console.error('❌ Ошибка удаления работы:', error);
        alert('Не удалось удалить работу: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
      }
    },

    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      if (!file.type.match('image.*')) {
        alert('Пожалуйста, выберите файл изображения');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert('Файл слишком большой. Максимальный размер - 5MB');
        return;
      }
      this.editingLesson.thumbnail = file;
    },

    removeImage() {
      this.editingLesson.thumbnail = '';
    },

    async saveEditedLesson() {
      const { moduleIndex, lessonIndex, ...lessonData } = this.editingLesson;
      const module = this.modules[moduleIndex];
      const formData = new FormData();
      formData.append('title', lessonData.title || 'Новая работа');
      formData.append('description', lessonData.description || '');
      formData.append('type', lessonData.type || 'ARTICLE');
      formData.append('duration', lessonData.duration || 0);
      formData.append('order', lessonData.order || 0);

      // Handle thumbnail
      if (lessonData.thumbnail instanceof File) {
        formData.append('thumbnail', lessonData.thumbnail);
      } else if (lessonData.thumbnail === '' || !lessonData.thumbnail) {
        const defaultImage = await this.getDefaultImage(lessonData.type || 'ARTICLE');
        if (defaultImage) {
          formData.append('thumbnail', defaultImage);
        } else {
          formData.append('thumbnail', '');
        }
      }

      try {
        const response = await this.api.put(
          `/courses/${this.courseSlug}/modules/${module.id}/lessons/${lessonData.id}/`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );
        module.lessons[lessonIndex] = response.data;
        this.modules[moduleIndex] = { ...module };
        this.searchModules();
        this.editingLesson = null;
        console.log('✅ Работа обновлена:', response.data);
        alert('Работа успешно обновлена');
      } catch (error) {
        console.error('❌ Ошибка обновления работы:', error);
        let errorMessage = 'Неизвестная ошибка';
        if (error.response?.data) {
          if (error.response.data.title) {
            errorMessage = error.response.data.title;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else {
            errorMessage = JSON.stringify(error.response.data);
          }
        }
        alert('Не удалось обновить работу: ' + errorMessage);
      }
    },

    cancelEdit() {
      this.editingLesson = null;
      this.editingModuleIndex = null;
      this.editingLessonIndex = null;
    },

    async initialize() {
      console.log('🔍 Начало инициализации CourseEditor');
      if (!this.authStore.isAuthenticated) {
        console.warn('❌ Пользователь не аутентифицирован, перенаправляем на SignIn');
        this.router.push({ name: 'SignIn' });
        return;
      }
      await this.loadModules();
    },
  },

  async mounted() {
    await this.initialize();
  },
};
</script>

<style scoped>
.main-content-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  background: var(--background-color);
  transition: background-color 0.3s ease;
}

.main-content-section {
  box-sizing: border-box;
  width: 100%;
  max-width: 1480px;
  padding: 50px 20px 101px;
  margin: 0 auto;
}

.module-card-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 88px;
  padding: 0 28px 0 29px;
  background: var(--form-background);
  border-radius: 20px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
}

.module-title-container {
  display: flex;
  flex-direction: row;
  gap: 16px;
  align-items: center;
  justify-content: flex-start;
  padding: 16px;
  background: var(--form-background);
  border-radius: 8px;
  transition: background-color 0.3s ease;
  width: 100%;
}

.svg-container {
  width: 24px;
  height: 24px;
  margin-right: 10px;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.search-input {
  width: 100%;
  min-width: 300px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 16px;
  color: var(--text-color);
  background: var(--form-background);
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: var(--secondary-text);
}

.search-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
}

.search-button:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.main-content-container1 {
  box-sizing: border-box;
  width: 100%;
  margin-top: 66px;
}

.module-container4 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  width: 100%;
  margin-bottom: 40px;
  padding: 20px;
  background: var(--form-background);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
}

.save-button-container {
  flex: 0 0 auto;
  align-self: flex-end;
  padding-right: 3px;
  padding-left: 3px;
  display: flex;
  gap: 10px;
}

.save-button {
  box-sizing: border-box;
  display: block;
  width: 137px;
  min-width: 137px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: var(--footer-text);
  cursor: pointer;
  background: var(--accent-color);
  border: none;
  border-radius: 10px;
  transition: all 0.2s;
}

.delete-button {
  box-sizing: border-box;
  display: block;
  width: 100px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: white;
  cursor: pointer;
  background: #ef4444;
  border: none;
  border-radius: 10px;
  transition: all 0.2s;
}

.module-container3 {
  flex: 0 0 auto;
  margin-top: 1px;
}

.module-container2 {
  display: flex;
  margin-left: 100px;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-start;
}

.module-title-input {
  width: 100%;
  padding: 12px;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
  border: none;
  border-bottom: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-color);
  transition: all 0.3s ease;
}

.articles-wrapper {
  display: flex;
  flex-wrap: wrap;
  margin: 100px;
  gap: 20px;
  margin-top: 20px;
}

.article-card {
  width: calc(33.333% - 14px);
  background: var(--background-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.article-thumbnail {
  width: 100%;
  height: 150px;
  object-fit: contain;
  border-radius: 10px;
  object-position: center;
}

.article-content {
  padding: 16px;
}

.article-content h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.article-content p {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.article-meta .lesson-type {
  margin-left: 10px;
}

.article-actions {
  display: flex;
  gap: 5px;
}

.article-actions button {
  background: var(--background-color);
  border: none;
  cursor: pointer;
  padding: 6px;
  margin: 0;
  border-radius: 6px;
  transition: background 0.2s, filter 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.article-actions button:hover {
  background: var(--hover-background);
  filter: brightness(1.1);
}

.article-actions button img {
  width: 20px;
  height: 20px;
  filter: var(--icon-filter, none);
  transition: filter 0.2s;
}

.add-article-card {
  width: calc(33.333% - 14px);
  background: var(--background-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 350px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: all 0.3s ease;
  box-sizing: border-box;
  overflow: hidden;
}

.add-article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.add-article-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.add-module-btn {
  cursor: pointer;
  color: var(--accent-color);
  text-align: center;
  padding: 10px;
  border: 2px dashed var(--accent-color);
  border-radius: 10px;
  margin-top: 40px;
  transition: all 0.3s ease;
  font: 400 16px Raleway, sans-serif;
}

.add-module-btn:hover {
  background: var(--hover-background);
  color: var(--accent-color);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--accent-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.2);
}

/* Remove spinner arrows from number inputs */
.form-group input[type="number"] {
  -moz-appearance: textfield;
}

.form-group input[type="number"]::-webkit-outer-spin-button,
.form-group input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-group select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: var(--background-color);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="6" viewBox="0 0 12 6"><path fill="%23A094B8" d="M0 0l6 6 6-6z"/></svg>');
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
  padding-right: 30px;
  cursor: pointer;
}

.form-group select:focus {
  border-color: var(--accent-color);
}

.fixed-textarea {
  resize: none;
  width: 100%;
  height: 100px;
  line-height: 1.5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--form-background);
  padding: 28px;
  border-radius: 16px;
  width: 500px;
  max-width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-sizing: border-box;
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

/* Add custom scrollbar for the modal */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: var(--background-color);
  border-radius: 8px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 8px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

/* Special styling for the title input in the modal */
.form-group input[name="title"],
.form-group input[placeholder="Введите название"] {
  font-size: 16px;
  font-weight: 500;
  padding: 12px 16px;
  border-width: 2px;
  background-color: var(--background-color);
  color: var(--text-color);
  border-color: var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.form-group input[name="title"]:focus,
.form-group input[placeholder="Введите название"]:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(160, 148, 184, 0.25);
  outline: none;
}

/* Improve dark theme support for all inputs */
.form-group input,
.form-group textarea,
.form-group select {
  background-color: var(--background-color);
  color: var(--text-color);
  border-color: var(--border-color);
}

.modal-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.save-btn {
  padding: 10px 20px;
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.save-btn:hover {
  background: var(--hover-accent);
  transform: translateY(-1px);
}

.cancel-btn {
  padding: 10px 20px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cancel-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.image-upload-container {
  margin-top: 10px;
}

.image-upload-label {
  display: inline-block;
  padding: 10px 20px;
  background: var(--accent-color);
  color: var(--footer-text);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-upload-label:hover {
  background: var(--hover-accent);
  transform: translateY(-1px);
}

.image-upload-input {
  display: none;
}

.image-preview {
  position: relative;
  margin-top: 15px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  display: block;
}

.remove-image-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
}

.remove-image-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}

:root {
  --icon-filter: none;
}

.dark-theme .article-actions button img {
  filter: brightness(0.85) invert(0.85);
}

.title-input {
  font-size: 16px !important;
  font-weight: 500 !important;
  padding: 14px 16px !important;
  border-width: 2px !important;
  border-radius: 10px !important;
  transition: all 0.3s ease !important;
  background-color: var(--background-color) !important;
  color: var(--text-color) !important;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important;
}

.title-input:focus {
  border-color: var(--accent-color) !important;
  box-shadow: 0 0 0 3px rgba(160, 148, 184, 0.3) !important;
  transform: translateY(-1px) !important;
}

/* Dark theme specific adjustments */
.dark-theme .title-input {
  background-color: var(--form-background) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .title-input:focus {
  background-color: var(--background-color) !important;
}
</style>