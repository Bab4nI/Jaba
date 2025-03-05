import axios from 'axios';

export default {
    namespaced: true, // Включаем пространство имен
    state: {
      fullName: '',
      email: '',
      newEmail: '',
      level: '',
      group: '',
      course: '',
      department: '',
      isEditingEmail: false,
      emailError: '',
      avatarBase64: '',
    },
    mutations: {
      SET_USER_DATA(state, userData) {
        state.fullName = `${userData.last_name} ${userData.first_name}`;
        state.email = userData.email;
        state.newEmail = userData.email;
        state.level = userData.level;
        state.group = userData.group;
        state.course = userData.course;
        state.department = userData.department;
        state.avatarBase64 = userData.avatar_base64;
      },
      SET_AVATAR(state, avatarBase64) {
        state.avatarBase64 = avatarBase64;
      },
      TOGGLE_EDIT_EMAIL(state) {
        state.isEditingEmail = !state.isEditingEmail;
        if (state.isEditingEmail) {
          state.newEmail = state.email;
        }
        state.emailError = '';
      },
      SET_EMAIL_ERROR(state, error) {
        state.emailError = error;
      },
      UPDATE_EMAIL(state, newEmail) {
        state.email = newEmail;
        state.isEditingEmail = false;
        state.emailError = '';
      },
      SET_NEW_EMAIL(state, newEmail) {
        state.newEmail = newEmail;
      },
    },
    actions: {
      async fetchUserProfile({ commit }) {
        try {
          const accessToken = localStorage.getItem('access_token');
          if (!accessToken) {
            console.error('Отсутствует токен доступа');
            return;
          }
  
          const response = await axios.get('http://localhost:8000/api/profile/', {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          });
  
          commit('SET_USER_DATA', response.data);
        } catch (error) {
          console.error('Ошибка при загрузке данных профиля:', error);
          if (error.response) {
            console.error('Данные ошибки:', error.response.data);
          }
        }
      },
    async updateAvatar({ commit }, base64) {
      try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
          console.error('Отсутствует токен доступа');
          return;
        }

        await axios.patch(
          'http://localhost:8000/api/profile/',
          { avatar_base64: base64 },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        commit('SET_AVATAR', base64);
      } catch (error) {
        console.error('Ошибка при обновлении аватарки:', error);
      }
    },
    async saveEmail({ commit, state }) {
      const validateEmail = (email) => {
        const regex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return regex.test(email);
      };

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

        await axios.patch(
          'http://localhost:8000/api/profile/',
          { email: state.newEmail },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        commit('UPDATE_EMAIL', state.newEmail);
      } catch (error) {
        console.error('Ошибка при обновлении email:', error);
      }
    },
    toggleEditEmail({ commit }) {
      commit('TOGGLE_EDIT_EMAIL');
    },
    cancelEdit({ commit, state }) {
      commit('UPDATE_EMAIL', state.email);
    },
  },
};