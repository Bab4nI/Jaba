// src/stores/aiStore.js
import { defineStore } from 'pinia'
import api from '@/api'

export const useAIStore = defineStore('ai', {
  state: () => ({
    selectedText: '',
    modalVisible: false,
    isLoading: false,
    aiResponse: null,
    error: null,
    isEnabled: false,
    currentLessonId: null
  }),

  actions: {
    async toggleAI() {
      if (!this.currentLessonId) return;
      
      try {
        const response = await api.post(`/lessons/${this.currentLessonId}/ai-chat-state/toggle_state/`);
        this.isEnabled = response.data.is_enabled;
      } catch (error) {
        console.error('Error toggling AI state:', error);
        throw error;
      }
    },

    async setAIEnabled(enabled) {
      if (!this.currentLessonId) return;
      
      try {
        const response = await api.post(`/lessons/${this.currentLessonId}/ai-chat-state/set_state/`, {
          is_enabled: enabled
        });
        this.isEnabled = response.data.is_enabled;
      } catch (error) {
        console.error('Error setting AI state:', error);
        throw error;
      }
    },

    async loadAIState(lessonId) {
      if (!lessonId) return;
      
      try {
        this.currentLessonId = lessonId;
        const response = await api.get(`/lessons/${lessonId}/ai-chat-state/get_state/`);
        this.isEnabled = response.data.is_enabled;
      } catch (error) {
        console.error('Error loading AI state:', error);
        this.isEnabled = false;
      }
    },

    setSelectedText(text) {
      this.selectedText = text
      this.modalVisible = true
    },

    async askAI(prompt) {
      this.isLoading = true
      this.error = null

      try {
        const response = await api.post('/ai-chat/', {
          prompt: prompt,
          selected_text: this.selectedText,
        })
        this.aiResponse = response.data.response
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to get AI response'
        console.error('AI request error:', error)
      } finally {
        this.isLoading = false
      }
    },

    reset() {
      this.selectedText = ''
      this.aiResponse = null
      this.error = null
      this.modalVisible = false
      this.currentLessonId = null
      this.isEnabled = false
    },
  },
})