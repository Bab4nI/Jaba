<template>
  <div class="schedule-container">
    <div class="calendar-container2">
      <div class="calendar-container1">
        <div class="horizontal-flex-container">
          <div class="svg-container small-icon" @click="prevMonth">
            <svg viewBox="0 0 6.5 13" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6,0.5l-5.5,6l5.5,6" stroke="#24222F" />
            </svg>
          </div>
          <div class="vertical-center-text-box">
            <p class="majestic-heading">{{ currentMonthName }} {{ currentYear }}</p>
          </div>
          <div class="svg-container small-icon" @click="nextMonth">
            <svg viewBox="0 0 6.5 13" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M0.5,0.5l5.5,6l-5.5,6" stroke="#24222F" />
            </svg>
          </div>
        </div>
      </div>
      <div class="calendar-container">
        <div class="flex-calendar-row">
          <p class="schedule-item">Пн</p>
          <p class="schedule-item">Вт</p>
          <p class="schedule-item">Ср</p>
          <p class="schedule-item">Чт</p>
          <p class="schedule-item">Пт</p>
          <p class="schedule-item weekend">Сб</p>
          <p class="schedule-item weekend">Вс</p>
        </div>
        <div class="calendar-grid">
          <div class="flex-calendar-row" v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex">
            <p
              v-for="(day, index) in week"
              :key="index"
              :class="{
                'text-block': day.isCurrentMonth && index < 5,
                'weekend': day.isCurrentMonth && index >= 5,
                'number-highlighted': !day.isCurrentMonth,
                'selected-date': day.isCurrentMonth && selectedDate === day.day,
                'has-assignment': day.isCurrentMonth && hasAssignment(day.day)
              }"
              @click="day.isCurrentMonth && openModal(day.day)"
            >
              {{ day.day }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ selectedAssignment?.title || 'Нет заданий' }}</h3>
          <span class="close-btn" @click="closeModal">&times;</span>
        </div>
        <div class="modal-body">
          <template v-if="selectedAssignments.length > 1">
            <select id="assignment-select" v-model="selectedAssignmentIndex" class="styled-select">
              <option v-for="(a, idx) in selectedAssignments" :key="a.id" :value="idx">
                {{ a.title }} ({{ formatAssignmentDate(a.start_datetime) }})
              </option>
            </select>
          </template>
          <template v-if="selectedAssignment">
            <p><strong>Название:</strong> {{ selectedAssignment.title }}</p>
            <p><strong>Тип:</strong> {{ selectedAssignment.type === 'LAB' ? 'Лабораторная работа' : 
                                        selectedAssignment.type === 'PRACTICE' ? 'Практика' : 'Статья' }}</p>
            <p><strong>Дата:</strong> {{ formatAssignmentDate(selectedAssignment.start_datetime) }}</p>
            <p><strong>Время:</strong> {{ selectedAssignment.time }}</p>
            <p><strong>Описание:</strong> {{ selectedAssignment.description }}</p>
            <button class="go-to-assignment-btn" @click="goToAssignment(selectedAssignment.id)">Перейти к работе</button>
          </template>
          <p v-else>На выбранную дату нет запланированных заданий.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRefreshStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();

// Configure axios
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

// Add request interceptor to add auth token
api.interceptors.request.use(
  config => {
    const authStore = useRefreshStore();
    const token = authStore.accessToken || localStorage.getItem('access_token');
    
    console.log('Current token:', token);
    
    if (token) {
      const tokenValue = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
      config.headers.Authorization = tokenValue;
      console.log('Added Authorization header:', tokenValue);
    } else {
      console.log('No token found');
    }
    
    return config;
  },
  error => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.log('Response error:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      });
      
      if (error.response.status === 401) {
        const authStore = useRefreshStore();
        authStore.logout();
        localStorage.removeItem('access_token');
        console.log('Authentication error, token cleared');
      }
    }
    return Promise.reject(error);
  }
);

const currentDate = ref(new Date());
const months = [
  "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];

// Modal state
const showModal = ref(false);
const selectedDate = ref(null);
const assignments = ref([]);
const loading = ref(false);
const error = ref(null);

// Fetch assignments from the server
const fetchAssignments = async () => {
  loading.value = true;
  error.value = null;
  
  const authStore = useRefreshStore();
  const token = authStore.accessToken || localStorage.getItem('access_token');
  
  if (!token) {
    error.value = 'Требуется авторизация';
    loading.value = false;
    return;
  }
  
  try {
    console.log('Testing API endpoints...');
    console.log('Using token:', token);
    
    const coursesResponse = await api.get('/api/courses/');
    console.log('Courses response:', coursesResponse.data);
    
    const courses = Array.isArray(coursesResponse.data) ? coursesResponse.data : coursesResponse.data.results || [];
    console.log('Parsed courses:', courses);
    
    if (courses.length === 0) {
      console.log('No courses found');
      return;
    }
    
    const allLessons = [];
    for (const course of courses) {
      try {
        console.log(`Fetching modules for course: ${course.slug}`);
        const modulesResponse = await api.get(`/api/courses/${course.slug}/modules/`);
        const modules = Array.isArray(modulesResponse.data) ? modulesResponse.data : modulesResponse.data.results || [];
        
        for (const module of modules) {
          console.log(`Fetching lessons for module: ${module.id}`);
          const lessonsResponse = await api.get(`/api/courses/${course.slug}/modules/${module.id}/lessons/`);
          const lessons = Array.isArray(lessonsResponse.data) ? lessonsResponse.data : lessonsResponse.data.results || [];
          console.log(`Found ${lessons.length} lessons in module ${module.id}`);
          allLessons.push(...lessons);
        }
      } catch (err) {
        console.error(`Error fetching data for course ${course.slug}:`, err);
        if (err.response) {
          console.error('Error details:', {
            status: err.response.status,
            data: err.response.data
          });
        }
      }
    }
    
    console.log('Total lessons found:', allLessons.length);
    console.log('Raw lessons data:', allLessons);
    
    assignments.value = allLessons
      .filter(lesson => lesson.start_datetime && lesson.end_datetime)
      .map(lesson => {
        const startDate = new Date(lesson.start_datetime);
        const endDate = new Date(lesson.end_datetime);
        return {
          id: lesson.id,
          title: lesson.title,
          date: startDate.toISOString().split('T')[0],
          time: `${startDate.toHoursMinutes()} - ${endDate.toHoursMinutes()}`,
          description: lesson.description || 'Нет описания',
          rooms: lesson.rooms || 'Не указано',
          type: lesson.type || 'ARTICLE',
          start_datetime: lesson.start_datetime,
          end_datetime: lesson.end_datetime
        };
      });
    
    console.log('Final assignments:', assignments.value);
  } catch (err) {
    error.value = 'Ошибка при загрузке заданий';
    console.error('Error fetching assignments:', err);
    if (err.response) {
      console.error('Error response:', err.response.data);
      console.error('Error status:', err.response.status);
      console.error('Error headers:', err.response.headers);
    }
  } finally {
    loading.value = false;
  }
};

// Helper function to format time
Date.prototype.toHoursMinutes = function() {
  return `${String(this.getHours()).padStart(2, '0')}:${String(this.getMinutes()).padStart(2, '0')}`;
};

const currentMonth = computed(() => currentDate.value.getMonth());
const currentYear = computed(() => currentDate.value.getFullYear());
const currentMonthName = computed(() => months[currentMonth.value]);

// Helper function to format date for comparison
const formatDateForComparison = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const formattedDate = `${year}-${month}-${day}`;
  console.log('Formatted date for comparison:', formattedDate);
  return formattedDate;
};

const hasAssignment = (day) => {
  if (!day) return false;
  const date = new Date(currentYear.value, currentMonth.value, day);
  date.setHours(0, 0, 0, 0);
  return assignments.value.some(a => {
    if (!a.start_datetime) return false;
    const start = new Date(a.start_datetime);
    start.setHours(0, 0, 0, 0);
    return date.getTime() === start.getTime();
  });
};

const selectedAssignments = computed(() => {
  if (!selectedDate.value) return [];
  const date = new Date(currentYear.value, currentMonth.value, selectedDate.value);
  date.setHours(0, 0, 0, 0);
  return assignments.value.filter(a => {
    if (!a.start_datetime) return false;
    const start = new Date(a.start_datetime);
    start.setHours(0, 0, 0, 0);
    return date.getTime() === start.getTime();
  });
});

const selectedAssignmentIndex = ref(0);
const selectedAssignment = computed(() => {
  const arr = selectedAssignments.value;
  return arr.length > 0 ? arr[selectedAssignmentIndex.value] : null;
});

const calendarWeeks = computed(() => {
  const year = currentYear.value;
  const month = currentMonth.value;
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startDay = firstDayOfMonth.getDay() === 0 ? 6 : firstDayOfMonth.getDay() - 1;
  const daysInMonth = lastDayOfMonth.getDate();
  const weeks = [];
  let week = [];

  for (let i = 0; i < startDay; i++) {
    week.push({ day: '', isCurrentMonth: false });
  }
  for (let day = 1; day <= daysInMonth; day++) {
    week.push({ day, isCurrentMonth: true });
    if (week.length === 7) {
      weeks.push(week);
      week = [];
    }
  }
  if (week.length > 0) {
    while (week.length < 7) {
      week.push({ day: '', isCurrentMonth: false });
    }
    weeks.push(week);
  }
  return weeks;
});

const prevMonth = () => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() - 1);

  const minDate = new Date();
  minDate.setMonth(minDate.getMonth() - 2);

  if (newDate >= minDate) {
    currentDate.value = newDate;
  }
};

const nextMonth = () => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() + 1);

  const maxDate = new Date();
  maxDate.setMonth(maxDate.getMonth() + 2);

  if (newDate <= maxDate) {
    currentDate.value = newDate;
  }
};

// Helper functions for date formatting
const formatDate = (date) => {
  if (typeof date === 'string') {
    const [year, month, day] = date.split('-');
    return `${day}.${month}.${year}`;
  }
  return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}`;
};

// Функция для форматирования даты создания
const formatAssignmentDate = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
};

// Modal functions
const openModal = (day) => {
  selectedDate.value = day;
  selectedAssignmentIndex.value = 0;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedDate.value = null;
};

// Функция перехода к работе
const goToAssignment = (id) => {
  if (id) {
    router.push(`/lessons/${id}`);
  }
};

// Load assignments when component is mounted
onMounted(() => {
  fetchAssignments();
});
</script>

<style scoped>
/* Existing styles */
.horizontal-flex-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
}

.vertical-center-text-box {
  width: 150px;
  text-align: center;
}

.schedule-container {
  width: 430px;
  padding: 0px 44px;
}

.calendar-container2 {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.calendar-container1 {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.horizontal-flex-container {
  display: flex;
  align-items: center;
  gap: 20px;
}

.svg-container {
  cursor: pointer;
  color: var(--text-color);
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.svg-container svg {
  stroke: currentColor;
  width: 100%;
  height: 100%;
}

.small-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.small-icon svg {
  width: 10px;
  height: 10px;
}

.majestic-heading {
  font: 700 20px Raleway, sans-serif;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.flex-calendar-row {
  display: flex;
  justify-content: space-between;
}

.calendar-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.schedule-item {
  font: 400 14px Raleway, sans-serif;
  color: var(--text-color);
  text-align: center;
  width: 31px;
  transition: color 0.3s ease;
}

.weekend {
  color: var(--error-color);
  font: 400 20px Montserrat, sans-serif;
  text-align: center;
  width: 31px;
  transition: color 0.3s ease;
}

.text-block {
  font: 400 20px Montserrat, sans-serif;
  color: var(--text-color);
  text-align: center;
  width: 31px;
  height: 31px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.text-block:hover {
  background-color: var(--hover-background);
}

.number-highlighted {
  font: 400 20px Montserrat, sans-serif;
  color: var(--border-color);
  text-align: center;
  width: 31px;
  transition: color 0.3s ease;
}

/* Highlight for selected date */
.selected-date {
  background-color: var(--hover-background);
  border-radius: 50%;
  font: 400 20px Montserrat, sans-serif;
  color: var(--text-color);
  transition: all 0.3s ease;
  border: 2px solid var(--accent-color);
}

/* Style for dates with assignments */
.has-assignment {
  position: relative;
  border: 2px solid var(--accent-color);
  border-radius: 50%;
  width: 31px;
  height: 31px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.has-assignment:hover {
  background-color: var(--hover-background);
  border-color: var(--hover-accent);
}

/* Remove the dot style */
.has-assignment::after {
  display: none;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--form-background);
  border-radius: 8px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.close-btn {
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: var(--text-color);
}

.modal-body {
  padding: 20px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.modal-body p {
  margin: 0 0 10px;
  line-height: 1.5;
}

.modal-body strong {
  font-weight: 600;
  color: var(--text-color);
  transition: color 0.3s ease;
}

/* Loading styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: var(--error-color);
  text-align: center;
  margin-top: 10px;
  padding: 10px;
  background-color: var(--error-background);
  border-radius: 4px;
}

/* Красивый select для модального окна */
.styled-select {
  width: 100%;
  padding: 10px 14px;
  margin-bottom: 18px;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  background: var(--form-background);
  border: 2px solid var(--accent-color);
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s;
  box-shadow: 0 2px 8px rgba(160, 148, 184, 0.07);
  appearance: none;
  cursor: pointer;
}

.styled-select:focus {
  border-color: var(--hover-accent);
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.15);
}

.styled-select option {
  background: var(--form-background);
  color: var(--text-color);
}

.go-to-assignment-btn {
  margin-top: 18px;
  width: 100%;
  padding: 10px 0;
  background: var(--accent-color);
  color: #fff;
  font: 500 16px Raleway, sans-serif;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(160, 148, 184, 0.07);
}

.go-to-assignment-btn:hover {
  background: var(--hover-accent);
}
</style>