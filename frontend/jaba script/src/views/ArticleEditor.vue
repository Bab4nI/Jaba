<template>
  <div class="main-content-container">
    <!-- Add countdown timer -->
    <div v-if="timeRemaining > 0" class="countdown-timer">
      Осталось времени: {{ formatTimeRemaining(timeRemaining) }}
    </div>

    <!-- Toast notification -->
    <div v-if="toastMessage" class="toast-notification" :class="toastType">
      {{ toastMessage }}
    </div>

    <div class="central-content-container">
      <!-- Show loading indicator when content is loading -->
      <div v-if="isLoading && !loadError" class="loading-indicator">
        <div class="spinner"></div>
        <p>Загрузка содержимого...</p>
      </div>
      
      <!-- Show error message if there's an error -->
      <div v-else-if="loadError" class="error-message">
        {{ loadError }}
        <button @click="goBack" class="retry-button" aria-label="Вернуться к модулям">
          Вернуться к модулям
        </button>
      </div>
      
      <!-- Show content when loaded -->
      <div v-else class="main-content-container1">
        <ArticleHeader
          :title="article.title"
          :isEditMode="isEditMode"
          :isAdmin="userStore.role === 'admin'"
          :isTimeExpired="isTimeExpired"
          :previewMode="mode !== 'edit' || isTimeExpired"
          :aiEnabled="aiStore.isEnabled"
          @update:title="val => article.title = val"
          @toggle-mode="toggleMode"
          @go-back="goBack"
          @ai-toggle="aiStore.setAIEnabled"
          @title-click="handleTitleClick"
        />
        
        <!-- Custom Forms Container -->
        <div 
          v-for="(form, formIndex) in customForms" 
          :key="'form-'+formIndex" 
          class="custom-form-container"
          :class="{ 'active-form': activeFormIndex === formIndex && mode === 'edit' }"
          @click="mode === 'edit' ? selectForm(formIndex, $event) : null"
        >
          <div class="form-header">
            <input 
              v-model="form.title" 
              class="form-title" 
              :placeholder="isEditMode ? 'Название формы' : ''"
              :readonly="!isEditMode"
              :disabled="!isEditMode"
              @click.stop
              @input="onFormTitleChange(formIndex)"
              @blur="onFormTitleBlur(formIndex)"
              @focus="onFormTitleFocus(formIndex)"
            />
            <div class="form-controls" v-if="isEditMode">
              <button @click.stop="removeForm(formIndex)" class="remove-form-btn" aria-label="Удалить форму">×</button>
            </div>
          </div>

          <!-- Form Content Blocks -->
          <div v-if="mode === 'edit' && userStore.role === 'admin'" class="editable-content" @click.stop="activeFormIndex = formIndex">
            <ContentBlock
              v-for="(element, elementIndex) in form.contents"
              :key="element.id || `form-${formIndex}-element-${elementIndex}`"
              :content="element"
              :read-only="isContentReadOnly"
              :is-time-expired="isTimeExpired"
              :is-first="elementIndex === 0"
              :is-last="elementIndex === form.contents.length - 1"
              @update:content="onFormContentUpdate(formIndex, elementIndex, $event)"
              @move-up="moveFormContentUp(formIndex, elementIndex)"
              @move-down="moveFormContentDown(formIndex, elementIndex)"
              @remove="removeFormContent(formIndex, elementIndex)"
              @answer-submitted="onAnswerSubmitted"
            />
          </div>
          <div v-else class="preview-content">
            <ContentBlock
              v-for="(element, elementIndex) in form.contents"
              :key="element.id || elementIndex"
              :content="element"
              :read-only="true"
              :is-time-expired="isTimeExpired"
              :allow-preview-edit="userStore.role === 'admin' && element.type === 'code'"
              @update:content="onFormContentUpdate(formIndex, elementIndex, $event)"
              @answer-submitted="onAnswerSubmitted"
            />
          </div>
        </div>

        <div v-if="mode === 'edit' && userStore.role === 'admin'" class="editor-toolbar">
          <div class="toolbar-content">
            <button
              @click="openBlockModal"
              class="add-content-btn"
              :class="{ 'form-selected': activeFormIndex >= 0, 'disabled': activeFormIndex < 0 }"
              :disabled="activeFormIndex < 0"
              aria-label="Добавить новый элемент"
            >
              <span class="btn-icon">+</span>
              {{ activeFormIndex >= 0 ? `Добавить в ${customForms[activeFormIndex]?.title ? '"' + customForms[activeFormIndex].title + '"' : 'форму'}` : 'Выберите форму' }}
            </button>

            <button
              @click="createNewForm" 
              class="create-form-btn"
              aria-label="Создать форму"
            >
              <span class="btn-icon">📋</span>
              Создать форму
            </button>

            <button
              @click="resetLessonProgress" 
              class="reset-progress-btn"
              :disabled="isSaving"
            >
              <span class="btn-icon">🔄</span> Сбросить прогресс
            </button>

            <button
              @click="saveAllChanges"
              class="save-button"
              aria-label="Сохранить все изменения"
            >
              <span v-if="isSaving" class="spinner"></span>
              <span v-else class="btn-icon">💾</span>
              {{ isSaving ? 'Сохранение...' : 'Сохранить работу' }}
              <span v-if="hasChanges" class="changes-indicator">*</span>
            </button>
          </div>
        </div>
        
        <!-- Progress tracking button at the bottom -->
        <div class="progress-tracking-container">
          <div class="score-summary" v-if="lessonScore.total > 0 || lessonScore.max > 0">
            <span class="score-label">Текущий счет:</span>
            <span class="score-value" :class="{'score-success': lessonScore.total === lessonScore.max && lessonScore.max > 0, 'score-partial': lessonScore.total > 0 && lessonScore.total < lessonScore.max}">
              {{ lessonScore.total }}/{{ lessonScore.max }}
            </span>
            <!-- Кнопка 'Отметить урок как пройденный' убрана -->
          </div>
        </div>
      </div>
    </div>

    <div class="dark-purple-flex-container">
      <Comments />
    </div>

    <!-- Error Message for Content Loading -->
    <div v-if="loadError" class="error-message">
      {{ loadError }}
      <button @click="goBack" class="retry-button" aria-label="Вернуться к модулям">
        Вернуться к модулям
      </button>
    </div>

    <!-- AI Chat Component -->
    <AIChat 
      :selected-text="selectedText"
      @show-toast="showToast"
      @close-modal="closeAiModalButton"
    />

    <!-- Toast Notifications -->
    <transition name="fade">
      <div v-if="toastMessage" class="toast" :class="toastType" role="alert">
        {{ toastMessage }}
        <button class="toast-close" @click="toastMessage = ''" aria-label="Закрыть уведомление">
          ×
        </button>
      </div>
    </transition>

    <!-- Block Creation Modal -->
    <div v-if="showBlockModal" class="block-modal" role="dialog" aria-labelledby="block-modal-title">
      <div class="block-modal-container">
        <div class="block-modal-header">
          <h3 id="block-modal-title" class="main-heading-style">Добавить новый элемент</h3>
          <button class="modal-close" @click="closeBlockModal" aria-label="Закрыть модальное окно">×</button>
        </div>
        <div class="block-modal-content">
          <div class="block-type-selection">
            <div 
              v-for="type in blockTypes" 
              :key="type.value"
              class="block-type-card"
              @click="addNewBlock(type.value)"
            >
              <span class="block-icon">{{ type.icon }}</span>
              <span class="block-title">{{ type.label }}</span>
              <span class="block-description">{{ type.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAIStore } from '@/stores/aiStore'
import { useRefreshStore } from '@/stores/auth'
import api from '@/api'
import { debounce } from 'lodash-es'
import ContentBlock from '@/components/article/ContentBlock.vue'
import Comments from '@/components/Comments.vue'
import AIChat from '@/components/AiChat.vue'
import ArticleHeader from '@/components/ArticleHeader.vue'

const CONTENT_TYPES = {
  text: 'TEXT',
  image: 'IMAGE',
  video: 'VIDEO',
  code: 'CODE',
  quiz: 'QUIZ',
  table: 'TABLE',
  file: 'FILE',
  form: 'FORM',
  fillin: 'FILLIN',
}

// Add form type to our content types
const FORM_TYPE = 'CUSTOM_FORM';

const DEFAULT_CONTENT = {
  text: { text: '', readOnly: false, max_score: 1 },
  image: { image: null, readOnly: false, max_score: 1 },
  video: { video_url: '', readOnly: false, max_score: 5 },
  code: { code: '', language: 'javascript', readOnly: false, max_score: 10 },
  quiz: { question: '', answers: ['', ''], correct_answer: null, readOnly: false, max_score: 2 },
  table: { headers: ['Заголовок 1', 'Заголовок 2'], data: [['', ''], ['', '']], readOnly: false, max_score: 1 },
  file: { file: null, filename: null, readOnly: false, max_score: 1 },
  form: { fields: [], readOnly: false, max_score: 1 },
  fillin: { text: '', answers: [], readOnly: false, max_score: 1 },
}

const BLOCK_TYPES = [
  {
    value: 'text',
    label: 'Текст',
    icon: '📝',
    description: 'Добавить текстовый блок'
  },
  {
    value: 'image',
    label: 'Изображение',
    icon: '🖼️',
    description: 'Добавить изображение'
  },
  {
    value: 'video',
    label: 'Видео',
    icon: '🎥',
    description: 'Добавить видео'
  },
  {
    value: 'code',
    label: 'Код',
    icon: '💻',
    description: 'Добавить блок кода'
  },
  {
    value: 'quiz',
    label: 'Тест',
    icon: '❓',
    description: 'Добавить тестовый вопрос'
  },
  {
    value: 'table',
    label: 'Таблица',
    icon: '📊',
    description: 'Добавить таблицу'
  },
  {
    value: 'file',
    label: 'Файл',
    icon: '📎',
    description: 'Добавить файл для скачивания'
  },
  {
    value: 'fillin',
    label: 'Пропущенное слово',
    icon: '✏️',
    description: 'Добавить задание на вставку пропущенного слова'
  }
]

// Function to generate a unique ID for forms and content
const generateUniqueId = () => {
  return 'temp_' + Date.now() + '_' + Math.floor(Math.random() * 1000000)
}

// Add mock backend support for forms since endpoints may not exist yet
const useLocalStorage = ref(true) // Set to false when backend endpoints are ready

export default {
  components: {
    ContentBlock,
    Comments,
    AIChat,
    ArticleHeader,
  },

  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    const aiStore = useAIStore()
    const refreshStore = useRefreshStore()

    const article = ref({
      id: route.params.lessonId,
      title: route.query.title || 'Новая работа',
      type: route.query.type || 'article',
    })

    // Add isLoading state to track loading status
    const isLoading = ref(true)
    const selectedContentType = ref('')
    const contents = ref([])
    const originalContents = ref([])
    const changedIndices = ref(new Set())
    const mode = ref('preview')
    const aiUserPrompt = ref('')
    const loadError = ref(null)
    const showAIButton = ref(false)
    const selectedText = ref('')
    const aiButtonPosition = ref({ top: '0px', left: '0px' })
    const isSaving = ref(false)
    const toastMessage = ref('')
    const toastType = ref('success')
    const lastSavedAt = ref(null)
    const showBlockModal = ref(false)
    const selectedBlockType = ref('')
    const blockTypes = ref(BLOCK_TYPES)
    const customForms = ref([])
    const currentFormIndex = ref(-1)
    const activeFormIndex = ref(-1)
    const isLessonCompleted = ref(false)
    const timeRemaining = ref(0)
    const countdownInterval = ref(null)
    const isTimeExpired = ref(false)
    
    // Calculate total maximum score based on all content elements
    const maxScore = computed(() => {
      let total = 0;
      
      // Add scores from main contents
      contents.value.forEach(content => {
        const disabledTypes = ['text', 'image', 'table', 'file'];
        if (!disabledTypes.includes(content.type)) {
          const contentMaxScore = parseInt(content.max_score) || 1;
          total += contentMaxScore;
        }
      });
      
      // Add scores from forms
      customForms.value.forEach(form => {
        form.contents.forEach(content => {
          const disabledTypes = ['text', 'image', 'table', 'file'];
          if (!disabledTypes.includes(content.type)) {
            const contentMaxScore = parseInt(content.max_score) || 1;
            total += contentMaxScore;
          }
        });
      });
      
      return total;
    });
    
    // Calculate current score based on user_score values
    const totalScore = computed(() => {
      let total = 0;
      
      // Add scores from main contents
      contents.value.forEach(content => {
        if (content.user_score !== undefined) {
          total += parseInt(content.user_score) || 0;
        }
      });
      
      // Add scores from forms
      customForms.value.forEach(form => {
        form.contents.forEach(content => {
          if (content.user_score !== undefined) {
            total += parseInt(content.user_score) || 0;
          }
        });
      });
      
      return total;
    });
    
    // Create a reactive lessonScore object using the computed properties
    const lessonScore = computed(() => {
      return {
        total: totalScore.value,
        max: maxScore.value
      };
    });

    const isContentReadOnly = computed(() => {
      return mode.value !== 'edit' || userStore.role !== 'admin'
    })

    const isEditMode = computed(() => {
      return mode.value === 'edit' && userStore.role === 'admin'
    })

    const hasChanges = computed(() => {
      return changedIndices.value.size > 0
    })

    const showToast = (message, type = 'success') => {
      toastMessage.value = message
      toastType.value = type
      setTimeout(() => {
        toastMessage.value = ''
      }, 5000)
    }

    const onContentUpdate = debounce((index, updatedContent) => {
      const currentContent = contents.value[index];
      
      // Update the content
      contents.value[index] = {
        ...currentContent,
        ...updatedContent,
        updated_at: new Date().toISOString()
      };
      
      changedIndices.value.add(index);
      
      // Save the updated score to localStorage
      saveScoreToLocalStorage();
    }, 500);

    const handleTextSelection = (text, event) => {
      if (text && text.trim().length > 5) {
        selectedText.value = text
        showAIButton.value = true

        if (event) {
          const rect = event.target.getBoundingClientRect()
          aiButtonPosition.value = {
            top: `${rect.bottom + window.scrollY + 10}px`,
            left: `${rect.left + window.scrollX}px`,
          }
        }
      } else {
        showAIButton.value = false
      }
    }

    const insertAiResponseFromComponent = (response) => {
      const activeTextElement = contents.value.find((c) => c.type === 'text')
      if (activeTextElement) {
        activeTextElement.text += `\n\n${response}`
        const index = contents.value.indexOf(activeTextElement)
        changedIndices.value.add(index)
      } else {
        const newContent = {
          type: 'text',
          text: response,
          order: contents.value.length + 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        contents.value.push(newContent)
        changedIndices.value.add(contents.value.length - 1)
      }
      showToast('Ответ AI вставлен в статью.', 'success')
    }

    const closeAiModalButton = () => {
      showAIButton.value = false
    }

    const copyAiResponse = () => {
      navigator.clipboard.writeText(aiStore.aiResponse)
      showToast('Ответ скопирован в буфер обмена.', 'success')
    }

    const closeAiModal = () => {
      aiStore.reset()
      aiUserPrompt.value = ''
      showAIButton.value = false
    }
    
    // Add the missing AI-related functions
    const openAIModal = () => {
      aiStore.setSelectedText(selectedText.value)
      aiStore.modalVisible = true
    }
    
    const aiExplainText = () => {
      aiStore.askAI('Объясни простыми словами')
    }
    
    const aiSimplifyText = () => {
      aiStore.askAI('Упрости текст для лучшего понимания')
    }
    
    const aiExpandText = () => {
      aiStore.askAI('Расширь и дополни текст')
    }
    
    const aiAskCustom = () => {
      if (aiUserPrompt.value.trim()) {
        aiStore.askAI(aiUserPrompt.value)
      } else {
        showToast('Введите запрос для AI.', 'error')
      }
    }
    
    const insertAiResponse = () => {
      const activeTextElement = contents.value.find((c) => c.type === 'text')
      if (activeTextElement) {
        activeTextElement.text += `\n\n${aiStore.aiResponse}`
        const index = contents.value.indexOf(activeTextElement)
        changedIndices.value.add(index)
      } else {
        const newContent = {
          type: 'text',
          text: aiStore.aiResponse,
          order: contents.value.length + 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        contents.value.push(newContent)
        changedIndices.value.add(contents.value.length - 1)
      }
      closeAiModal()
      showToast('Ответ AI вставлен в статью.', 'success')
    }

    const getContentTypeName = (type) => {
      const types = {
        text: 'Текст',
        image: 'Изображение',
        video: 'Видео',
        code: 'Код',
        quiz: 'Тест',
        table: 'Таблица',
        file: 'Файл',
        form: 'Форма',
        fillin: 'Задание на вставку пропущенного слова',
      }
      return types[type] || type
    }

    const getContentComponent = (type) => {
      const components = {
        text: 'TextElement',
        image: 'ImageElement',
        video: 'VideoElement',
        code: 'CodeElement',
        quiz: 'QuizElement',
        table: 'TableElement',
        file: 'FileElement',
        form: 'FormElement',
        fillin: 'FillinElement',
      }
      return components[type] || 'TextElement'
    }

    const addContent = () => {
      if (!selectedContentType.value) return

      const newContent = {
        id: null,
        type: selectedContentType.value,
        order: contents.value.length + 1,
        ...JSON.parse(JSON.stringify(DEFAULT_CONTENT[selectedContentType.value])),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      contents.value.push(newContent)
      changedIndices.value.add(contents.value.length - 1)
      selectedContentType.value = ''
      showToast('Новый элемент добавлен.', 'success')
    }

    const removeContent = async (index) => {
      if (!confirm('Вы уверены, что хотите удалить этот элемент?')) return

      const content = contents.value[index]
      if (content.id) {
        try {
          await api.delete(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/${content.id}/`)
          showToast('Элемент удален.', 'success')
        } catch (error) {
          console.error('Ошибка удаления контента:', error)
          showToast('Не удалось удалить элемент.', 'error')
          return
        }
      }
      contents.value.splice(index, 1)
      changedIndices.value.delete(index)
      const newIndices = new Set()
      changedIndices.value.forEach(i => {
        if (i > index) newIndices.add(i - 1)
        else if (i < index) newIndices.add(i)
      })
      changedIndices.value = newIndices
      updateContentOrder()
    }

    const moveContentUp = (index) => {
      if (index > 0) {
        const temp = contents.value[index]
        contents.value[index] = contents.value[index - 1]
        contents.value[index - 1] = temp
        changedIndices.value.add(index)
        changedIndices.value.add(index - 1)
        updateContentOrder()
      }
    }

    const moveContentDown = (index) => {
      if (index < contents.value.length - 1) {
        const temp = contents.value[index]
        contents.value[index] = contents.value[index + 1]
        contents.value[index + 1] = temp
        changedIndices.value.add(index)
        changedIndices.value.add(index + 1)
        updateContentOrder()
      }
    }

    const updateContentOrder = () => {
      contents.value.forEach((content, index) => {
        content.order = index + 1
        changedIndices.value.add(index)
      })
    }
    
    const saveOrder = async () => {
      const orderedIds = contents.value
        .filter((content) => content.id)
        .map((content, index) => ({
          id: content.id,
          order: index + 1,
        }))

      if (orderedIds.length === 0) return

      try {
        await api.patch(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/order/`, {
          order: orderedIds,
        })
        showToast('Порядок элементов сохранен.', 'success')
      } catch (error) {
        console.error('Ошибка сохранения порядка:', error)
        showToast('Не удалось сохранить порядок элементов.', 'error')
      }
    }

    const saveAllChanges = async () => {
      isSaving.value = true
      const errors = []

      try {
        const courseSlug = route.params.courseSlug
        const moduleId = route.params.moduleId
        const lessonId = route.params.lessonId

        // Save article title
        await api.patch(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/`, {
          title: article.value.title
        })

        // Save main contents
        const contentPromises = contents.value.map(async (content, index) => {
          content.order = index + 1
          if (content.id) {
            return api.patch(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/contents/${content.id}/`, content)
          } else {
            return api.post(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/contents/`, content)
          }
        })

        await Promise.all(contentPromises)

        // Save forms (no localStorage, only server)
        for (const form of customForms.value) {
          const formData = {
            title: form.title || 'Новая форма',
            contents: form.contents || [],
          }
          if (typeof form.id === 'number') {
            // PATCH если id числовой
            await api.patch(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/forms/${form.id}/`, formData)
          } else {
            // POST если id нет или временный
            const response = await api.post(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/forms/`, formData)
            form.id = response.data.id
          }
        }

        changedIndices.value.clear()
        lastSavedAt.value = new Date()
        await saveScoreToServer()
        if (mode.value === 'edit') {
          toggleMode()
        }
        showToast('Все изменения успешно сохранены', 'success')
      } catch (error) {
        console.error('Ошибка сохранения работы:', error)
        showToast(`Ошибка при сохранении: ${error.message}`, 'error')
      } finally {
        isSaving.value = false
      }
    }

    // Function to save the current score to server or local storage
    const saveScoreToServer = async () => {
      try {
        const lessonId = route.params.lessonId

        await api.post(`/lessons/${lessonId}/mark-completed/`, {
          lesson_id: lessonId,
          max_score: maxScore.value,
          current_score: totalScore.value
        })

        console.log(`Saved score to server: ${totalScore.value}/${maxScore.value}`)
      } catch (error) {
        console.warn('Error saving score to server, using local storage:', error)
        // Fallback to local storage
        localStorage.setItem(`lesson_score_${lessonId}`, JSON.stringify({
          total: totalScore.value,
          max: maxScore.value
        }))
      }
    }

    const goBack = async () => {
      if (hasChanges.value) {
        if (!confirm('У вас есть несохраненные изменения. Хотите выйти без сохранения?')) {
          return
        }
      }
      try {
        await router.push(`/courses/${route.params.courseSlug}`)
      } catch (error) {
        console.error('Navigation to course failed:', error)
        showToast('Не удалось вернуться к курсу.', 'error')
        router.push('/')
      }
    }
    
    const toggleMode = () => {
      if (userStore.role === 'admin') {
        mode.value = mode.value === 'edit' ? 'preview' : 'edit'
        
        // Clear active form selection when switching to preview mode
        if (mode.value === 'preview') {
          activeFormIndex.value = -1;
        }
        
        // Remove the mode change toast
        // showToast(`Режим изменен на ${mode.value === 'edit' ? 'редактирование' : 'предпросмотр'}.`, 'info')
      }
    }
    
    const handleGlobalTextSelection = (event) => {
      const selection = window.getSelection()
      const text = selection.toString().trim()
      handleTextSelection(text, event)
    }
    
    const beforeUnloadHandler = (e) => {
      if (hasChanges.value) {
        e.preventDefault()
        e.returnValue = 'У вас есть несохраненные изменения. Вы уверены, что хотите уйти?'
        return e.returnValue
      }
    }

    const openBlockModal = () => {
      // Check if a form is currently selected
      if (activeFormIndex.value >= 0) {
        currentFormIndex.value = activeFormIndex.value;
        showBlockModal.value = true;
        selectedBlockType.value = '';
        showToast(`Добавление элемента в форму "${customForms.value[activeFormIndex.value].title}"`, 'info');
      } else {
        // If no form is selected, show a message to select a form first
        showToast('Пожалуйста, выберите форму перед добавлением элемента', 'warning');
      }
    }

    const closeBlockModal = () => {
      showBlockModal.value = false
      selectedBlockType.value = ''
    }

    const createNewForm = () => {
      const newForm = {
        id: generateUniqueId(),
        title: 'Новая форма',
        contents: [],
        total: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      customForms.value.push(newForm)
      activeFormIndex.value = customForms.value.length - 1
      showToast('Новая форма создана.', 'success')
    }

    const removeForm = async (index) => {
      if (!confirm('Вы уверены, что хотите удалить эту форму?')) return
      const form = customForms.value[index]
      try {
        if (form && typeof form.id === 'number') {
          const courseSlug = route.params.courseSlug
          const moduleId = route.params.moduleId
          const lessonId = route.params.lessonId
          await api.delete(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/forms/${form.id}/`)
        }
      } catch (error) {
        showToast('Ошибка при удалении формы', 'error')
        return
      }
      customForms.value.splice(index, 1)
      if (activeFormIndex.value === index) {
        activeFormIndex.value = -1
      } else if (activeFormIndex.value > index) {
        activeFormIndex.value--
      }
      showToast('Форма удалена.', 'success')
    }

    const onFormContentUpdate = (formIndex, contentIndex, updatedContent) => {
      if (!customForms.value[formIndex]) return
      
      const currentContent = customForms.value[formIndex].contents[contentIndex]
      if (!currentContent) return
      
      // Update the content
      customForms.value[formIndex].contents[contentIndex] = {
        ...currentContent,
        ...updatedContent,
        updated_at: new Date().toISOString()
      }
      
      // Update total
      customForms.value[formIndex].total = customForms.value[formIndex].contents.length
      
      // Save the updated score to localStorage
      saveScoreToLocalStorage()
    }

    const moveFormContentUp = (formIndex, contentIndex) => {
      if (contentIndex > 0) {
        const temp = customForms.value[formIndex].contents[contentIndex]
        customForms.value[formIndex].contents[contentIndex] = customForms.value[formIndex].contents[contentIndex - 1]
        customForms.value[formIndex].contents[contentIndex - 1] = temp
        updateFormContentOrder(formIndex)
      }
    }

    const moveFormContentDown = (formIndex, contentIndex) => {
      if (contentIndex < customForms.value[formIndex].contents.length - 1) {
        const temp = customForms.value[formIndex].contents[contentIndex]
        customForms.value[formIndex].contents[contentIndex] = customForms.value[formIndex].contents[contentIndex + 1]
        customForms.value[formIndex].contents[contentIndex + 1] = temp
        updateFormContentOrder(formIndex)
      }
    }

    const removeFormContent = (formIndex, contentIndex) => {
      if (!confirm('Вы уверены, что хотите удалить этот элемент?')) return
      if (!customForms.value[formIndex]) return
      
      customForms.value[formIndex].contents.splice(contentIndex, 1)
      customForms.value[formIndex].total = customForms.value[formIndex].contents.length
      updateFormContentOrder(formIndex)
      showToast('Элемент удален.', 'success')
    }

    const updateFormContentOrder = (formIndex) => {
      customForms.value[formIndex].contents.forEach((content, index) => {
        content.order = index + 1
      })
    }

    const openFormBlockModal = (formIndex) => {
      currentFormIndex.value = formIndex
      showBlockModal.value = true
    }

    const selectForm = (index, event) => {
      if (event) {
        event.stopPropagation()
      }
      activeFormIndex.value = index
    }

    const onFormTitleChange = (index) => {
      customForms.value[index].updated_at = new Date().toISOString()
    }

    const onFormTitleBlur = (index) => {
      if (!customForms.value[index].title || customForms.value[index].title.trim() === '') {
        customForms.value[index].title = 'Новая форма'
      }
    }

    const onFormTitleFocus = (index) => {
      activeFormIndex.value = index
    }

    const onAnswerSubmitted = (contentId, score) => {
      // Handle both formats: direct score value or object with score property
      let numericScore = 0
      let actualContentId = contentId
      
      if (typeof contentId === 'object' && contentId !== null) {
        // New format: object with contentId and score properties
        numericScore = parseInt(contentId.score) || 0
        actualContentId = contentId.contentId
        console.log(`Answer submitted in object format for content ${actualContentId} with score ${numericScore}`)
      } else {
        // Old format: direct contentId and score
        numericScore = parseInt(score) || 0
        console.log(`Answer submitted in direct format for content ${contentId} with score ${numericScore}`)
      }
      
      // Find the content in either main contents or forms
      let contentFound = false
      
      // Check in main contents
      for (let i = 0; i < contents.value.length; i++) {
        if (contents.value[i].id === actualContentId) {
          // Update the user_score property
          console.log(`Found content in main contents, updating score from ${contents.value[i].user_score} to ${numericScore}`)
          contents.value[i].user_score = numericScore
          contentFound = true
          break
        }
      }
      
      // If not found in main contents, check in forms
      if (!contentFound) {
        for (const form of customForms.value) {
          for (let i = 0; i < form.contents.length; i++) {
            if (form.contents[i].id === actualContentId) {
              // Update the user_score property
              console.log(`Found content in form, updating score from ${form.contents[i].user_score} to ${numericScore}`)
              form.contents[i].user_score = numericScore
              contentFound = true
              break
            }
          }
          if (contentFound) break
        }
      }
      
      if (!contentFound) {
        console.warn(`Content with ID ${actualContentId} not found in any form or main content`)
      }
      
      // Save the updated score to server
      saveScoreToServer()
    }

    const resetLessonProgress = async () => {
      if (!confirm('Вы уверены, что хотите сбросить весь прогресс по этому уроку?')) return
      
      try {
        isSaving.value = true
        const lessonId = route.params.lessonId
        
        // Reset progress on server
        await api.post(`/lessons/${lessonId}/reset-progress/`, {
          lesson_id: lessonId
        })
        
        // Reset local state
        isLessonCompleted.value = false
        
        // Reset all form content answers
        customForms.value.forEach(form => {
          form.contents.forEach(content => {
            if (content.type === 'quiz' && content.user_answer) {
              delete content.user_answer
            }
            if (content.user_score !== undefined) {
              delete content.user_score
            }
          })
        })
        
        // Reset user_score for main contents
        contents.value.forEach(content => {
          if (content.user_score !== undefined) {
            delete content.user_score
          }
        })
        
        showToast('Прогресс урока успешно сброшен', 'success')
      } catch (error) {
        console.error('Error resetting lesson progress:', error)
        showToast('Не удалось сбросить прогресс урока', 'error')
      } finally {
        isSaving.value = false
      }
    }

    // Function to save the current score to localStorage
    const saveScoreToLocalStorage = () => {
      try {
        localStorage.setItem(`lesson_score_${article.value.id}`, JSON.stringify({
          total: totalScore.value,
          max: maxScore.value
        }));
        console.log(`Saved score to localStorage: ${totalScore.value}/${maxScore.value}`);
      } catch (error) {
        console.error('Error saving score to localStorage:', error);
      }
    };

    const formatTimeRemaining = (ms) => {
      const seconds = Math.floor(ms / 1000)
      const minutes = Math.floor(seconds / 60)
      const hours = Math.floor(minutes / 60)
      const days = Math.floor(hours / 24)

      const remainingHours = hours % 24
      const remainingMinutes = minutes % 60
      const remainingSeconds = seconds % 60

      let result = ''
      if (days > 0) result += `${days} д. `
      if (remainingHours > 0) result += `${remainingHours} ч. `
      if (remainingMinutes > 0) result += `${remainingMinutes} мин. `
      if (remainingSeconds > 0 && minutes === 0) result += `${remainingSeconds} сек.`

      return result.trim()
    }

    const startCountdown = (endTime) => {
      if (!endTime) return
      
      // Clear any existing interval
      if (countdownInterval.value) {
        clearInterval(countdownInterval.value)
      }
      
      const updateCountdown = () => {
        const now = new Date()
        const end = new Date(endTime)
        const diff = end - now

        if (diff <= 0) {
          timeRemaining.value = 0
          isTimeExpired.value = true
          clearInterval(countdownInterval.value)
          mode.value = 'preview' // Switch to preview mode when time expires
          showToast('Время истекло. Редактирование недоступно.', 'info')
          return
        }

        timeRemaining.value = diff
      }

      // Initial update
      updateCountdown()
      
      // Update every second
      countdownInterval.value = setInterval(updateCountdown, 1000)
    }

    // Add method to refresh time
    const refreshTime = async () => {
      try {
        const courseSlug = route.params.courseSlug
        const moduleId = route.params.moduleId
        const lessonId = route.params.lessonId
        
        const lessonResponse = await api.get(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/`)
        if (lessonResponse.data.end_datetime) {
          startCountdown(lessonResponse.data.end_datetime)
        }
      } catch (error) {
        console.error('Error refreshing time:', error)
      }
    }

    // Watch for changes in mode to prevent editing when time expires
    watch(timeRemaining, (newValue) => {
      if (newValue === 0 && mode.value === 'edit') {
        mode.value = 'preview'
      }
    })

    // Add interval to refresh time every minute
    let timeRefreshInterval = null

    // Load article content when component is mounted
    onMounted(async () => {
      try {
        isLoading.value = true
        loadError.value = null
        
        // First, ensure we have valid tokens
        const authStore = useRefreshStore()
        const isReady = await authStore.ready()
        
        if (!isReady) {
          throw new Error('Authentication required. Please log in again')
        }
        
        const courseSlug = route.params.courseSlug
        const moduleId = route.params.moduleId
        const lessonId = route.params.lessonId
        
        if (!courseSlug || !moduleId || !lessonId) {
          throw new Error('Отсутствуют необходимые параметры (курс, модуль или урок)')
        }

        // Load all required data in parallel
        try {
          const [lessonResponse, contentResponse, formsResponse, progressResponse] = await Promise.all([
            // Get lesson details including end time
            api.get(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/`),
            // Load lesson content
            api.get(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/contents/`),
            // Load custom forms - explicitly call the forms endpoint
            api.get(`/courses/${courseSlug}/modules/${moduleId}/lessons/${lessonId}/forms/`).catch(error => {
              console.warn('Error loading forms:', error);
              // Return empty array as fallback
              return { data: [] };
            }),
            // Check lesson progress
            api.get(`/lessons/${lessonId}/progress/`)
          ])

          // Process lesson response
          if (lessonResponse.data.end_datetime) {
            startCountdown(lessonResponse.data.end_datetime)
          }
          article.value.title = lessonResponse.data.title || 'Новая работа'
          
          // Process content response
          contents.value = contentResponse.data.sort((a, b) => a.order - b.order)
          originalContents.value = JSON.parse(JSON.stringify(contents.value))
          
          // Process forms response with better error handling
          if (formsResponse.data && Array.isArray(formsResponse.data)) {
            customForms.value = formsResponse.data.map(form => ({
              ...form,
              contents: Array.isArray(form.contents) ? form.contents : [],
              total: Array.isArray(form.contents) ? form.contents.length : 0
            }))
            console.log('Successfully loaded forms:', customForms.value)
          } else {
            console.warn('No forms data received from server, checking localStorage')
            // Try to load from localStorage as fallback
            const savedForms = localStorage.getItem(`lesson_forms_${lessonId}`)
            if (savedForms) {
              try {
                const parsedForms = JSON.parse(savedForms)
                customForms.value = parsedForms.map(form => ({
                  ...form,
                  contents: Array.isArray(form.contents) ? form.contents : [],
                  total: Array.isArray(form.contents) ? form.contents.length : 0
                }))
                console.log('Loaded forms from localStorage:', customForms.value)
              } catch (e) {
                console.error('Error parsing forms from localStorage:', e)
                customForms.value = []
              }
            } else {
              customForms.value = []
            }
          }
          
          // Process progress response
          isLessonCompleted.value = progressResponse.data.completed
          
          // Set up interval to refresh time every minute
          timeRefreshInterval = setInterval(refreshTime, 60000)

        } catch (error) {
          console.error('Error loading article content:', error)
          if (error.message === 'Authentication required. Please log in again.') {
            loadError.value = 'Требуется авторизация. Пожалуйста, войдите снова.'
            setTimeout(() => {
              router.push('/signin')
            }, 2000)
          } else {
            loadError.value = error.response?.data?.detail || error.message || 'Ошибка загрузки содержимого'
            
            // Try to load from localStorage as fallback
            const savedForms = localStorage.getItem(`lesson_forms_${lessonId}`)
            if (savedForms) {
              try {
                const parsedForms = JSON.parse(savedForms)
                customForms.value = parsedForms.map(form => ({
                  ...form,
                  contents: Array.isArray(form.contents) ? form.contents : [],
                  total: Array.isArray(form.contents) ? form.contents.length : 0
                }))
                console.log('Loaded forms from localStorage:', customForms.value)
              } catch (e) {
                console.error('Error parsing forms from localStorage:', e)
                customForms.value = []
              }
            }
          }
        } finally {
          isLoading.value = false
        }

      } catch (error) {
        console.error('Error loading article content:', error)
        if (error.message === 'Authentication required. Please log in again.') {
          loadError.value = 'Требуется авторизация. Пожалуйста, войдите снова.'
          setTimeout(() => {
            router.push('/signin')
          }, 2000)
        } else {
          loadError.value = error.response?.data?.detail || error.message || 'Ошибка загрузки содержимого'
          
          // Try to load from localStorage as fallback
          const savedForms = localStorage.getItem(`lesson_forms_${lessonId}`)
          if (savedForms) {
            try {
              const parsedForms = JSON.parse(savedForms)
              customForms.value = parsedForms.map(form => ({
                ...form,
                contents: Array.isArray(form.contents) ? form.contents : [],
                total: Array.isArray(form.contents) ? form.contents.length : 0
              }))
              console.log('Loaded forms from localStorage:', customForms.value)
            } catch (e) {
              console.error('Error parsing forms from localStorage:', e)
              customForms.value = []
            }
          }
        }
      } finally {
        isLoading.value = false
      }
    })

    // Clean up intervals when component is unmounted
    onUnmounted(() => {
      if (countdownInterval.value) {
        clearInterval(countdownInterval.value)
      }
      if (timeRefreshInterval) {
        clearInterval(timeRefreshInterval)
      }
    })

    const handleTitleClick = (e) => {
      if (mode.value !== 'edit') {
        e.preventDefault();
        e.stopPropagation();
        showToast('Переключитесь в режим редактирования, чтобы изменить название работы', 'info');
      }
    }

    const addNewBlock = (type) => {
      if (!type) return
      const newContent = {
        id: generateUniqueId(),
        type,
        order: contents.value.length + 1,
        ...JSON.parse(JSON.stringify(DEFAULT_CONTENT[type])),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      if (currentFormIndex.value >= 0) {
        const formIndex = currentFormIndex.value
        if (!customForms.value[formIndex]) return
        
        newContent.order = customForms.value[formIndex].contents.length + 1
        customForms.value[formIndex].contents.push(newContent)
        customForms.value[formIndex].total = customForms.value[formIndex].contents.length
        updateFormContentOrder(formIndex)
        showToast(`Элемент "${getContentTypeName(type)}" добавлен в форму "${customForms.value[formIndex].title}"`, 'success')
        currentFormIndex.value = -1
      } else {
        contents.value.push(newContent)
        changedIndices.value.add(contents.value.length - 1)
        showToast(`Элемент "${getContentTypeName(type)}" добавлен`, 'success')
      }
      
      closeBlockModal()
    }

    return {
      userStore,
      aiStore,
      article,
      selectedContentType,
      contents,
      mode,
      aiUserPrompt,
      loadError,
      showAIButton,
      selectedText,
      aiButtonPosition,
      isSaving,
      toastMessage,
      toastType,
      hasChanges,
      isContentReadOnly,
      isEditMode,
      handleTextSelection,
      openAIModal,
      closeAiModalButton,
      insertAiResponseFromComponent,
      getContentTypeName,
      getContentComponent,
      addContent,
      onContentUpdate,
      removeContent,
      saveAllChanges,
      goBack,
      toggleMode,
      moveContentUp,
      moveContentDown,
      showBlockModal,
      selectedBlockType,
      blockTypes,
      openBlockModal,
      closeBlockModal,
      addNewBlock,
      customForms,
      createNewForm,
      removeForm,
      onFormContentUpdate,
      moveFormContentUp,
      moveFormContentDown,
      removeFormContent,
      openFormBlockModal,
      activeFormIndex,
      selectForm,
      onFormTitleChange,
      onFormTitleBlur,
      onFormTitleFocus,
      closeAiModal,
      copyAiResponse,
      aiExplainText,
      aiSimplifyText,
      aiExpandText,
      aiAskCustom,
      insertAiResponse,
      showToast,
      isLessonCompleted,
      isLoading,
      lessonScore,
      onAnswerSubmitted,
      resetLessonProgress,
      handleGlobalTextSelection,
      beforeUnloadHandler,
      updateContentOrder,
      saveOrder,
      handleTitleClick,
      timeRemaining,
      formatTimeRemaining,
      isTimeExpired,
    }
  },
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600;700&display=swap');

* {
  box-sizing: border-box;
}

.main-content-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1480px;
  background: var(--background-color);
  transition: background-color 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.center-column-box-layout {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
}

.header-section {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 8px;
  align-items: flex-end;
  justify-content: space-between;
  padding: 30px 29px 40px 99px;
  background: var(--form-background);
  border-radius: 8px;
  padding: 1.5rem;
  transition: background-color 0.5s ease, box-shadow 0.4s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.header-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: var(--accent-color);
  transform-origin: left;
  transform: scaleX(0);
  transition: transform 0.5s ease-out;
}

.header-section:hover::after {
  transform: scaleX(1);
}

.main-title-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 36px Helvetica;
  color: #24222f;
}

.navigation-bar {
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 29.5px;
  align-items: center;
  justify-content: flex-start;
}

.main-title-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}

.vertical-divider {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 1px;
  height: 29px;
  border-left: 1px solid #24222f;
}

.course-info-panel {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  width: 52px;
  padding-top: 9px;
  padding-bottom: 4.5px;
}

.course-title-text-style {
  flex: 0 0 auto;
  align-self: center;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}

.course-divider {
  flex: 0 0 auto;
  margin-top: 2.5px;
  border-top: 1px solid #24222f;
}

.main-page-icon {
  box-sizing: border-box;
  display: block;
  width: 42px;
  max-width: initial;
  height: 40px;
  border: none;
  object-fit: cover;
}

.central-content-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}

.main-content-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 43px;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1043px;
  padding-top: 91px;
  padding-bottom: 157px;
  /* Ensure content is centered */
  margin: 0 auto;
  max-width: 1200px;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  background: var(--form-background);
  border-radius: 8px;
  padding: 1.5rem;
  transition: background-color 0.5s ease, box-shadow 0.4s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

/* Add a class to indicate preview mode */
.article-header.preview-mode .article-title {
  pointer-events: none;
  border-color: transparent;
  cursor: default;
}

.article-title {
  flex: 1;
  font-size: 2rem;
  font-weight: 600;
  padding: 1rem;
  border: none;
  border-bottom: 2px solid var(--accent-color);
  background: transparent;
  color: var(--text-color);
  outline: none;
  transition: border-color 0.4s, color 0.4s ease, transform 0.3s;
  margin-right: 2rem;
  /* Ensure text wrapping for long titles */
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  max-width: 100%;
}

.article-title:focus:not(:disabled) {
  border-color: var(--secondary-text);
  transform: translateY(-2px);
}

.article-title:read-only,
.article-title:disabled {
  border-color: transparent;
  cursor: default;
  opacity: 1;
  background-color: transparent;
  pointer-events: none; /* Prevent any interaction */
  -webkit-user-select: none; /* Safari */
  -ms-user-select: none; /* IE 10+ */
  user-select: none; /* Standard syntax */
}

.mode-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.mode-toggle-btn,
.back-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: all 0.2s ease;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.mode-toggle-btn::before,
.back-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.2));
  transform: translateX(-100%);
  transition: transform 0.4s ease-out;
}

.mode-toggle-btn:hover::before,
.back-button:hover::before {
  transform: translateX(0);
}

.mode-toggle-btn:hover:not(:disabled),
.back-button:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.mode-toggle-btn:active,
.back-button:active {
  transform: translateY(0);
}

.mode-toggle-btn.active {
  background: var(--secondary-text);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
}

.create-form-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-form-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.custom-form-container {
  margin-top: 35px;
  padding: 25px;
  background: var(--form-background);
  border-radius: 12px;
  border: 2px solid var(--border-color);
  transition: all 0.4s ease;
  /* Fixed width for form containers */
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
}

.custom-form-container:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
  border-color: var(--accent-color);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  padding-left: 10px;
  padding-right: 10px;
  /* Remove the border-bottom */
  /* border-bottom: 2px solid var(--border-color); */
  transition: border-color 0.3s ease;
  position: relative;
}


.custom-form-container:hover .form-header::after {
  width: 100px;
}

.active-form .form-header::after {
  width: 100%;
}

.form-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--text-color);
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
  padding: 8px 12px;
  transition: all 0.3s ease, color 0.3s ease;
  border-radius: 6px;
  margin-bottom: 5px;
  /* Ensure text wrapping for long titles */
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
}

.form-title:not([readonly]):not([disabled]):focus {
  background-color: var(--background-color);
  border: 1px solid var(--accent-color);
  box-shadow: 0 0 8px rgba(160, 148, 184, 0.3);
}

.form-title:not([readonly]):not([disabled]):hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.form-title[readonly], .form-title[disabled] {
  cursor: default;
  opacity: 0.95;
}

.form-controls {
  display: flex;
  gap: 10px;
}

.form {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 40px;
  align-items: stretch;
  justify-content: flex-start;
  padding: 20px;
  background: #f5f9f8;
  border-radius: 8px;
  margin-bottom: 30px;
  position: relative;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 48px;
  padding-left: 70px;
  margin-bottom: 40px;
}

.main-heading-style {
  flex: 0 0 auto;
  padding: 0;
  padding-right: 48px;
  padding-left: 70px;
  margin: 0;
  font: 600 36px Raleway, sans-serif;
  color: #24222f;
}

.editor-toolbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--form-background);
  padding: 16px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
  transition: background-color 0.3s ease;
}

.toolbar-content {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
}

.content-type-select {
  padding: 12px 24px;
  border: 1px solid #a094b8;
  border-radius: 10px;
  background: #fff;
  color: #24222f;
  font-size: 16px;
  font-family: 'Raleway', sans-serif;
  min-width: 200px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.content-type-select:hover {
  border-color: #8b7ca5;
}

.content-type-select:focus {
  outline: none;
  border-color: #575667;
  box-shadow: 0 0 0 2px rgba(87, 86, 103, 0.2);
}

.add-content-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 400;
  font-family: 'Raleway', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  background: var(--accent-color);
  color: var(--footer-text);
}

.add-content-btn:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.add-content-btn:disabled, 
.add-content-btn.disabled {
  background: #d1d5db;
  cursor: not-allowed;
  opacity: 0.7;
  position: relative;
}

.add-content-btn:disabled:hover,
.add-content-btn.disabled:hover {
  background: #d1d5db;
  transform: none;
  box-shadow: none;
}

.add-content-btn:disabled::after,
.add-content-btn.disabled::after {
  content: 'Выберите форму сначала';
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.add-content-btn:disabled:hover::after,
.add-content-btn.disabled:hover::after {
  opacity: 1;
}

.save-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 400;
  font-family: 'Raleway', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  background: var(--accent-color);
  color: var(--footer-text);
}

.save-button:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.save-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 18px;
  line-height: 1;
}

.changes-indicator {
  color: #ef4444;
  margin-left: 4px;
  font-weight: 700;
}

.dark-purple-flex-container {
  width: 100%;
}

.team-contacts-section1,
.team-contacts-section,
.team-contact-info-container,
.team-contacts-heading,
.team-contact-info-display-style,
.contact-info-style,
.contact-info-link,
.line-break-separator,
.partner-section1,
.partner-section,
.image-container,
.center-aligned-copyright-text,
.purple-heading {
  /* These styles are now in the Footer component */
  display: none;
}

.ai-chat-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.ai-chat-container {
  background: var(--form-background);
  border-radius: 20px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  font-family: 'Raleway', sans-serif;
}

.ai-chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 29px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.ai-modal-close {
  background: #ef4444;
  color: #f5f9f8;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: background 0.2s, transform 0.1s;
}

.ai-modal-close:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.ai-chat-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding: 40px 70px;
}

.selected-text-panel {
  background: #ebefef;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #a094b8;
}

.info-text {
  font-size: 15px;
  font-weight: 400;
  color: #24222f;
  margin: 0;
  white-space: pre-wrap;
}

.ai-prompt-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-prompt-input {
  width: 100%;
  min-height: 120px;
  padding: 14px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-family: 'Raleway', sans-serif;
  font-size: 15px;
  resize: vertical;
  background: #fff;
}

.ai-quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.ai-action-btn {
  background: #a094b8;
  color: #f5f9f8;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background 0.2s, transform 0.1s;
  min-width: 100px;
}

.ai-action-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.ai-loading-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #24222f;
  font-style: italic;
}

.ai-error-panel {
  background: #fef2f2;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #ef4444;
}

.error-text {
  font-size: 15px;
  font-weight: 400;
  color: #dc2626;
  margin: 0;
}

.ai-response-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.title-heading {
  font-size: 24px;
  font-weight: 600;
  color: #24222f;
  margin: 0;
}

.ai-response-content {
  background: #ebefef;
  padding: 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 400;
  color: #24222f;
  white-space: pre-wrap;
}

.ai-response-actions {
  display: flex;
  gap: 16px;
}

.ai-insert-btn,
.ai-copy-btn {
  background: #a094b8;
  color: #f5f9f8;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.ai-insert-btn:hover,
.ai-copy-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.ai-copy-btn {
  background: #575667;
}

.ai-copy-btn:hover {
  background: #4a4857;
}

.ai-chat-footer {
  padding: 20px 29px;
  text-align: right;
  border-top: 1px solid #e5e7eb;
}

.ai-close-btn {
  background: #ef4444;
  color: #f5f9f8;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.ai-close-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.ai-floating-btn {
  position: absolute;
  background: #a094b8;
  color: #f5f9f8;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 999;
  transition: background 0.2s, transform 0.1s;
}

.ai-floating-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.error-message {
  color: var(--error-color);
  background: var(--error-background);
  padding: 16px;
  border-radius: 10px;
  margin-bottom: 24px;
  text-align: center;
  font-size: 15px;
  width: 100%;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.retry-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 16px;
  font-size: 16px;
  font-weight: 400;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 120px;
}

.spinner {
  border: 3px solid #e5e7eb;
  border-top: 3px solid #a094b8;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.toast {
  position: fixed;
  bottom: 32px;
  right: 32px;
  padding: 16px 24px;
  border-radius: 10px;
  color: var(--footer-text);
  font-size: 16px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 90%;
  transition: background-color 0.3s ease;
}

.toast.success {
  background-color: #4CAF50;
}

.toast.error {
  background-color: #f44336;
}

.toast.info {
  background-color: #2196F3;
}

.toast-close {
  background: transparent;
  color: #f5f9f8;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
}

@media (max-width: 768px) {
  .main-content-container {
    padding: 16px;
  }

  .header-section {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .header-section h1 {
    font-size: 28px;
  }

  .navigation-bar {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .main-title-style {
    width: 100%;
    padding: 12px;
  }

  .editor-toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .content-type-select,
  .add-content-btn {
    width: 100%;
    padding: 12px;
  }

  .ai-chat-container {
    padding: 24px;
    width: 95%;
    max-width: 95%;
  }

  .ai-chat-content {
    padding: 24px;
  }

  .ai-quick-actions {
    flex-direction: column;
  }

  .ai-action-btn {
    width: 100%;
    padding: 12px;
  }

  .ai-response-actions {
    flex-direction: column;
  }

  .ai-insert-btn,
  .ai-copy-btn,
  .ai-close-btn {
    width: 100%;
    padding: 12px;
  }

  .toast {
    bottom: 16px;
    right: 16px;
    max-width: 95%;
  }
}

@media (max-width: 480px) {
  .header-section h1 {
    font-size: 24px;
  }

  .content-item {
    padding: 16px;
  }

  .order-btn,
  .remove-content-btn {
    width: 28px;
    height: 28px;
    font-size: 16px;
  }

  .ai-chat-content {
    padding: 16px;
  }

  .ai-prompt-input,
  .info-text,
  .ai-response-content {
    font-size: 14px;
  }
}

.block-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.block-modal-container {
  background: var(--form-background);
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  overflow-x: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease;
}

.block-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 29px 20px;
  border-bottom: 1px solid var(--border-color);
  position: relative;
  transition: border-color 0.3s ease;
}

.main-heading-style {
  font-size: 36px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  flex: 1;
  transition: color 0.3s ease;
}

.modal-close {
  background: #ef4444;
  color: #f5f9f8;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 20px;
  position: static;
}

.modal-close:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.block-modal-content {
  padding: 20px;
}

.block-type-selection {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.block-type-card {
  box-sizing: border-box;
  padding: 20px;
  background: var(--background-color);
  border: 2px solid var(--border-color);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 150px;
}

.block-type-card:hover {
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.block-type-card.selected {
  border-color: var(--secondary-text);
  background: var(--form-background);
}

.block-icon {
  font-size: 24px;
  margin-bottom: 12px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.block-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
  text-align: center;
  transition: color 0.3s ease;
}

.block-description {
  font-size: 12px;
  color: var(--secondary-text);
  text-align: center;
  line-height: 1.4;
  padding: 0 10px;
  transition: color 0.3s ease;
}

.block-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.add-block-btn {
  background: #575667;
  color: #f5f9f8;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background 0.2s, transform 0.1s;
}

.add-block-btn:hover:not(:disabled) {
  background: #4a4857;
  transform: translateY(-1px);
}

.add-block-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.cancel-btn {
  background: #ef4444;
  color: #f5f9f8;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background 0.2s, transform 0.1s;
}

.cancel-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.preview-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 400;
  font-family: 'Raleway', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.active-form {
  border: 2px solid var(--accent-color);
  box-shadow: 0 0 25px rgba(160, 148, 184, 0.25);
  transform: translateY(-3px);
}

.remove-form-btn {
  background: var(--error-color, #ef4444);
  color: var(--footer-text, #f5f9f8);
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.remove-form-btn:hover {
  background: var(--hover-delete, #dc2626);
  transform: translateY(-1px);
}

:root {
  --error-color: #ef4444;
  --hover-delete: #dc2626;
}

.dark-theme {
  --error-color: #ff6b6b;
  --hover-delete: #e55a5a;
}

.add-content-btn.form-selected {
  background: #575667;
  position: relative;
}

.add-content-btn.form-selected:hover:not(:disabled) {
  background: #4a4857;
}

.editable-content,
.preview-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Keep left alignment */
  width: 100%;
  gap: 20px;
  --content-block-width: auto; /* Initialize the CSS variable */
  /* Fixed width for content */
  max-width: 850px;
  margin-left: auto;
  margin-right: auto;
}

.article-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--form-background);
  border-radius: 8px;
  margin-bottom: 1rem;
  transition: background-color 0.3s ease;
}

.editor-btn {
  padding: 0.5rem 1rem;
  background: #a094b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s, transform 0.1s;
}

.editor-btn:hover {
  background: #8275a0;
  transform: translateY(-1px);
}

.add-content-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  background: #a094b8;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s, transform 0.1s;
}

.add-content-btn:hover {
  background: #8275a0;
  transform: translateY(-1px);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.block-modal-content {
  padding: 20px;
}

.block-type-selection {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.ai-prompt-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-prompt-input {
  width: 100%;
  min-height: 120px;
  padding: 14px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-family: 'Raleway', sans-serif;
  font-size: 15px;
  resize: vertical;
  background: var(--background-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

.ai-action-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 100px;
}

.ai-action-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.ai-error-panel {
  background: #fef2f2;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #ef4444;
}

.ai-response-content {
  background: var(--background-color);
  padding: 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 400;
  color: var(--text-color);
  white-space: pre-wrap;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.ai-insert-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 120px;
}

.ai-copy-btn {
  background: var(--secondary-text);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 120px;
}

/* Add new styles for images */
:deep(img) {
  opacity: 0.85;
  transition: opacity 0.3s ease, filter 0.3s ease;
}

:deep(.dark-theme img) {
  filter: brightness(0.9);
}

.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.toast-notification.success {
  background-color: #4CAF50;
}

.toast-notification.error {
  background-color: #f44336;
}

.toast-notification.warning {
  background-color: #ff9800;
}

.toast-notification.info {
  background-color: #2196F3;
}

.progress-tracking-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
  flex-wrap: wrap;
}

.score-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.score-label {
  font-size: 16px;
  color: var(--text-color);
  font-weight: 500;
}

.score-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
}

.score-success {
  color: #2e8b33;
}

.score-partial {
  color: #f59e0b;
}

.mark-completed-btn {
  margin-left: 16px;
  padding: 8px 16px;
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.mark-completed-btn:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.mark-completed-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.mark-completed-btn .btn-icon {
  font-size: 16px;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  width: 100%;
  padding: 20px;
}

.loading-indicator .spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 16px;
}

.loading-indicator p {
  font-size: 16px;
  color: var(--text-color);
}

:global(.dark-theme) .score-summary {
  background: rgba(255, 255, 255, 0.08);
}

:global(.dark-theme) .score-success {
  color: #6bdb70;
}

:global(.dark-theme) .score-partial {
  color: #fbbf24;
}

.progress-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.reset-progress-btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 400;
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reset-progress-btn:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.reset-progress-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.add-content-btn .btn-icon,
.create-form-btn .btn-icon,
.reset-progress-btn .btn-icon,
.save-button .btn-icon {
  font-size: 18px;
  line-height: 1;
}

.ai-control {
  display: flex;
  align-items: center;
  margin-right: 15px;
}

.ai-toggle {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  position: relative;
  padding: 4px;
  border-radius: 20px;
  transition: background-color 0.3s ease;
}

.ai-toggle:hover {
  background-color: rgba(160, 148, 184, 0.1);
}

.ai-toggle input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.ai-toggle-label {
  font-size: 14px;
  color: var(--text-color);
  transition: color var(--transition-speed) var(--transition-timing);
  margin-left: 32px;
  position: relative;
}

.ai-toggle-label::before {
  content: '';
  position: absolute;
  left: -32px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 14px;
  background-color: var(--border-color);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.ai-toggle-label::after {
  content: '';
  position: absolute;
  left: -30px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  background-color: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.ai-toggle input[type="checkbox"]:checked + .ai-toggle-label::before {
  background-color: var(--accent-color);
}

.ai-toggle input[type="checkbox"]:checked + .ai-toggle-label::after {
  left: -16px;
}

.ai-toggle input[type="checkbox"]:focus + .ai-toggle-label::before {
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.3);
}

:global(.dark-theme) .ai-toggle-label {
  color: var(--text-color);
}

:global(.dark-theme) .ai-toggle-label::before {
  background-color: var(--border-color);
}

:global(.dark-theme) .ai-toggle-label::after {
  background-color: var(--background-color);
}

.back-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 120px;
}

.back-button:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.back-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.back-button .btn-icon {
  font-size: 18px;
  line-height: 1;
}

.countdown-timer {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--accent-color);
  color: var(--footer-text);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.preview-mode {
  opacity: 0.8;
  pointer-events: none;
}

.preview-mode .article-title {
  border-color: transparent;
  cursor: default;
}

.preview-mode .mode-controls {
  display: none;
}
</style>