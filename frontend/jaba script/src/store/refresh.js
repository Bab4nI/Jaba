// refresh.js
import axios from 'axios';

export default {
    namespaced: false,
    state: {
      accessToken: localStorage.getItem('access_token') || null,
      refreshToken: localStorage.getItem('refresh_token') || null,
      isRefreshingToken: false,
      lastRefreshTime: null,
    },
    mutations: {
      setTokens(state, { access, refresh }) {
        state.accessToken = access;
        state.refreshToken = refresh;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
      },
      clearTokens(state) {
        state.accessToken = null;
        state.refreshToken = null;
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
        const currentTime = Date.now();
        if (state.lastRefreshTime && currentTime - state.lastRefreshTime < 60000) {
          console.log('Задержка 1 минута перед следующим обновлением токена.');
          return;
        }
  
        if (state.isRefreshingToken) {
          console.log('Токен уже обновляется...');
          return;
        }
  
        if (!state.refreshToken) {
          console.log('Refresh token отсутствует. Выход из системы...');
          commit('clearTokens');
          return;
        }
  
        try {
          commit('setRefreshingToken', true);
          console.log('Обновление токена...');
          const response = await axios.post('http://localhost:8000/api/token/refresh/', {
            refresh: state.refreshToken,
          });
          console.log('Ответ сервера:', response.data);
  
          const newRefreshToken = response.data.refresh || state.refreshToken;
  
          commit('setTokens', {
            access: response.data.access,
            refresh: newRefreshToken,
          });
  
          commit('setLastRefreshTime', Date.now());
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