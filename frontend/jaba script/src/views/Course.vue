<template>
  <div>
    <div class="main-content-container">
      <div class="main-content-section">
        <div class="module-card-container">
          <div class="module-title-container">
            <div class="svg-container">
              <svg viewBox="0 0 24 24" x="0" y="0" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g id="Group 65" xmlns="http://www.w3.org/2000/svg">
                  <circle id="Ellipse 7" cx="11" cy="9.5" r="8" stroke="#575667" />
                  <line id="Line 12" x1="15.879999999999995" y1="15.675000000000011" x2="21.879999999999995" y2="22.67500000000001" stroke="#575667" />
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
          <input v-model="editingLesson.title" placeholder="Введите название" />
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
  align-items: center;
  justify-content: flex-start;
  width: 1480px;
  max-width: 1480px;
  margin: 0 auto;
  overflow-x: hidden;
}

.main-content-section {
  box-sizing: border-box;
  width: 100%;
  max-width: 1480px;
  padding: 50px 20px 101px;
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
  background: #ebefef;
  border-radius: 20px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
}

.module-title-container {
  box-sizing: border-box;
  display: flex;
  flex: 1;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  height: 43px;
  padding: 0 8.5px;
  background: #f5f9f8;
  border: 1px solid #c5c8cc;
  border-radius: 20px;
}

.svg-container {
  display: flex;
  flex: 0 0 auto;
  width: 24px;
  height: 24px;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
  margin-left: 13.5px;
}

.search-button {
  box-sizing: border-box;
  display: block;
  flex: 0 0 auto;
  width: 111px;
  min-width: 111px;
  height: 40px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 20px;
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
  color: #24222f;
  cursor: pointer;
  background: #cff6c3;
  border: none;
  border-radius: 10px;
}

.delete-button {
  box-sizing: border-box;
  display: block;
  width: 100px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #fff;
  cursor: pointer;
  background: #ff6b6b;
  border: none;
  border-radius: 10px;
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
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
  font: 400 24px Raleway, sans-serif;
  color: #24222f;
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
  background: #ebefef;
  border-radius: 20px;
  padding: 20px;
  position: relative;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  min-height: 350px;
  box-sizing: border-box;
  cursor: pointer;
}

.article-thumbnail {
  width: 100%;
  height: 150px;
  object-fit: contain;
  border-radius: 10px;
  object-position: center;
}

.article-content {
  margin-top: 15px;
}

.article-content h3 {
  margin: 0;
  padding: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}

.article-content p {
  margin: 7px 0 0 0;
  padding: 0;
  font: 300 14px Raleway, sans-serif;
  color: #575667;
  height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 7px;
  font: 400 12px Raleway, sans-serif;
  color: #a094b8;
}

.article-meta .lesson-type {
  margin-left: 10px;
}

.article-actions {
  display: flex;
  gap: 5px;
}

.article-actions button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin: 0;
}

.article-actions button img {
  width: 20px;
  height: 20px;
}

.add-article-card {
  width: calc(33.333% - 14px);
  background: #ebefef;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 350px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  padding: 20px;
  transition: background 0.3s;
  box-sizing: border-box;
}

.add-article-card:hover {
  background: #dde3e2;
}

.add-article-image {
  width: 55px;
  height: 55px;
  object-fit: contain;
}

.add-module-btn {
  cursor: pointer;
  color: #a094b8;
  text-align: center;
  padding: 10px;
  border: 2px dashed #a094b8;
  border-radius: 10px;
  margin-top: 40px;
  transition: background 0.3s;
  font: 400 16px Raleway, sans-serif;
}

.add-module-btn:hover {
  background: #ebefef;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-group select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5" viewBox="0 0 10 5"><path fill="%23575667" d="M0 0l5 5 5-5H0z"/></svg>') no-repeat right 10px center;
  background-size: 10px;
}

.fixed-textarea {
  resize: none;
  width: 100%;
  height: 100px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-sizing: border-box;
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.save-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.image-upload-container {
  margin-top: 10px;
}

.image-upload-label {
  display: inline-block;
  padding: 8px 16px;
  background: #2196F3;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.image-upload-input {
  display: none;
}

.image-preview {
  position: relative;
  margin-top: 10px;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
</style>