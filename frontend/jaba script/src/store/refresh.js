// store/refresh.js
import axios from 'axios';

export default {
  namespaced: true,
  state: {
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isRefreshingToken: false,
    lastRefreshTime: null,
    isAuthenticated: !!localStorage.getItem('access_token'), // Добавляем состояние аутентификации
  },
  mutations: {
    setAccessToken(state, accessToken) {
      state.accessToken = accessToken;
      localStorage.setItem('access_token', accessToken);
      state.isAuthenticated = true; // Устанавливаем аутентификацию
    },
    setRefreshToken(state, refreshToken) {
      state.refreshToken = refreshToken;
      localStorage.setItem('refresh_token', refreshToken);
    },
    clearTokens(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false; // Сбрасываем аутентификацию
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    setRefreshingToken(state, isRefreshing) {
      state.isRefreshingToken = isRefreshing;
    },
    setLastRefreshTime(state, time) {
      state.lastRefreshTime = time;
    },
  },
  actions: {
    async refreshToken({ commit, state }) {
      if (state.isRefreshingToken) return;

      if (!state.refreshToken) {
        commit('clearTokens');
        return;
      }

      try {
        commit('setRefreshingToken', true);
        const response = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: state.refreshToken, // Исправлено: state.refreshToken
        });

        if (response.data.access) {
          commit('setAccessToken', response.data.access);
          if (response.data.refresh) {
            commit('setRefreshToken', response.data.refresh);
          }
          commit('setLastRefreshTime', Date.now());
        } else {
          commit('clearTokens');
        }
      } catch (error) {
        console.error('Ошибка при обновлении токена:', error.response?.data || error.message);
        commit('clearTokens');
      } finally {
        commit('setRefreshingToken', false);
      }
    },
    logout({ commit }) {
      commit('clearTokens');
    },
  },
};