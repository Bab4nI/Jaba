<template>
  <div class="course-statistics-root">
    <h2 class="course-title" v-if="selectedCourse && courseName">{{ courseName }}</h2>
    
    <div class="course-select-row">
      <select v-model="selectedCourse" class="course-select" @change="onCourseChange">
        <option value="" disabled>Выберите курс</option>
        <option v-for="course in courses" :key="course.id" :value="course.slug">{{ course.title }}</option>
      </select>
      <span class="select-arrow">&#9662;</span>
      </div>
    
    <div class="group-select-row" v-if="selectedCourse">
      <select v-model="selectedGroup" class="course-select" @change="loadGroupData">
        <option value="admins">Преподаватели</option>
        <option v-for="group in groups" :key="group" :value="group">{{ group }}</option>
      </select>
      <span class="select-arrow">&#9662;</span>
          </div>
          
    <div v-if="loading" class="loading-indicator">Загрузка данных...</div>
    <div v-else-if="!selectedCourse" class="no-selection-message">Выберите курс для просмотра статистики</div>
    <div v-else-if="!works.length" class="no-selection-message">В курсе нет материалов для отображения</div>
    <div v-else class="table-wrapper">
      <table class="statistics-table">
        <thead>
          <tr>
            <th>{{ selectedGroup === 'admins' ? 'Имя преподавателя' : 'Имя студента' }}</th>
            <th v-for="work in works" :key="work.id">{{ work.title }}</th>
            <th>ИТОГ</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(student, idx) in students" :key="student.id || idx">
            <td>{{ student.full_name || 'Имя' }}</td>
            <td v-for="(work, workIdx) in works" :key="work.id" 
                :class="{ 'fail': getStudentWorkProgress(student, work).isFail }">
              {{ getStudentWorkProgress(student, work).value }}
            </td>
            <td :class="{ 'fail': getStudentTotal(student).isFail }">
              {{ getStudentTotal(student).value }}
            </td>
          </tr>
          <!-- Пустые строки для заполнения таблицы -->
          <tr v-for="n in emptyRows" :key="'empty'+n" class="empty-row">
            <td v-for="i in works.length + 2" :key="i">&nbsp;</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  </template>
  
<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import api from '@/api';

const loading = ref(false);
const groups = ref([]);
const selectedGroup = ref('');
const courses = ref([]);
const selectedCourse = ref('');
const courseName = ref('');

// Учебные работы (лабораторные, контрольные, статьи)
const works = ref([]);

const students = ref([]);
const progressData = ref({});

// Загрузка списка курсов при монтировании компонента
onMounted(async () => {
  loading.value = true;
  try {
    // Загружаем доступные курсы
    const coursesResponse = await api.get('/courses/');
    courses.value = coursesResponse.data;
    
    // Загружаем доступные группы
    await loadGroups();
  } catch (error) {
    console.error('Ошибка загрузки начальных данных:', error);
  } finally {
    loading.value = false;
  }
});

// Загрузка групп
const loadGroups = async () => {
  try {
    // Запрос на список уникальных групп через API
    const groupsResponse = await api.get('/groups/');
    groups.value = groupsResponse.data;
  } catch (error) {
    console.error('Ошибка загрузки групп:', error);
    // Fallback to hardcoded groups if API fails
    groups.value = ['КТсо2-4', 'КТсо2-3'];
      }
};

// Функция для обработки изменения выбранного курса
const onCourseChange = async () => {
  if (!selectedCourse.value) return;
  
  loading.value = true;
  try {
    // Загружаем данные курса (модули, уроки)
    const courseResponse = await api.get(`/courses/${selectedCourse.value}/`);
    const course = courseResponse.data;
    
    // Сохраняем название курса
    courseName.value = course.title;
    
    // Подготавливаем массив работ (lessons)
    const lessonPromises = [];
    
    // Для каждого модуля загружаем уроки
    for (const module of course.modules) {
      const lessonsResponse = await api.get(`/courses/${selectedCourse.value}/modules/${module.id}/lessons/`);
      lessonPromises.push(...lessonsResponse.data);
  }
  
    // Преобразуем уроки в формат работ для таблицы
    works.value = lessonPromises.map(lesson => ({
      id: lesson.id,
      title: lesson.title,
      max_score: 5, // Максимальный балл
      type: lesson.type || 'ARTICLE'
    }));
    
    // Если группа не выбрана, выбираем первую или admins
    if (!selectedGroup.value && groups.value.length > 0) {
      selectedGroup.value = groups.value[0];
    } else if (!selectedGroup.value) {
      selectedGroup.value = 'admins';
    }
    
    // Загружаем данные по выбранной группе
    await loadGroupData();
    
  } catch (error) {
    console.error('Ошибка загрузки данных курса:', error);
    works.value = [];
    courseName.value = '';
  } finally {
    loading.value = false;
  }
};

// Загрузка данных о студентах группы или админах
const loadGroupData = async () => {
  if (!selectedGroup.value || !selectedCourse.value) return;
  
  try {
    loading.value = true;
    
    let endpoint = '';
    // Определяем, загружать ли студентов группы или админов
    if (selectedGroup.value === 'admins') {
      endpoint = '/admins/';
    } else {
      endpoint = `/group-users/?group=${selectedGroup.value}`;
    }
    
    // Получаем список студентов/админов
    const studentsResponse = await api.get(endpoint);
    students.value = studentsResponse.data;
    
    // Инициализируем объект для хранения прогресса
    const newProgressData = {};
    
    // Загружаем прогресс для каждого студента/админа
    for (const student of students.value) {
      newProgressData[student.id] = {};
      
      try {
        // Реальный API-вызов для получения прогресса
        const progressResponse = await api.get(`/student-progress/?student_id=${student.id}&course_slug=${selectedCourse.value}`);
        
        // Обрабатываем полученные данные
        const progress = progressResponse.data;
        
        // Преобразуем данные в формат для отображения в таблице
        works.value.forEach(work => {
          if (progress[work.id]) {
            // Если есть данные о прогрессе для этого lesson_id
            const lessonProgress = progress[work.id];
            
            // Рассчитываем общий балл по содержимому урока
            let totalScore = 0;
            let maxPossibleScore = work.max_score;
            
            // Если есть детальные данные по контенту
            if (lessonProgress.contents && Object.keys(lessonProgress.contents).length > 0) {
              totalScore = Object.values(lessonProgress.contents).reduce((sum, content) => sum + content.score, 0);
              maxPossibleScore = Object.values(lessonProgress.contents).reduce((sum, content) => sum + content.max_score, 0);
            } else if (lessonProgress.completed) {
              // Если просто отмечено как завершенное
              totalScore = maxPossibleScore;
            }
            
            newProgressData[student.id][work.id] = {
              score: totalScore,
              completed: lessonProgress.completed,
              max_score: maxPossibleScore
            };
          } else {
            // Если нет данных, ставим нули
            newProgressData[student.id][work.id] = {
              score: 0,
              completed: false,
              max_score: work.max_score
            };
          }
        });
      } catch (error) {
        console.error(`Ошибка загрузки прогресса для студента ${student.id}:`, error);
        
        // Если ошибка при загрузке, инициализируем все нулями
        works.value.forEach(work => {
          newProgressData[student.id][work.id] = {
            score: 0,
            completed: false,
            max_score: work.max_score
          };
        });
      }
    }
    
    progressData.value = newProgressData;
  } catch (error) {
    console.error('Ошибка загрузки студентов:', error);
    students.value = [];
  } finally {
    loading.value = false;
  }
};

// Функция для получения прогресса студента по конкретной работе
const getStudentWorkProgress = (student, work) => {
  // Проверяем, есть ли данные о прогрессе для этого студента и работы
  const progress = progressData.value[student.id]?.[work.id];
  
  if (progress) {
    const value = `${progress.score}/${progress.max_score}`;
    const isFail = progress.score === 0 || (progress.max_score > 0 && progress.score < progress.max_score / 2);
    return { value, isFail };
  }
  
  return { value: '-', isFail: false };
};

// Функция для получения общего прогресса студента
const getStudentTotal = (student) => {
  if (!progressData.value[student.id]) {
    return { value: '0/0', isFail: true };
  }
  
  let totalScore = 0;
  let maxPossibleScore = 0;
  
  works.value.forEach(work => {
    if (progressData.value[student.id]?.[work.id]) {
      totalScore += progressData.value[student.id][work.id].score;
      maxPossibleScore += progressData.value[student.id][work.id].max_score;
    }
  });
  
  const value = `${totalScore}/${maxPossibleScore}`;
  const isFail = maxPossibleScore > 0 && totalScore < maxPossibleScore / 2;
  
  return { value, isFail };
};

// Сколько пустых строк добавить, чтобы таблица была как на макете
const emptyRows = computed(() => Math.max(0, 10 - students.value.length));

// Обновляем данные при изменении курса
watch(() => selectedCourse.value, (newValue) => {
  if (newValue) {
    onCourseChange();
  } else {
    // Если курс не выбран, сбрасываем данные
    works.value = [];
    students.value = [];
    progressData.value = {};
    courseName.value = '';
  }
});
</script>

<style scoped>
.course-statistics-root {
  background: var(--form-background, #f5f9f8);
  border-radius: 30px;
  padding: 40px 32px 32px 32px;
  min-width: 900px;
  transition: background-color 0.3s ease;
}
.course-title {
  font: 600 24px Raleway, sans-serif;
  color: var(--text-color, #24222f);
  margin-bottom: 18px;
  transition: color 0.3s ease;
  }
.course-select-row,
.group-select-row {
    display: flex;
  align-items: center;
  margin-bottom: 24px;
  position: relative;
  width: 280px;
}
.course-select {
  font: 400 18px Raleway, sans-serif;
  color: var(--text-color, #24222f);
  background: var(--input-background, #ebefef);
  border: 1px solid var(--border-color, #c5c8cc);
  border-radius: 10px;
  padding: 10px 40px 10px 16px;
  width: 100%;
  appearance: none;
  outline: none;
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
.select-arrow {
  position: absolute;
  right: 18px;
  pointer-events: none;
  color: var(--text-color, #24222f);
  font-size: 18px;
  transition: color 0.3s ease;
}
.loading-indicator,
.no-selection-message {
  text-align: center;
  padding: 20px;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color, #24222f);
  transition: color 0.3s ease;
}
.table-wrapper {
  background: var(--form-background, #fff);
  border-radius: 10px;
    overflow: hidden;
  box-shadow: 0 2px 8px rgba(160, 148, 184, 0.07);
  transition: background-color 0.3s ease;
}
.statistics-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-family: Raleway, sans-serif;
  background: var(--form-background, #fff);
  transition: background-color 0.3s ease;
}
.statistics-table thead tr {
  background: var(--thead-background, #ebefef);
  transition: background-color 0.3s ease;
}
.statistics-table th, .statistics-table td {
  padding: 12px 16px;
  text-align: center;
  font: 400 16px Raleway, sans-serif;
  border-bottom: 1px solid var(--border-color, #e0e4e8);
  color: var(--text-color, #24222f);
  transition: color 0.3s ease, border-color 0.3s ease;
}
.statistics-table th:first-child, .statistics-table td:first-child {
  text-align: left;
}
.statistics-table th {
  font-weight: 600;
  color: var(--secondary-text, #575667);
  transition: color 0.3s ease;
}
.statistics-table td.fail, .statistics-table th.fail {
  color: var(--error-color, #da1f38);
  font-weight: 600;
}
.statistics-table tr:last-child td {
  border-bottom: none;
}
.empty-row td {
  height: 36px;
}

/* Темная тема */
:global(.dark-theme) .course-statistics-root {
  --form-background: #23222b;
  --input-background: #2d2c38;
  --text-color: #f5f9f8;
  --secondary-text: #adadad;
  --border-color: #3e3d49;
  --thead-background: #2d2c38;
  --error-color: #ff4d4d;
  }
  </style>