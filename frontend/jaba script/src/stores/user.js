// store/user.js
import { defineStore } from 'pinia';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';

export const useUserStore = defineStore('user', {
  state: () => ({
    first_name: '',
    last_name: '',
    middle_name: '',
    email: '',
    newEmail: '',
    group: '',
    avatarBase64: '',
    role: '',
    activeTab: 'Мой профиль',
    accessToken: localStorage.getItem('access_token') || null,
  }),
  actions: {
    setAccessToken(accessToken) {
      this.accessToken = accessToken;
    },
    SET_USER_DATA(userData) {
      this.first_name = userData.first_name || '';
      this.last_name = userData.last_name || '';
      this.middle_name = userData.middle_name || '';
      this.email = userData.email || '';
      this.newEmail = userData.email || '';
      this.group = userData.group || '';
      this.avatarBase64 = userData.avatar_base64 || '';
      this.role = userData.role || '';
    },
    async fetchUserProfile() {
      try {
        const token = this.accessToken;
        if (!token) {
          console.error('❌ Отсутствует токен доступа');
          return;
        }

        const response = await axios.get('http://localhost:8000/api/profile/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.SET_USER_DATA(response.data);
      } catch (error) {
        console.error('❌ Ошибка при загрузке данных профиля:', error);
        if (error.response && error.response.status === 401) {
          const refreshStore = useRefreshStore();
          await refreshStore.refreshToken();

          // ✅ Если токен обновился — перезапрашиваем профиль
          if (refreshStore.accessToken) {
            this.setAccessToken(refreshStore.accessToken);
            await this.fetchUserProfile();
          }
        }
      }
    },
    async updateAvatar(base64) {
      try {
        const token = this.accessToken;
        if (!token) {
          console.error('❌ Отсутствует токен доступа');
          return;
        }

        await axios.patch(
          'http://localhost:8000/api/profile/',
          { avatar_base64: base64 },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        this.avatarBase64 = base64;
      } catch (error) {
        console.error('❌ Ошибка при обновлении аватарки:', error);
      }
    },
    async saveEmail() {
      try {
        const token = this.accessToken;
        if (!token) {
          console.error('❌ Отсутствует токен доступа');
          return;
        }

        await axios.patch(
          'http://localhost:8000/api/profile/',
          { email: this.newEmail },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        this.email = this.newEmail;
      } catch (error) {
        console.error('❌ Ошибка при обновлении email:', error);
        if (error.response && error.response.status === 401) {
          const refreshStore = useRefreshStore();
          await refreshStore.refreshToken();

          if (refreshStore.accessToken) {
            this.setAccessToken(refreshStore.accessToken);
            await this.saveEmail();
          }
        }
      }
    },
    toggleEditEmail() {
      this.isEditingEmail = !this.isEditingEmail;
      if (this.isEditingEmail) {
        this.newEmail = this.email;
      }
      this.emailError = '';
    },
    cancelEdit() {
      this.newEmail = this.email;
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    },
  },
});
