<template>
  <div class="course-editor-container">
    <!-- Поиск и создание курса -->
    <div class="search-section">
      <div class="search-container">
        <div class="svg-container">
          <svg viewBox="0 0 24 24" x="0" y="0" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g id="Group 65">
              <circle id="Ellipse 7" cx="11" cy="9.5" r="8" stroke="currentColor" />
              <line id="Line 12" x1="15.88" y1="15.68" x2="21.88" y2="22.68" stroke="currentColor" />
            </g>
          </svg>
        </div>
        <input
          v-model="searchQuery"
          class="search-input"
          placeholder="Название курса или ID"
        />
      </div>
      <button class="search-button">Искать</button>
    </div>

    <!-- Список курсов -->
    <div class="courses-list">
      <div v-if="isLoading" class="loading">Загрузка...</div>
      <div v-else>
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="course-item"
        >
          <div class="course-info">
            <div class="course-image" v-if="course.thumbnail">
              <img :src="getImageUrl(course.thumbnail)" alt="Course Thumbnail" />
            </div>
            <div class="course-details">
              <router-link
                :to="{ name: 'CourseDetail', params: { slug: course.slug }}"
                class="course-title"
              >
                {{ course.title }}
              </router-link>
              <div class="course-meta">
                <span>{{ course.id }}</span>
              </div>
              <div class="course-description" v-if="course.description">
                {{ course.description }}
              </div>
            </div>
          </div>
          <div class="course-actions">
            <button class="edit-btn" @click="openEditCourseModal(course)">
              Редактировать
            </button>
            <button class="delete-btn" @click="confirmDeleteCourse(course)">
              Удалить
            </button>
            <button class="continue-btn" @click="goToCourseDetail(course.slug)">
              Продолжить
            </button>
          </div>
        </div>
        <div v-if="!filteredCourses.length" class="no-courses">
          Нет доступных курсов
        </div>
      </div>
    </div>

    <!-- Кнопка создания курса -->
    <button class="create-course-btn" @click="openCreateCourseModal">
      + Создать курс
    </button>

    <!-- Модальное окно для создания курса -->
    <div v-if="showCreateCourseModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Создание курса</h3>
        
        <div class="form-group">
          <label>Название курса</label>
          <input v-model="newCourseForm.title" type="text" class="form-control" placeholder="Введите название курса">
        </div>
        
        <div class="form-group">
          <label>Описание курса</label>
          <textarea v-model="newCourseForm.description" class="form-control fixed-textarea" placeholder="Введите описание курса"></textarea>
        </div>
        
        <div class="form-group">
          <label>Опубликован</label>
          <select v-model="newCourseForm.is_published" class="form-control">
            <option :value="true">Да</option>
            <option :value="false">Нет</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Изображение курса</label>
          <div class="image-upload-container">
            <label for="create-course-image-upload" class="image-upload-label">
              <span v-if="!newCourseForm.thumbnail">Выберите изображение</span>
              <span v-else>Изменить изображение</span>
              <input 
                id="create-course-image-upload" 
                type="file" 
                accept="image/*" 
                @change="handleCreateCourseImageUpload"
                class="image-upload-input"
              />
            </label>
            <div v-if="newCourseForm.thumbnail" class="image-preview">
              <img :src="getImageUrl(newCourseForm.thumbnail)" class="preview-image" />
              <button @click="removeCreateCourseImage" class="remove-image-btn">×</button>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="createNewCourse" class="save-btn">Сохранить</button>
          <button @click="cancelCreateCourse" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для редактирования курса -->
    <div v-if="showEditCourseModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Редактирование курса</h3>
        
        <div class="form-group">
          <label>Название курса</label>
          <input v-model="editCourseForm.title" type="text" class="form-control" placeholder="Введите название курса">
        </div>
        
        <div class="form-group">
          <label>Описание курса</label>
          <textarea v-model="editCourseForm.description" class="form-control fixed-textarea" placeholder="Введите описание курса"></textarea>
        </div>
        
        <div class="form-group">
          <label>Опубликован</label>
          <select v-model="editCourseForm.is_published" class="form-control">
            <option :value="true">Да</option>
            <option :value="false">Нет</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Изображение курса</label>
          <div class="image-upload-container">
            <label for="edit-course-image-upload" class="image-upload-label">
              <span v-if="!editCourseForm.thumbnail && !editCourseForm.thumbnailPreview">Выберите изображение</span>
              <span v-else>Изменить изображение</span>
              <input 
                id="edit-course-image-upload" 
                type="file" 
                accept="image/*" 
                @change="handleEditCourseImageUpload"
                class="image-upload-input"
              />
            </label>
            <div v-if="editCourseForm.thumbnail || editCourseForm.thumbnailPreview" class="image-preview">
              <img :src="editCourseForm.thumbnailPreview || getImageUrl(editCourseForm.thumbnail)" class="preview-image" />
              <button @click="removeEditCourseImage" class="remove-image-btn">×</button>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="updateCourse" class="save-btn">Сохранить</button>
          <button @click="confirmDeleteCourse(editCourseForm)" class="delete-btn">Удалить</button>
          <button @click="cancelEditCourse" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';

export default {
  name: 'CourseEditor',

  setup() {
    const router = useRouter();
    const authStore = useRefreshStore();

    const api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Create cache helper functions
    const cache = {
      // Get data from cache
      get: (key) => {
        try {
          const cachedData = localStorage.getItem(`cache_${key}`);
          if (!cachedData) return null;
          
          const { data, expiry } = JSON.parse(cachedData);
          
          // Check if cache has expired
          if (expiry < Date.now()) {
            localStorage.removeItem(`cache_${key}`);
            return null;
          }
          
          return data;
        } catch (error) {
          console.error('Error reading from cache:', error);
          return null;
        }
      },
      
      // Set data in cache with expiry time (default 5 minutes)
      set: (key, data, expiryMinutes = 5) => {
        try {
          const expiry = Date.now() + (expiryMinutes * 60 * 1000);
          localStorage.setItem(`cache_${key}`, JSON.stringify({ data, expiry }));
        } catch (error) {
          console.error('Error setting cache:', error);
        }
      },
      
      // Remove item from cache
      remove: (key) => {
        try {
          localStorage.removeItem(`cache_${key}`);
        } catch (error) {
          console.error('Error removing from cache:', error);
        }
      },
      
      // Clear entire cache
      clear: () => {
        try {
          Object.keys(localStorage)
            .filter(key => key.startsWith('cache_'))
            .forEach(key => localStorage.removeItem(key));
        } catch (error) {
          console.error('Error clearing cache:', error);
        }
      }
    };

    api.interceptors.request.use(
      (config) => {
        const token = authStore.accessToken || localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Check cache for GET requests
        if (config.method?.toLowerCase() === 'get' && !config.skipCache) {
          const cacheKey = `${config.url}_${JSON.stringify(config.params || {})}`;
          const cachedData = cache.get(cacheKey);
          
          if (cachedData) {
            // Return a dummy promise that resolves with cached data
            config.adapter = () => {
              return Promise.resolve({
                data: cachedData,
                status: 200,
                statusText: 'OK',
                headers: {},
                config,
                request: {}
              });
            };
          }
        }
        
        return config;
      },
      (error) => Promise.reject(error)
    );

    api.interceptors.response.use(
      (response) => {
        // Cache successful GET responses
        if (response.config.method?.toLowerCase() === 'get' && !response.config.skipCache) {
          const cacheKey = `${response.config.url}_${JSON.stringify(response.config.params || {})}`;
          cache.set(cacheKey, response.data);
        }
        return response;
      },
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            await authStore.refreshToken();
            originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
            return api(originalRequest);
          } catch (refreshError) {
            console.error('❌ Не удалось обновить токен в интерцепторе:', refreshError);
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
      api,
      authStore,
      cache
    };
  },

  data() {
    return {
      searchQuery: '',
      courses: [],
      showCreateCourseModal: false,
      newCourseForm: {
        title: '',
        description: '',
        is_published: false,
        thumbnail: null,
      },
      showEditCourseModal: false,
      editCourseForm: {
        slug: '',
        title: '',
        description: '',
        is_published: false,
        thumbnail: null,
        thumbnailPreview: null,
      },
      isLoading: false,
    };
  },

  computed: {
    filteredCourses() {
      if (!this.searchQuery.trim()) return this.courses;
      const query = this.searchQuery.toLowerCase().trim();
      return this.courses.filter(
        (course) =>
          course.title?.toLowerCase().includes(query) ||
          course.id?.toString().includes(query)
      );
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

    async loadCourses() {
      this.isLoading = true;
      try {
        const response = await this.api.get('/courses/');
        this.courses = Array.isArray(response.data) ? response.data : [];
      } catch (error) {
        console.error('Ошибка загрузки курсов:', error);
        this.courses = [];
        if (error.response?.status === 401) {
          this.authStore.logout();
          this.router.push({ name: 'SignIn' });
        }
      } finally {
        this.isLoading = false;
      }
    },

    goToCourseDetail(slug) {
      this.router.push({ name: 'CourseDetail', params: { slug } });
    },

    // Создание курса
    openCreateCourseModal() {
      this.resetNewCourseForm();
      this.showCreateCourseModal = true;
    },

    cancelCreateCourse() {
      this.showCreateCourseModal = false;
      this.resetNewCourseForm();
    },

    resetNewCourseForm() {
      this.newCourseForm = {
        title: '',
        description: '',
        is_published: false,
        thumbnail: null,
      };
    },

    handleCreateCourseImageUpload(event) {
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

      this.newCourseForm.thumbnail = file;
    },

    removeCreateCourseImage() {
      this.newCourseForm.thumbnail = null;
    },

    async createNewCourse() {
      try {
        const formData = new FormData();
        formData.append('title', this.newCourseForm.title || 'Новый курс');
        formData.append('description', this.newCourseForm.description);
        formData.append('is_published', this.newCourseForm.is_published);

        if (this.newCourseForm.thumbnail instanceof File) {
          formData.append('thumbnail', this.newCourseForm.thumbnail);
        }

        const response = await this.api.post('/courses/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Invalidate courses cache after creating a new course
        this.cache.remove('cache_/courses/_{}');
        
        this.courses.push(response.data);
        this.showCreateCourseModal = false;
        this.resetNewCourseForm();
      } catch (error) {
        console.error('Ошибка создания курса:', error);
        alert('Не удалось создать новый курс: ' + (error.message || 'Неизвестная ошибка'));
        if (error.response?.status === 401) {
          this.authStore.logout();
          this.router.push({ name: 'SignIn' });
        }
      }
    },

    // Редактирование курса
    openEditCourseModal(course) {
      this.editCourseForm = {
        slug: course.slug,
        title: course.title,
        description: course.description,
        is_published: course.is_published,
        thumbnail: course.thumbnail,
        thumbnailPreview: null,
      };
      this.showEditCourseModal = true;
    },

    cancelEditCourse() {
      this.showEditCourseModal = false;
      this.resetEditCourseForm();
    },

    resetEditCourseForm() {
      this.editCourseForm = {
        slug: '',
        title: '',
        description: '',
        is_published: false,
        thumbnail: null,
        thumbnailPreview: null,
      };
    },

    handleEditCourseImageUpload(event) {
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

      this.editCourseForm.thumbnail = file;
      this.editCourseForm.thumbnailPreview = URL.createObjectURL(file);
    },

    removeEditCourseImage() {
      this.editCourseForm.thumbnail = '';
      this.editCourseForm.thumbnailPreview = null;
    },

    async updateCourse() {
      try {
        const formData = new FormData();
        formData.append('title', this.editCourseForm.title);
        formData.append('description', this.editCourseForm.description);
        formData.append('is_published', this.editCourseForm.is_published);

        // Only include thumbnail if it's a File or explicitly cleared
        if (this.editCourseForm.thumbnail instanceof File) {
          formData.append('thumbnail', this.editCourseForm.thumbnail);
        } else if (this.editCourseForm.thumbnail === '') {
          formData.append('thumbnail', '');
        }

        const response = await this.api.patch(`/courses/${this.editCourseForm.slug}/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Invalidate course cache after updating
        this.cache.remove(`cache_/courses/${this.editCourseForm.slug}/_{}`)
        // Also invalidate courses list
        this.cache.remove('cache_/courses/_{}');

        const index = this.courses.findIndex(course => course.slug === this.editCourseForm.slug);
        if (index !== -1) {
          this.courses[index] = response.data;
        }

        this.showEditCourseModal = false;
        this.resetEditCourseForm();
      } catch (error) {
        console.error('Ошибка обновления курса:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
        }
        alert('Не удалось обновить курс: ' + (error.message || 'Неизвестная ошибка'));
        if (error.response?.status === 401) {
          this.authStore.logout();
          this.router.push({ name: 'SignIn' });
        }
      }
    },

    // Удаление курса
    confirmDeleteCourse(course) {
      if (confirm(`Вы уверены, что хотите удалить курс "${course.title}"?`)) {
        this.deleteCourse(course);
      }
    },

    async deleteCourse(course) {
      try {
        await this.api.delete(`/courses/${course.slug}/`);
        
        // Invalidate cache after deleting
        this.cache.remove(`cache_/courses/${course.slug}/_{}`)
        // Also invalidate courses list
        this.cache.remove('cache_/courses/_{}');
        
        this.courses = this.courses.filter(c => c.slug !== course.slug);
        this.showEditCourseModal = false;
        this.resetEditCourseForm();
      } catch (error) {
        console.error('Ошибка удаления курса:', error);
        alert('Не удалось удалить курс: ' + (error.message || 'Неизвестная ошибка'));
        if (error.response?.status === 401) {
          this.authStore.logout();
          this.router.push({ name: 'SignIn' });
        }
      }
    },

    async initialize() {
      console.log('🔍 Начало инициализации: Проверка состояния авторизации');
      console.log('Текущий accessToken:', this.authStore.accessToken);
      console.log('Текущий refreshToken:', this.authStore.refreshToken);
      console.log('isAuthenticated:', this.authStore.isAuthenticated);

      if (typeof this.authStore.ready === 'function') {
        try {
          await this.authStore.ready();
          console.log('✅ Токен инициализирован, isAuthenticated:', this.authStore.isAuthenticated);
        } catch (error) {
          console.error('❌ Ошибка при инициализации токена:', error);
        }
      } else {
        console.warn('Метод ready отсутствует в authStore, пропускаем инициализацию токена');
        if (!this.authStore.accessToken) {
          console.warn('❌ Access token отсутствует, перенаправляем на SignIn');
          this.authStore.logout();
          this.router.push({ name: 'SignIn' });
          return;
        }
      }

      if (!this.authStore.isAuthenticated) {
        console.warn('❌ Пользователь не аутентифицирован, перенаправляем на SignIn');
        this.router.push({ name: 'SignIn' });
        return;
      }

      console.log('✅ Пользователь аутентифицирован, загружаем курсы');
      await this.loadCourses();
    },
  },

  async mounted() {
    await this.initialize();
  },
};
</script>

<style scoped>
.course-editor-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: var(--background-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Поиск */
.search-section {
  display: flex;
  gap: 15px;
}

.search-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  background-color: var(--form-background);
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  padding: 0 15px;
  transition: background-color 0.3s ease;
}

.svg-container {
  width: 24px;
  height: 24px;
  margin-right: 10px;
  color: var(--secondary-text);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 15px 0;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  width: 100%;
  outline: none;
  transition: color 0.3s ease;
}

.search-input::placeholder {
  color: var(--secondary-text);
}

.search-button {
  display: block;
  width: 137px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: var(--footer-text);
  cursor: pointer;
  background: var(--accent-color);
  border: none;
  border-radius: 10px;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background: var(--hover-accent);
}

/* Список курсов */
.courses-list {
  margin-top: 40px;
}

.course-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 20px;
  background-color: var(--form-background);
  border-radius: 20px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, background-color 0.3s ease;
}

.course-item:hover {
  transform: translateY(-5px);
}

.course-info {
  display: flex;
  gap: 20px;
  flex: 1;
}

.course-image {
  width: 100px;
  height: 100px;
  border-radius: 10px;
  overflow: hidden;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-details {
  flex: 1;
}

.course-title {
  display: block;
  margin-bottom: 5px;
  font: 600 18px Raleway, sans-serif;
  color: var(--text-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.course-title:hover {
  color: var(--accent-color);
}

.course-meta {
  margin-bottom: 10px;
  font: 400 14px Raleway, sans-serif;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.course-description {
  font: 400 14px Raleway, sans-serif;
  color: var(--secondary-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.3s ease;
}

.course-actions {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
}

.edit-btn, .continue-btn {
  padding: 8px 15px;
  font: 400 14px Raleway, sans-serif;
  color: var(--footer-text);
  cursor: pointer;
  background: var(--accent-color);
  border: none;
  border-radius: 10px;
  transition: background-color 0.3s ease;
}

.edit-btn:hover, .continue-btn:hover {
  background: var(--hover-accent);
}

.delete-btn {
  padding: 8px 15px;
  font: 400 14px Raleway, sans-serif;
  color: white;
  cursor: pointer;
  background: var(--error-color);
  border: none;
  border-radius: 10px;
  transition: background-color 0.3s ease;
}

.delete-btn:hover {
  background: var(--hover-delete);
}

.no-courses {
  text-align: center;
  padding: 40px;
  font: 400 18px Raleway, sans-serif;
  color: var(--secondary-text);
  background-color: var(--form-background);
  border-radius: 20px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Кнопка создания курса */
.create-course-btn {
  display: block;
  width: 200px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: var(--footer-text);
  cursor: pointer;
  background: var(--accent-color);
  border: none;
  border-radius: 20px;
  margin-top: 40px;
  transition: background-color 0.3s ease;
}

.create-course-btn:hover {
  background: var(--hover-accent);
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: background-color 0.3s ease;
}

.modal-content {
  background-color: var(--form-background);
  color: var(--text-color);
  padding: 25px;
  border-radius: 10px;
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.modal-content h3 {
  margin: 0 0 20px;
  font: 400 20px Raleway, sans-serif;
  color: var(--text-color);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font: 500 14px Raleway, sans-serif;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font: 400 14px Raleway, sans-serif;
  color: var(--text-color);
  box-sizing: border-box;
  background-color: var(--background-color);
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 5px rgba(160, 148, 184, 0.2);
}

.form-control::placeholder {
  color: var(--secondary-text);
}

.fixed-textarea {
  resize: none;
  height: 100px;
}

.form-group select {
  appearance: none;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5" viewBox="0 0 10 5"><path fill="%23575667" d="M0 0l5 5 5-5H0z"/></svg>') no-repeat right 10px center;
  background-size: 10px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.save-btn {
  display: block;
  width: 137px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  cursor: pointer;
  background: var(--accent-color);
  border: none;
  border-radius: 10px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.save-btn:hover {
  background: var(--hover-accent);
}

.cancel-btn {
  display: block;
  width: 100px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: var(--footer-text);
  cursor: pointer;
  background: var(--error-color);
  border: none;
  border-radius: 10px;
  transition: background-color 0.3s ease;
}

.cancel-btn:hover {
  background: var(--hover-delete);
}

/* Стили для загрузки изображений */
.image-upload-container {
  margin-top: 10px;
}

.image-upload-label {
  display: inline-block;
  padding: 8px 16px;
  font: 400 14px Raleway, sans-serif;
  color: var(--text-color);
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

.image-upload-label:hover {
  background-color: var(--hover-background);
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
  border: 1px solid #c5c8cc;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: #ff6b6b;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
}

.remove-image-btn:hover {
  background: #e55a5a;
}

/* Стиль для состояния загрузки */
.loading {
  text-align: center;
  padding: 20px;
  font: 400 16px Raleway, sans-serif;
  color: var(--secondary-text);
  background: var(--form-background);
  border-radius: 20px;
  transition: background-color 0.3s ease, color 0.3s ease;
}
</style>
```