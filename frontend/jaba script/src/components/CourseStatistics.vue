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
      <select v-model="selectedGroup" class="course-select" @change="onGroupChange">
        <option value="admins">Преподаватели</option>
        <option v-for="group in filteredGroups" :key="group" :value="group">{{ group }}</option>
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
            <th v-for="lesson in works" :key="lesson.id">{{ lesson.title || ('Урок ' + lesson.id) }}</th>
            <th>ИТОГ</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(student, idx) in students" :key="student.id || idx">
            <td>{{ student.full_name || 'Имя' }}</td>
            <td v-for="lesson in works" :key="lesson.id">
              {{ getStudentLessonScore(student, lesson) }}
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
import { useCourseStore } from '@/stores/course';

const loading = ref(false);
const groups = ref([]);
const selectedGroup = ref('admins');
const courses = ref([]);
const selectedCourse = ref('');
const courseName = ref('');
const courseStore = useCourseStore();
const lastFetchTime = ref(null);
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes cache

// Учебные работы (лабораторные, контрольные, статьи)
const works = ref([]);

const students = ref([]);
const progressData = ref({});
const lessonProgress = ref({});

// Загрузка списка курсов при монтировании компонента
onMounted(async () => {
  loading.value = true;
  try {
    // Загружаем доступные курсы с предотвращением кэширования
    const coursesResponse = await api.get('/courses/', {
      params: {
        _t: new Date().getTime()
      }
    });
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
    // Запрос на список уникальных групп через API с предотвращением кэширования
    const groupsResponse = await api.get('/groups/', {
      params: {
        _t: new Date().getTime()
      }
    });
    groups.value = groupsResponse.data;
  } catch (error) {
    console.error('Ошибка загрузки групп:', error);
    groups.value = [];
  }
};

// Функция для проверки необходимости обновления данных
const shouldRefreshData = () => {
  if (!lastFetchTime.value) return true;
  return Date.now() - lastFetchTime.value > CACHE_DURATION;
};

// Функция для обработки изменения выбранного курса
const onCourseChange = async () => {
  if (!selectedCourse.value) return;
  
  loading.value = true;
  try {
    // Загружаем данные курса (модули, уроки) с предотвращением кэширования
    const courseResponse = await api.get(`/courses/${selectedCourse.value}/`, {
      params: {
        _t: new Date().getTime()
      }
    });
    const course = courseResponse.data;
    console.log('DEBUG: course', course);
    
    // Сохраняем название курса
    courseName.value = course.title;
    
    // Подготавливаем массив работ (lessons)
    const allLessons = [];
    if (course.modules && course.modules.length) {
      for (const module of course.modules) {
        console.log('DEBUG: module', module);
        const lessonsResponse = await api.get(`/courses/${selectedCourse.value}/modules/${module.id}/lessons/`, {
          params: {
            _t: new Date().getTime()
          }
        });
        console.log('DEBUG: lessons for module', module.id, lessonsResponse.data);
        allLessons.push(...lessonsResponse.data);
      }
    } else {
      console.warn('DEBUG: course.modules is empty or undefined');
    }
    console.log('DEBUG: allLessons', allLessons);
  
    // Преобразуем уроки в формат работ для таблицы
    works.value = allLessons.map(lesson => ({
      id: lesson.id,
      title: lesson.title,
      max_score: lesson.max_score !== undefined ? lesson.max_score : 0,
      type: lesson.type || 'ARTICLE'
    }));
    console.log('DEBUG: works.value', works.value);
    
    // Если группа не выбрана, выбираем первую или admins
    if (!selectedGroup.value && groups.value.length > 0) {
      selectedGroup.value = groups.value[0];
    } else if (!selectedGroup.value) {
      selectedGroup.value = 'admins';
    }
    
    // Загружаем данные по выбранной группе
    await loadGroupData();
    
    // Обновляем время последней загрузки
    lastFetchTime.value = Date.now();
    
  } catch (error) {
    console.error('Ошибка загрузки данных курса:', error);
    works.value = [];
    courseName.value = '';
  } finally {
    loading.value = false;
  }
};

// Функция для обработки изменения выбранной группы
const onGroupChange = async () => {
  console.log('Group changed to:', selectedGroup.value);
  if (selectedGroup.value) {
    await loadGroupData();
  }
};

// Загрузка данных о студентах группы или админов
const loadGroupData = async () => {
  if (!selectedGroup.value || !selectedCourse.value) {
    console.log('Missing required data:', { group: selectedGroup.value, course: selectedCourse.value });
    return;
  }
  
  try {
    loading.value = true;
    console.log('Loading group data for:', { course: selectedCourse.value, group: selectedGroup.value });
    
    // Получаем статистику группы с предотвращением кэширования
    const response = await api.get(`/group-statistics/`, {
      params: {
        course_slug: selectedCourse.value,
        group: selectedGroup.value,
        _t: new Date().getTime()
      }
    });
    console.log('Group statistics response:', response.data);
    
    const data = response.data;
    
    // Обновляем название курса
    courseName.value = data.course.title;
    
    // Получаем актуальные названия уроков из API
    const courseResponse = await api.get(`/courses/${selectedCourse.value}/`, {
      params: {
        _t: new Date().getTime()
      }
    });
    const course = courseResponse.data;
    const allLessons = [];
    for (const module of course.modules) {
      const lessonsResponse = await api.get(`/courses/${selectedCourse.value}/modules/${module.id}/lessons/`, {
        params: {
          _t: new Date().getTime()
        }
      });
      allLessons.push(...lessonsResponse.data);
    }
    
    // Обновляем названия работ в works.value по id
    works.value = data.lessons.map(lesson => {
      const fresh = allLessons.find(l => l.id === lesson.id);
      return {
        ...lesson,
        title: fresh ? fresh.title : lesson.title
      };
    });
    
    // Обновляем список студентов и их прогресс
    students.value = data.users.map(user => ({
      id: user.id,
      full_name: user.full_name || user.username
    }));
    
    // Обновляем данные о прогрессе
    const newProgressData = {};
    data.users.forEach(user => {
      newProgressData[user.id] = {};
      works.value.forEach(work => {
        const progress = user.progress[work.id];
        if (progress) {
          newProgressData[user.id][work.id] = {
            score: progress.score || 0,
            max_score: progress.max_score || work.max_score
          };
        } else {
          newProgressData[user.id][work.id] = {
            score: 0,
            max_score: work.max_score
          };
        }
      });
    });
    
    progressData.value = newProgressData;
    
    // Обновляем время последней загрузки
    lastFetchTime.value = Date.now();
    
  } catch (error) {
    console.error('Ошибка загрузки статистики группы:', error);
    students.value = [];
    works.value = [];
    progressData.value = {};
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
  let totalScore = 0;
  let totalMax = 0;
  
  for (const lesson of works.value) {
    const progress = progressData.value[student.id]?.[lesson.id];
    if (progress) {
      totalScore += progress.score;
      totalMax += progress.max_score;
    }
  }
  
  return {
    value: `${totalScore}/${totalMax}`,
    isFail: totalMax > 0 && totalScore / totalMax < 0.6
  };
};

// Сколько пустых строк добавить, чтобы таблица была как на макете
const emptyRows = computed(() => Math.max(0, 10 - students.value.length));

// Обновляем данные при изменении курса
watch(() => selectedCourse.value, async (newValue) => {
  if (newValue) {
    if (shouldRefreshData()) {
      await onCourseChange();
    }
    // Если группа уже выбрана, загружаем данные группы
    if (selectedGroup.value) {
      await loadGroupData();
    }
  } else {
    // Если курс не выбран, сбрасываем данные
    works.value = [];
    students.value = [];
    progressData.value = {};
    courseName.value = '';
  }
});

// Добавляем watch для selectedGroup
watch(() => selectedGroup.value, async (newValue) => {
  if (newValue && selectedCourse.value) {
    if (shouldRefreshData()) {
      await loadGroupData();
    }
  }
});

// Добавляем watch для refreshTrigger из стора
watch(() => courseStore.refreshTrigger, async () => {
  if (selectedCourse.value && selectedGroup.value) {
    // Принудительно обновляем данные при изменении refreshTrigger
    lastFetchTime.value = null;
    await loadGroupData();
  }
});

// Фильтр для групп, чтобы не было дублирующегося 'admins'
const filteredGroups = computed(() => groups.value.filter(g => g !== 'admins'));

// Загрузка прогресса по всем урокам для всех студентов
const loadLessonProgress = async () => {
  lessonProgress.value = {};
  for (const student of students.value) {
    try {
      const response = await api.get('/content-progress/', {
        params: { user_id: student.id }
      });
      lessonProgress.value[student.id] = {};
      for (const progress of response.data) {
        lessonProgress.value[student.id][progress.content_id] = {
          score: progress.score,
          completed: progress.completed
        };
      }
    } catch (e) {
      lessonProgress.value[student.id] = {};
    }
  }
};

// После загрузки студентов и works вызываем loadLessonProgress
watch([students, works], async () => {
  if (students.value.length && works.value.length) {
    await loadLessonProgress();
  }
});

// Для отображения в таблице:
const getStudentLessonScore = (student, lesson) => {
  const progress = progressData.value[student.id]?.[lesson.id];
  if (!progress) return '-';
  return `${progress.score}/${progress.max_score}`;
};
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