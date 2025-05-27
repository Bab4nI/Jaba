<template>
  <div class="course-editor-container">
    <!-- Кнопка редактирования -->
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
      <button v-if="userRole === 'admin'" class="edit-toggle-btn" @click="toggleEditMode">
        {{ isEditMode ? 'Завершить редактирование' : 'Редактировать' }}
      </button>
    </div>

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
                <span class="publication-status" :class="{'published': course.is_published, 'unpublished': !course.is_published}">
                  {{ course.is_published ? 'Опубликован' : 'Не опубликован' }}
                </span>
              </div>
              <div class="course-description" v-if="course.description">
                {{ course.description }}
              </div>
            </div>
          </div>
          <div class="course-actions">
            <button v-if="isEditMode" class="edit-btn" @click="openEditCourseModal(course)">
              Редактировать
            </button>
            <button v-if="isEditMode" class="delete-btn" @click="confirmDeleteCourse(course)">
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
    <button v-if="isEditMode" class="create-course-btn" @click="openCreateCourseModal">
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

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const authStore = useRefreshStore();
const userStore = useUserStore();
const userRole = computed(() => {
  const role = userStore.role;
  console.log('Current user role in Sidebar:', role);
  return role;
});

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
    if (config.url && !config.url.endsWith('/') && !config.url.includes('?')) {
      config.url = `${config.url}/`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => {
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
        authStore.logout();
        router.push({ name: 'SignIn' });
        return Promise.reject(refreshError);
      }
    }
    if (error.response?.status === 404 && originalRequest.method === 'delete') {
      const url = originalRequest.url;
      const newUrl = url.endsWith('/') ? url.slice(0, -1) : `${url}/`;
      try {
        const retryConfig = { ...originalRequest, url: newUrl };
        return await api(retryConfig);
      } catch (retryError) {
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

const searchQuery = ref('');
const courses = ref([]);
const showCreateCourseModal = ref(false);
const showEditCourseModal = ref(false);
const isLoading = ref(false);
const isEditMode = ref(false);

const newCourseForm = ref({
  title: '',
  description: '',
  is_published: false,
  thumbnail: null,
});

const editCourseForm = ref({
  slug: '',
  title: '',
  description: '',
  is_published: false,
  thumbnail: null,
  thumbnailPreview: null,
});

const filteredCourses = computed(() => {
  let filtered = courses.value;
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    filtered = filtered.filter(
      (course) =>
        course.title?.toLowerCase().includes(query) ||
        course.id?.toString().includes(query)
    );
  }
  if (userStore.role === 'student') {
    filtered = filtered.filter(course => course.is_published);
  }
  return filtered;
});

const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  if (typeof imagePath === 'object') {
    return URL.createObjectURL(imagePath);
  }
  if (imagePath.startsWith('http')) return imagePath;
  return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${imagePath}`;
};

const loadCourses = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('/courses/', {
      skipCache: true,
      params: { _t: new Date().getTime() }
    });
    if (Array.isArray(response.data)) {
      courses.value = response.data;
    } else {
      courses.value = [];
    }
  } catch (error) {
    courses.value = [];
    if (error.response?.status === 401) {
      authStore.logout();
      router.push({ name: 'SignIn' });
    }
  } finally {
    isLoading.value = false;
  }
};

const goToCourseDetail = (slug) => {
  router.push({ name: 'CourseDetail', params: { slug } });
};

const openCreateCourseModal = () => {
  resetNewCourseForm();
  showCreateCourseModal.value = true;
};
const cancelCreateCourse = () => {
  showCreateCourseModal.value = false;
  resetNewCourseForm();
};
const resetNewCourseForm = () => {
  newCourseForm.value = {
    title: '',
    description: '',
    is_published: false,
    thumbnail: null,
  };
};
const handleCreateCourseImageUpload = (event) => {
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
  newCourseForm.value.thumbnail = file;
};
const removeCreateCourseImage = () => {
  newCourseForm.value.thumbnail = null;
};
const createNewCourse = async () => {
  try {
    const formData = new FormData();
    formData.append('title', newCourseForm.value.title || 'Новый курс');
    if (newCourseForm.value.description && newCourseForm.value.description.trim() !== '') {
      formData.append('description', newCourseForm.value.description);
    }
    formData.append('is_published', newCourseForm.value.is_published);
    if (newCourseForm.value.thumbnail instanceof File) {
      formData.append('thumbnail', newCourseForm.value.thumbnail);
    }
    const response = await api.post('/courses/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    courses.value.push(response.data);
    showCreateCourseModal.value = false;
    resetNewCourseForm();
  } catch (error) {
    let errorMessage = 'Неизвестная ошибка';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    alert('Не удалось создать новый курс: ' + errorMessage);
    if (error.response?.status === 401) {
      authStore.logout();
      router.push({ name: 'SignIn' });
    }
  }
};
const openEditCourseModal = (course) => {
  editCourseForm.value = {
    slug: course.slug,
    title: course.title,
    description: course.description,
    is_published: course.is_published,
    thumbnail: course.thumbnail,
    thumbnailPreview: null,
  };
  showEditCourseModal.value = true;
};
const cancelEditCourse = () => {
  showEditCourseModal.value = false;
  resetEditCourseForm();
};
const resetEditCourseForm = () => {
  editCourseForm.value = {
    slug: '',
    title: '',
    description: '',
    is_published: false,
    thumbnail: null,
    thumbnailPreview: null,
  };
};
const handleEditCourseImageUpload = (event) => {
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
  editCourseForm.value.thumbnail = file;
  editCourseForm.value.thumbnailPreview = URL.createObjectURL(file);
};
const removeEditCourseImage = () => {
  editCourseForm.value.thumbnail = '';
  editCourseForm.value.thumbnailPreview = null;
};
const updateCourse = async () => {
  try {
    const formData = new FormData();
    formData.append('title', editCourseForm.value.title || 'Без названия');
    formData.append('description', editCourseForm.value.description || '');
    formData.append('is_published', editCourseForm.value.is_published);
    if (editCourseForm.value.thumbnail instanceof File) {
      formData.append('thumbnail', editCourseForm.value.thumbnail);
    } else if (editCourseForm.value.thumbnail === '') {
      formData.append('thumbnail', '');
    }
    const response = await api.patch(`/courses/${editCourseForm.value.slug}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    const index = courses.value.findIndex(course => course.slug === editCourseForm.value.slug);
    if (index !== -1) {
      courses.value[index] = response.data;
    }
    showEditCourseModal.value = false;
    resetEditCourseForm();
  } catch (error) {
    let errorMessage = 'Неизвестная ошибка';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    alert('Не удалось обновить курс: ' + errorMessage);
    if (error.response?.status === 401) {
      authStore.logout();
      router.push({ name: 'SignIn' });
    }
  }
};
const confirmDeleteCourse = (course) => {
  if (confirm(`Вы уверены, что хотите удалить курс "${course.title}"?`)) {
    deleteCourse(course);
  }
};
const deleteCourse = async (course) => {
  try {
    if (!course.slug) {
      throw new Error('Course slug is missing');
    }
    const url = `/courses/${course.slug}/`;
    try {
      await api.delete(url);
      courses.value = courses.value.filter(c => c.slug !== course.slug);
      showEditCourseModal.value = false;
      resetEditCourseForm();
      await loadCourses();
    } catch (error) {
      if (error.response?.status === 404) {
        try {
          const response = await api.get('/courses/');
          const coursesList = response.data;
          const similarCourse = coursesList.find(c => 
            c.title.toLowerCase() === course.title.toLowerCase() && c.slug !== course.slug
          );
          if (similarCourse) {
            await api.delete(`/courses/${similarCourse.slug}/`);
            courses.value = courses.value.filter(c => c.id !== similarCourse.id);
            showEditCourseModal.value = false;
            resetEditCourseForm();
            await loadCourses();
            return;
          }
        } catch (listError) {}
      }
      throw error;
    }
  } catch (error) {
    let errorMessage = 'Неизвестная ошибка';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    alert('Не удалось удалить курс: ' + errorMessage);
    if (error.response?.status === 401) {
      authStore.logout();
      router.push({ name: 'SignIn' });
    }
  }
};
const initialize = async () => {
  if (typeof authStore.ready === 'function') {
    try {
      await authStore.ready();
      try {
        const response = await api.get('/profile/');
        userStore.role = response.data.role;
      } catch (error) {
        userStore.role = 'student';
      }
    } catch (error) {}
  } else {
    if (!authStore.accessToken) {
      authStore.logout();
      router.push({ name: 'SignIn' });
      return;
    }
  }
  if (!authStore.isAuthenticated) {
    router.push({ name: 'SignIn' });
    return;
  }
  await loadCourses();
};
const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value;
  if (!isEditMode.value) {
    showCreateCourseModal.value = false;
    showEditCourseModal.value = false;
    resetNewCourseForm();
    resetEditCourseForm();
  }
};
onMounted(async () => {
  await initialize();
});
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

.publication-status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 10px;
}

.published {
  background-color: #4CAF50;
  color: white;
}

.unpublished {
  background-color: #F44336;
  color: white;
}

.form-group select.form-control {
  height: 44px;
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 10px;
  font-size: 14px;
  width: 100%;
}

.edit-toggle-btn {
  padding: 10px 24px;
  background: var(--background-color);
  color: var(--text-color);
  border: 2px solid var(--accent-color);
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 10px;
}

.edit-toggle-btn:hover {
  background: var(--accent-color);
  color: var(--footer-text);
}
</style>
