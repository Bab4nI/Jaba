// store/userStore.js
import axios from 'axios';

export default {
  namespaced: true,
  state: {
    first_name: '', // Имя пользователя
    last_name: '', // Фамилия пользователя
    middle_name: '', // Отчество
    email: '', // Электронная почта пользователя
    newEmail: '', // Новый email для редактирования
    group: '', // Группа пользователя
    avatarBase64: '', // Аватар пользователя в формате base64
    role: '', // Роль пользователя (по умолчанию 'user')
    activeTab: 'Мой профиль', // Активная вкладка
  },
  mutations: {
    // Установка данных пользователя
    SET_USER_DATA(state, userData) {
      state.first_name = userData.first_name; // Имя
      state.last_name = userData.last_name; // Фамилия
      state.middle_name = userData.middle_name; // Отчество
      state.email = userData.email; // Электронная почта
      state.newEmail = userData.email; // Новый email (для редактирования)
      state.group = userData.group; // Группа
      state.avatarBase64 = userData.avatar_base64; // Аватар
      state.role = userData.role; // Роль пользователя
    },
    // Установка аватара
    SET_AVATAR(state, avatarBase64) {
      state.avatarBase64 = avatarBase64;
    },
    // Переключение режима редактирования email
    TOGGLE_EDIT_EMAIL(state) {
      state.isEditingEmail = !state.isEditingEmail;
      if (state.isEditingEmail) {
        state.newEmail = state.email; // Сбрасываем новое значение email на текущее
      }
      state.emailError = ''; // Очищаем ошибку
    },
    // Установка ошибки email
    SET_EMAIL_ERROR(state, error) {
      state.emailError = error;
    },
    // Обновление email
    UPDATE_EMAIL(state, newEmail) {
      state.email = newEmail;
      state.isEditingEmail = false; // Завершаем редактирование
      state.emailError = ''; // Очищаем ошибку
    },
    // Установка нового email (для редактирования)
    SET_NEW_EMAIL(state, newEmail) {
      state.newEmail = newEmail;
    },
    // Установка роли пользователя
    SET_ROLE(state, role) {
      state.role = role;
    },
    // Установка активной вкладки
    SET_ACTIVE_TAB(state, tab) {
      state.activeTab = tab;
    },
  },
  actions: {
    // Загрузка данных профиля пользователя
    async fetchUserProfile({ commit, dispatch }) {
      try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
          console.error('Отсутствует токен доступа');
          return;
        }

        // Запрос данных профиля
        const response = await axios.get('http://localhost:8000/api/profile/', {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        // Сохранение данных в хранилище
        commit('SET_USER_DATA', response.data);
      } catch (error) {
        console.error('Ошибка при загрузке данных профиля:', error);
        if (error.response && error.response.status === 401) {
          // Если токен истек, обновляем его и повторяем запрос
          await dispatch('refresh/refreshToken', null, { root: true });
          await dispatch('fetchUserProfile');
        }
      }
    },
    // Обновление аватара пользователя
    async updateAvatar({ commit }, base64) {
      try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
          console.error('Отсутствует токен доступа');
          return;
        }

        // Отправка запроса на обновление аватара
        await axios.patch(
          'http://localhost:8000/api/profile/',
          { avatar_base64: base64 },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        // Сохранение нового аватара в хранилище
        commit('SET_AVATAR', base64);
      } catch (error) {
        console.error('Ошибка при обновлении аватарки:', error);
      }
    },
    // Сохранение нового email
    async saveEmail({ commit, state, dispatch }) {
      const validateEmail = (email) => {
        const regex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return regex.test(email);
      };

      // Валидация email
      if (!validateEmail(state.newEmail)) {
        commit('SET_EMAIL_ERROR', 'Введите корректный адрес электронной почты');
        return;
      }

      try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
          console.error('Отсутствует токен доступа');
          return;
        }

        // Отправка запроса на обновление email
        await axios.patch(
          'http://localhost:8000/api/profile/',
          { email: state.newEmail },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        // Сохранение нового email в хранилище
        commit('UPDATE_EMAIL', state.newEmail);
      } catch (error) {
        console.error('Ошибка при обновлении email:', error);
        if (error.response && error.response.status === 401) {
          // Если токен истек, обновляем его и повторяем запрос
          await dispatch('refresh/refreshToken', null, { root: true });
          await dispatch('saveEmail');
        }
      }
    },
    // Переключение режима редактирования email
    toggleEditEmail({ commit }) {
      commit('TOGGLE_EDIT_EMAIL');
    },
    // Отмена редактирования email
    cancelEdit({ commit, state }) {
      commit('UPDATE_EMAIL', state.email);
    },
    // Установка активной вкладки
    setActiveTab({ commit }, tab) {
      commit('SET_ACTIVE_TAB', tab);
    },
  },
  getters: {
    // Получение активной вкладки
    activeTab: (state) => state.activeTab,
  },
};