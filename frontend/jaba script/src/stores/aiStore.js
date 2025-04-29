// src/stores/aiStore.js
import { defineStore } from 'pinia'
import api from '@/api'

export const useAIStore = defineStore('ai', {
  state: () => ({
    selectedText: '',
    modalVisible: false,
    isLoading: false,
    aiResponse: '',
    error: null,
  }),

  actions: {
    setSelectedText(text) {
      this.selectedText = text
      this.modalVisible = true
    },

    async askAI(prompt) {
      this.isLoading = true
      this.error = null

      try {
        const response = await api.post('/ai/chat/', {
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
      this.aiResponse = ''
      this.error = null
      this.modalVisible = false
    },
  },
})