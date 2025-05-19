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
    isEnabled: false
  }),

  actions: {
    toggleAI() {
      this.isEnabled = !this.isEnabled
    },

    setAIEnabled(enabled) {
      this.isEnabled = enabled
    },

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
      this.aiResponse = null
      this.error = null
      this.modalVisible = false
    },
  },
})