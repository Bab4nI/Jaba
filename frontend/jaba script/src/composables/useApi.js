import { ref } from 'vue';
import axios from 'axios';

export function useApi() {
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  const error = ref(null);
  const isLoading = ref(false);

  const uploadImage = async (lessonId, file) => {
    try {
      isLoading.value = true;
      const formData = new FormData();
      formData.append('image', file);
      formData.append('content_type', 'IMAGE');
      
      const response = await api.post(`api/courses/modules/lessons/${lessonId}/contents/`, formData);
      return response.data;
    } catch (err) {
      error.value = err.response?.data || err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const uploadFile = async (lessonId, file) => {
    try {
      isLoading.value = true;
      const formData = new FormData();
      formData.append('file', file);
      formData.append('content_type', 'FILE');
      
      const response = await api.post(`api/courses/modules/lessons/${lessonId}/contents/`, formData);
      return response.data;
    } catch (err) {
      error.value = err.response?.data || err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const saveContent = async (lessonId, contentData) => {
    try {
      isLoading.value = true;
      const url = contentData.id 
        ? `api/courses/modules/lessons/${lessonId}/contents/${contentData.id}/`
        : `api/courses/modules/lessons/${lessonId}/contents/`;
      
      const method = contentData.id ? 'put' : 'post';
      const response = await api[method](url, contentData);
      return response.data;
    } catch (err) {
      error.value = err.response?.data || err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    error,
    isLoading,
    uploadImage,
    uploadFile,
    saveContent
  };
}