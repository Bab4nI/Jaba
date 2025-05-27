import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const useNewsStore = defineStore('news', {
  state: () => ({
    news: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchNews() {
      this.loading = true;
      try {
        const response = await axios.get(`${API_URL}/news/`);
        this.news = response.data;
      } catch (error) {
        this.error = error.message;
        console.error('Error fetching news:', error);
      } finally {
        this.loading = false;
      }
    },

    async uploadImage(file) {
      try {
        const formData = new FormData();
        formData.append('image', file);

        const response = await axios.post(`${API_URL}/news/upload_media/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        return response.data;
      } catch (error) {
        console.error('Error uploading image:', error);
        throw error;
      }
    },

    async addNews(title, content, imageUrl = '', link = '') {
      try {
        const response = await axios.post(`${API_URL}/news/`, {
          title,
          content,
          image_url: imageUrl,
          link
        });
        this.news.unshift(response.data);
        return response.data.id;
      } catch (error) {
        console.error('Error adding news:', error);
        throw error;
      }
    },

    async editNews(id, title, content, imageUrl = '', link = '') {
      try {
        let finalImageUrl = imageUrl;
        if (imageUrl && imageUrl.startsWith('http')) {
          const parts = imageUrl.split('/media/');
          if (parts.length > 1) {
            finalImageUrl = parts[1];
          }
        }

        const response = await axios.put(`${API_URL}/news/${id}/`, {
          title,
          content,
          image_url: finalImageUrl,
          link
        });
        const index = this.news.findIndex(item => item.id === id);
        if (index !== -1) {
          this.news[index] = response.data;
        }
        return true;
      } catch (error) {
        console.error('Error editing news:', error);
        throw error;
      }
    },

    async deleteNews(id) {
      try {
        await axios.delete(`${API_URL}/news/${id}/`);
        const index = this.news.findIndex(item => item.id === id);
        if (index !== -1) {
          this.news.splice(index, 1);
        }
        return true;
      } catch (error) {
        console.error('Error deleting news:', error);
        throw error;
      }
    },

    getRecentNews(count = 3) {
      return this.news.slice(0, count);
    },
  },
}); 