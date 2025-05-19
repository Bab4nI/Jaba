<template>
  <!-- AI Chat Modal -->
  <div v-if="aiStore.modalVisible" class="ai-chat-modal" role="dialog" aria-labelledby="ai-modal-title">
    <div class="chat-container">
      <div class="chat-bubble-container">
        <p class="chat-title-text-style">Чат с ИИ-ассистентом</p>
        <button class="ai-modal-close" @click="closeAiModal" aria-label="Закрыть модальное окно">×</button>
      </div>
      
      <div class="student-question-card">
        <div class="neural-response-container1">
          <div class="neural-response-container2" v-if="aiStore.aiResponse">
            <div class="neural-answer-container">AI</div>
            <div class="neural-response-container">
              <p class="neural-response-text" v-html="renderMarkdown(aiStore.aiResponse)"></p>
              <p class="time-stamp-text-style">{{ getCurrentTime() }}</p>
            </div>
          </div>
          
          <div v-if="aiStore.isLoading" class="neural-response-container2">
            <div class="neural-answer-container">AI</div>
            <div class="neural-response-container">
              <div class="ai-loading-panel">
                <span class="spinner"></span>
                <p class="info-text">Идет обработка запроса...</p>
              </div>
            </div>
          </div>
          
          <div v-if="aiStore.error" class="neural-response-container2">
            <div class="neural-answer-container">AI</div>
            <div class="neural-response-container error">
              <p class="error-text">Ошибка AI: {{ aiStore.error }}</p>
            </div>
          </div>
          
          <div class="content-container1">
            <div class="border-divider-horizontal"></div>
            <div class="content-wrapper2">
              <input 
                type="text" 
                v-model="aiUserPrompt" 
                class="question-prompt" 
                placeholder="Спросить что-нибудь..." 
                @keyup.enter="aiAskCustom"
              >
              <div class="ai-quick-actions">
                <button @click="aiExplainText" class="ai-action-btn">Объяснить</button>
                <button @click="aiSimplifyText" class="ai-action-btn">Упростить</button>
              </div>
              <button @click="aiAskCustom" class="send-button" aria-label="Отправить запрос">
                <svg viewBox="0 0 24 24" width="18" height="18" class="send-icon">
                  <defs>
                    <linearGradient id="sendGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
                      <stop offset="100%" stop-color="#e6e6e6" stop-opacity="0.8" />
                    </linearGradient>
                  </defs>
                  <path 
                    d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" 
                    fill="url(#sendGradient)" 
                    stroke="white" 
                    stroke-width="1.5" 
                    stroke-linecap="round" 
                    stroke-linejoin="round"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAIStore } from '@/stores/aiStore'
import { useThemeStore } from '@/stores/themeStore'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export default {
  name: 'AIChat',
  props: {
    selectedText: {
      type: String,
      default: ''
    }
  },
  emits: ['show-toast', 'close-modal'],
  setup(props, { emit }) {
    const aiStore = useAIStore()
    const themeStore = useThemeStore()
    const aiUserPrompt = ref('')
    let isSelecting = false

    // Configure marked options
    marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: false,
      mangle: false
    })

    // Function to safely render markdown
    const renderMarkdown = (text) => {
      if (!text) return ''
      const html = marked(text)
      return DOMPurify.sanitize(html)
    }

    // Remove any existing floating button from the DOM
    const removeExistingButton = () => {
      const existingButton = document.querySelector('.ai-floating-btn')
      if (existingButton) {
        existingButton.remove()
      }
    }

    // Create a floating button when text is selected
    const createFloatingButton = (selectedText, selectionRect) => {
      // First remove any existing button
      removeExistingButton()
      
      if (!selectedText || selectedText.trim().length < 5 || !aiStore.isEnabled) return
      
      const button = document.createElement('button')
      button.className = 'ai-floating-btn'
      button.textContent = 'AI Запрос'
      button.setAttribute('aria-label', 'Открыть AI запрос')
      
      // Position the button 40px above the selection
      button.style.position = 'absolute'
      button.style.top = `${selectionRect.top - 40}px`
      button.style.left = `${selectionRect.left}px`
      button.style.zIndex = '999'
      
      // Apply the same styles as in our component
      button.style.background = 'var(--accent-color)'
      button.style.color = 'white'
      button.style.border = 'none'
      button.style.padding = '8px 16px'
      button.style.borderRadius = '8px'
      button.style.cursor = 'pointer'
      button.style.fontFamily = "'Raleway', sans-serif"
      button.style.fontSize = '14px'
      button.style.fontWeight = '400'
      button.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)'
      button.style.transition = 'all 0.3s ease'
      button.style.transformOrigin = 'center bottom'
      
      // Hover effect
      button.onmouseover = () => {
        button.style.background = 'var(--hover-accent)'
        button.style.transform = 'translateY(-2px) scale(1.05)'
        button.style.boxShadow = '0 6px 15px rgba(0, 0, 0, 0.25)'
      }
      
      button.onmouseout = () => {
        button.style.background = 'var(--accent-color)'
        button.style.transform = 'none'
        button.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)'
      }
      
      // IMPORTANT: Direct DOM event handler for button click
      button.addEventListener('click', function(e) {
        e.preventDefault()
        e.stopPropagation()
        
        // This is the crucial part - set the text and open modal directly
        aiUserPrompt.value = selectedText
        aiStore.modalVisible = true
        
        // Clean up
        removeExistingButton()
      })
      
      document.body.appendChild(button)
      
      // Auto-hide on scroll
      const scrollHandler = () => {
        removeExistingButton()
        document.removeEventListener('scroll', scrollHandler)
      }
      
      document.addEventListener('scroll', scrollHandler, { passive: true })
    }
    
    // Mouse down handler to track selection start
    const handleMouseDown = (e) => {
      // Only track selection if not clicking on our button
      if (!e.target.closest('.ai-floating-btn')) {
        isSelecting = true
        removeExistingButton()
      }
    }
    
    // Mouse up handler for text selection
    const handleMouseUp = (e) => {
      // Don't process when clicking on our button
      if (e.target.closest('.ai-floating-btn')) {
        return
      }
      
      if (isSelecting) {
        setTimeout(() => {
          const selection = window.getSelection()
          if (!selection) return
          
          const text = selection.toString().trim()
          
          if (text.length > 5) {
            try {
              const range = selection.getRangeAt(0)
              if (!range) return
              
              const rect = range.getBoundingClientRect()
              
              // Account for scroll position
              const scrolledRect = {
                top: rect.top + window.scrollY,
                left: rect.left + window.scrollX,
                right: rect.right + window.scrollX,
                bottom: rect.bottom + window.scrollY
              }
              
              createFloatingButton(text, scrolledRect)
            } catch (e) {
              console.error('Error creating AI button:', e)
            }
          }
        }, 10)
      }
      isSelecting = false
    }

    // Handle click anywhere to remove button if it's not on the button itself
    const handleDocumentClick = (e) => {
      if (!e.target.closest('.ai-floating-btn') && !isSelecting) {
        removeExistingButton()
      }
    }

    const getCurrentTime = () => {
      const now = new Date();
      return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    const aiExplainText = () => {
      try {
        aiStore.askAI('Объясни простыми словами')
      } catch (error) {
        console.error('Error in aiExplainText:', error)
      }
    }

    const aiSimplifyText = () => {
      try {
        aiStore.askAI('Упрости текст для лучшего понимания')
      } catch (error) {
        console.error('Error in aiSimplifyText:', error)
      }
    }

    const aiAskCustom = () => {
      try {
        if (aiUserPrompt.value.trim()) {
          aiStore.askAI(aiUserPrompt.value)
          aiUserPrompt.value = ''
        } else {
          console.warn('Empty AI prompt')
        }
      } catch (error) {
        console.error('Error in aiAskCustom:', error)
      }
    }

    const closeAiModal = () => {
      try {
        aiStore.reset()
        aiUserPrompt.value = ''
        emit('close-modal')
      } catch (error) {
        console.error('Error in closeAiModal:', error)
      }
    }

    onMounted(() => {
      document.addEventListener('mousedown', handleMouseDown)
      document.addEventListener('mouseup', handleMouseUp)
      document.addEventListener('click', handleDocumentClick)
    })

    onUnmounted(() => {
      document.removeEventListener('mousedown', handleMouseDown)
      document.removeEventListener('mouseup', handleMouseUp)
      document.removeEventListener('click', handleDocumentClick)
      removeExistingButton()
    })

    return {
      aiStore,
      themeStore,
      aiUserPrompt,
      getCurrentTime,
      aiExplainText,
      aiSimplifyText,
      aiAskCustom,
      closeAiModal,
      renderMarkdown
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600;700&display=swap');

.ai-chat-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* Новый дизайн чата */
.chat-container {
  width: 500px;
  background: var(--form-background);
  border: 3px solid var(--accent-color);
  border-radius: 20px;
  font-family: 'Raleway', sans-serif;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  transition: background-color var(--transition-speed) var(--transition-timing),
              border-color var(--transition-speed) var(--transition-timing);
}

.chat-bubble-container {
  padding: 20px 30px;
  background: var(--accent-color);
  border-radius: 17px 17px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title-text-style {
  font-weight: 700;
  font-size: 16px;
  color: var(--text-color);
  margin: 0;
}

.ai-modal-close {
  background: var(--error-color);
  color: #f5f9f8;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-modal-close:hover {
  background: var(--hover-delete);
  transform: translateY(-1px);
}

.student-question-card {
  padding: 20px 15px;
  overflow-y: auto;
  flex-grow: 1;
}

.neural-response-container1 {
  margin-top: 20px;
}

.neural-response-container2 {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.neural-answer-container {
  width: 32px;
  height: 32px;
  margin-right: 10px;
  background: var(--accent-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f5f9f8;
  font-weight: bold;
  font-size: 14px;
}

.neural-response-container {
  background: var(--hover-background);
  border-radius: 10px;
  padding: 15px;
  max-width: 80%;
  position: relative;
  transition: background-color var(--transition-speed) var(--transition-timing);
}

.neural-response-text {
  font-size: 14px;
  color: var(--text-color);
  margin: 0;
  line-height: 1.4;
  white-space: pre-wrap;
  transition: color var(--transition-speed) var(--transition-timing);
}

.time-stamp-text-style {
  font-weight: 300;
  font-size: 10px;
  color: var(--secondary-text);
  margin: 10px 0 0;
  text-align: right;
  transition: color var(--transition-speed) var(--transition-timing);
}

.content-container1 {
  padding: 15px 0 0;
}

.border-divider-horizontal {
  border-top: 1px solid var(--accent-color);
  margin: 15px 0;
  transition: border-color var(--transition-speed) var(--transition-timing);
}

.content-wrapper2 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.question-prompt {
  font-size: 14px;
  color: var(--text-color);
  flex-grow: 1;
  padding: 12px 16px;
  background: var(--hover-background);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s, 
              color var(--transition-speed) var(--transition-timing), 
              background-color var(--transition-speed) var(--transition-timing);
}

.question-prompt:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.3);
}

.send-button {
  width: 45px;
  height: 45px;
  margin-left: 10px;
  background: var(--accent-color);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.send-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
}

.send-button:hover {
  background: var(--hover-accent);
  transform: translateY(-3px) scale(1.08);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.2);
}

.send-button:hover::before {
  opacity: 1;
}

.send-button:active {
  transform: translateY(1px) scale(0.95);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.send-icon {
  transition: transform 0.3s ease;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.send-button:hover .send-icon {
  transform: translate(1px, -1px) scale(1.1);
}

.ai-quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0;
  width: 100%;
}

.ai-action-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 400;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.ai-action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.ai-action-btn:hover {
  background: var(--hover-accent);
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
}

.ai-action-btn:hover::before {
  opacity: 1;
}

.ai-action-btn:active {
  transform: translateY(1px);
}

.ai-loading-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-color);
  font-style: italic;
  transition: color var(--transition-speed) var(--transition-timing);
}

.spinner {
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--accent-color);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background: var(--error-background);
  border-left: 4px solid var(--error-color);
  transition: background-color var(--transition-speed) var(--transition-timing);
}

.error-text {
  font-size: 14px;
  font-weight: 400;
  color: var(--error-color);
  margin: 0;
  transition: color var(--transition-speed) var(--transition-timing);
}

@media (max-width: 570px) {
  .chat-container {
    width: 90%;
    max-width: 450px;
    max-height: 90vh;
  }
  
  .ai-action-btn {
    font-size: 11px;
    padding: 6px 10px;
  }
  
  .neural-response-container {
    max-width: 90%;
  }
}

@media (max-width: 400px) {
  .chat-container {
    width: 95%;
  }
  
  .chat-bubble-container {
    padding: 15px 20px;
  }
  
  .ai-quick-actions {
    flex-direction: column;
  }
  
  .ai-action-btn {
    width: 100%;
  }
}

/* Add Markdown styles */
:deep(.neural-response-text) {
  font-size: 14px;
  color: var(--text-color);
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
  transition: color var(--transition-speed) var(--transition-timing);
}

:deep(.neural-response-text h1),
:deep(.neural-response-text h2),
:deep(.neural-response-text h3),
:deep(.neural-response-text h4),
:deep(.neural-response-text h5),
:deep(.neural-response-text h6) {
  margin: 1em 0 0.5em;
  color: var(--accent-color);
  font-weight: 600;
}

:deep(.neural-response-text h1) { font-size: 1.5em; }
:deep(.neural-response-text h2) { font-size: 1.3em; }
:deep(.neural-response-text h3) { font-size: 1.2em; }
:deep(.neural-response-text h4) { font-size: 1.1em; }
:deep(.neural-response-text h5) { font-size: 1em; }
:deep(.neural-response-text h6) { font-size: 0.9em; }

:deep(.neural-response-text p) {
  margin: 0.5em 0;
}

:deep(.neural-response-text ul),
:deep(.neural-response-text ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

:deep(.neural-response-text li) {
  margin: 0.3em 0;
}

:deep(.neural-response-text code) {
  background: var(--hover-background);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}

:deep(.neural-response-text pre) {
  background: var(--hover-background);
  padding: 1em;
  border-radius: 5px;
  overflow-x: auto;
  margin: 0.5em 0;
}

:deep(.neural-response-text pre code) {
  background: none;
  padding: 0;
  font-size: 0.9em;
}

:deep(.neural-response-text blockquote) {
  border-left: 3px solid var(--accent-color);
  margin: 0.5em 0;
  padding: 0.5em 1em;
  background: var(--hover-background);
  border-radius: 0 5px 5px 0;
}

:deep(.neural-response-text a) {
  color: var(--accent-color);
  text-decoration: none;
  transition: color 0.2s;
}

:deep(.neural-response-text a:hover) {
  text-decoration: underline;
}

:deep(.neural-response-text img) {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
  margin: 0.5em 0;
}

:deep(.neural-response-text table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}

:deep(.neural-response-text th),
:deep(.neural-response-text td) {
  border: 1px solid var(--border-color);
  padding: 0.5em;
  text-align: left;
}

:deep(.neural-response-text th) {
  background: var(--hover-background);
  font-weight: 600;
}

:deep(.neural-response-text hr) {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 1em 0;
}
</style> 