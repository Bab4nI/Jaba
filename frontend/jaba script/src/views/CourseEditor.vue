```vue
<template>
  <div class="course-editor-container">
    <!-- Поиск и создание курса -->
    <div class="search-section">
      <div class="search-container">
        <div class="svg-container">
          <svg viewBox="0 0 24 24" x="0" y="0" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g id="Group 65">
              <circle id="Ellipse 7" cx="11" cy="9.5" r="8" stroke="#575667" />
              <line id="Line 12" x1="15.88" y1="15.68" x2="21.88" y2="22.68" stroke="#575667" />
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
import { jwtDecode } from 'jwt-decode';

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
        const token = this.authStore.accessToken || localStorage.getItem('access_token');
        if (!token) {
          throw new Error('Токен авторизации не найден');
        }
        const decodedToken = jwtDecode(token);
        const authorId = decodedToken.user_id;

        const formData = new FormData();
        formData.append('title', this.newCourseForm.title || 'Новый курс');
        formData.append('description', this.newCourseForm.description);
        formData.append('author', authorId);
        formData.append('is_published', this.newCourseForm.is_published);

        if (this.newCourseForm.thumbnail instanceof File) {
          formData.append('thumbnail', this.newCourseForm.thumbnail);
        }

        const response = await this.api.post('/courses/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

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
        // If thumbnail is a URL (unchanged), do not include it

        console.log('FormData:', Object.fromEntries(formData)); // Debug log

        const response = await this.api.patch(`/courses/${this.editCourseForm.slug}/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

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
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 1480px;
  max-width: 1480px;
  margin: 0 auto;
  padding: 50px 20px 100px;
  font-family: 'Raleway', sans-serif;
  overflow-x: hidden;
}

/* Поиск */
.search-section {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  margin-bottom: 40px;
}

.search-container {
  display: flex;
  align-items: center;
  flex-grow: 1;
  height: 44px;
  padding: 0 15px;
  background: #f5f9f8;
  border: 1px solid #c5c8cc;
  border-radius: 20px;
}

.svg-container {
  display: flex;
  flex: 0 0 auto;
  width: 24px;
  height: 24px;
  margin-right: 10px;
}

.svg-container svg {
  width: 100%;
  height: 100%;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
}

.search-button {
  display: block;
  width: 111px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 20px;
}

.search-button:hover {
  background: #8c84a8;
}

/* Список курсов */
.courses-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  margin-top: 20px;
}

.course-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  background: #ebefef;
  border-radius: 20px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  transition: background 0.3s;
}

.course-item:hover {
  background: #dde3e2;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-grow: 1;
}

.course-image img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #c5c8cc;
}

.course-details {
  flex-grow: 1;
}

.course-title {
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
  text-decoration: none;
}

.course-title:hover {
  text-decoration: underline;
}

.course-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 7px;
}

.course-meta span {
  font: 400 12px Raleway, sans-serif;
  color: #a094b8;
  background: #f5f9f8;
  padding: 2px 10px;
  border-radius: 12px;
}

.course-description {
  font: 300 14px Raleway, sans-serif;
  color: #575667;
  margin-top: 10px;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.course-actions {
  display: flex;
  gap: 10px;
}

.edit-btn {
  display: block;
  width: 137px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  cursor: pointer;
  background: #cff6c3;
  border: none;
  border-radius: 10px;
}

.edit-btn:hover {
  background: #b8e0a8;
}

.delete-btn {
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

.delete-btn:hover {
  background: #e55a5a;
}

.continue-btn {
  display: block;
  width: 137px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 10px;
}

.continue-btn:hover {
  background: #8c84a8;
}

.no-courses {
  text-align: center;
  font: 400 16px Raleway, sans-serif;
  color: #575667;
  padding: 20px;
  background: #f5f9f8;
  border-radius: 20px;
}

.create-course-btn {
  display: block;
  width: 200px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 20px;
  margin-top: 40px;
}

.create-course-btn:hover {
  background: #8c84a8;
}

/* Модальное окно */
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
  background: #fff;
  padding: 25px;
  border-radius: 10px;
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
}

.modal-content h3 {
  margin: 0 0 20px;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font: 500 14px Raleway, sans-serif;
  color: #575667;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #c5c8cc;
  border-radius: 4px;
  font: 400 14px Raleway, sans-serif;
  color: #24222f;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #a094b8;
  box-shadow: 0 0 5px rgba(160, 148, 184, 0.2);
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
  color: #24222f;
  cursor: pointer;
  background: #cff6c3;
  border: none;
  border-radius: 10px;
}

.save-btn:hover {
  background: #b8e0a8;
}

.cancel-btn {
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

.cancel-btn:hover {
  background: #e55a5a;
}

/* Стили для загрузки изображений */
.image-upload-container {
  margin-top: 10px;
}

.image-upload-label {
  display: inline-block;
  padding: 8px 16px;
  font: 400 14px Raleway, sans-serif;
  color: #f5f9f8;
  background: #a094b8;
  border-radius: 4px;
  cursor: pointer;
}

.image-upload-label:hover {
  background: #8c84a8;
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
  color: #575667;
  background: #f5f9f8;
  border-radius: 20px;
}
</style>
```