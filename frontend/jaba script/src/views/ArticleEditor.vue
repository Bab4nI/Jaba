<template>
  <div class="main-content-container">

    <div class="central-content-container">
      <div class="main-content-container1">
        <div class="article-header">
          <input
            v-model="article.title"
            type="text"
            class="article-title"
            :placeholder="isEditMode ? 'Название работы' : ''"
            :readonly="!isEditMode"
          >
          <div class="mode-controls" v-if="userStore.role === 'admin'">
            <button 
              @click="toggleMode" 
              class="mode-toggle-btn"
              :class="{ 'active': mode === 'edit' }"
            >
              {{ mode === 'edit' ? 'Предпросмотр' : 'Редактировать' }}
            </button>
          </div>
        </div>
        
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
              :is-first="elementIndex === 0"
              :is-last="elementIndex === form.contents.length - 1"
              @update:content="onFormContentUpdate(formIndex, elementIndex, $event)"
              @move-up="moveFormContentUp(formIndex, elementIndex)"
              @move-down="moveFormContentDown(formIndex, elementIndex)"
              @remove="removeFormContent(formIndex, elementIndex)"
            />
          </div>
          <div v-else class="preview-content">
            <ContentBlock
              v-for="(element, elementIndex) in form.contents"
              :key="element.id || elementIndex"
              :content="element"
              :read-only="true"
            />
          </div>
        </div>

        <div v-if="mode === 'edit' && userStore.role === 'admin'" class="editor-toolbar">
          <div class="toolbar-content">
            <button
              @click="openBlockModal"
              class="add-content-btn"
              :class="{ 'form-selected': activeFormIndex >= 0 }"
              aria-label="Добавить новый элемент"
            >
              <span class="btn-icon">+</span>
              {{ activeFormIndex >= 0 ? `Добавить в ${customForms[activeFormIndex]?.title ? '"' + customForms[activeFormIndex].title + '"' : 'форму'}` : 'Добавить элемент' }}
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
              @click="toggleMode"
              class="preview-btn"
              aria-label="Предпросмотр"
            >
              <span class="btn-icon">👁️</span>
              Предпросмотр
            </button>

            <button
              @click="saveAllChanges"
              class="save-button"
              :disabled="isSaving || !hasChanges"
              aria-label="Сохранить все изменения"
            >
              <span v-if="isSaving" class="spinner"></span>
              <span v-else class="btn-icon">💾</span>
              {{ isSaving ? 'Сохранение...' : 'Сохранить работу' }}
              <span v-if="hasChanges" class="changes-indicator">*</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="dark-purple-flex-container">
      <Footer />
    </div>

    <!-- Error Message for Content Loading -->
    <div v-if="loadError" class="error-message">
      {{ loadError }}
      <button @click="goBack" class="retry-button" aria-label="Вернуться к модулям">
        Вернуться к модулям
      </button>
    </div>

    <!-- Floating AI Button -->
    <transition name="fade">
      <button
        v-if="showAIButton && selectedText"
        class="ai-floating-btn"
        :style="aiButtonPosition"
        @click="openAIModal"
        aria-label="Открыть AI запрос"
      >
        AI Запрос
      </button>
    </transition>

    <!-- AI Chat Modal -->
    <div v-if="aiStore.modalVisible" class="ai-chat-modal" role="dialog" aria-labelledby="ai-modal-title">
      <div class="ai-chat-container">
        <div class="ai-chat-header">
          <h3 id="ai-modal-title" class="main-heading-style">Работа с выделенным текстом</h3>
          <button class="ai-modal-close" @click="closeAiModal" aria-label="Закрыть модальное окно">×</button>
        </div>
        <div class="ai-chat-content">
          <div class="selected-text-panel">
            <p class="info-text">{{ aiStore.selectedText || 'Выделите текст для обработки' }}</p>
          </div>
          <div class="ai-prompt-panel">
            <textarea
              v-model="aiUserPrompt"
              placeholder="Уточните ваш запрос или выберите действие..."
              class="ai-prompt-input"
              aria-label="Поле для ввода запроса к AI"
            ></textarea>
            <div class="ai-quick-actions">
              <button @click="aiExplainText" class="ai-action-btn">Объяснить</button>
              <button @click="aiSimplifyText" class="ai-action-btn">Упростить</button>
              <button @click="aiExpandText" class="ai-action-btn">Расширить</button>
              <button @click="aiAskCustom" class="ai-action-btn">Спросить</button>
            </div>
          </div>
          <div v-if="aiStore.isLoading" class="ai-loading-panel">
            <span class="spinner"></span>
            <p class="info-text">Идет обработка запроса...</p>
          </div>
          <div v-else-if="aiStore.error" class="ai-error-panel">
            <p class="error-text">Ошибка AI: {{ aiStore.error }}</p>
          </div>
          <div v-else-if="aiStore.aiResponse" class="ai-response-panel">
            <h4 class="title-heading">Ответ:</h4>
            <p class="ai-response-content">{{ aiStore.aiResponse }}</p>
            <div class="ai-response-actions">
              <button @click="insertAiResponse" class="ai-insert-btn">Вставить в статью</button>
              <button @click="copyAiResponse" class="ai-copy-btn">Копировать</button>
            </div>
          </div>
        </div>
        <div class="ai-chat-footer">
          <button @click="closeAiModal" class="ai-close-btn">Закрыть</button>
        </div>
      </div>
    </div>

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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAIStore } from '@/stores/aiStore'
import api from '@/api'
import { debounce } from 'lodash-es'
import ContentBlock from '@/components/article/ContentBlock.vue'
import Footer from '@/components/Footer.vue'

const CONTENT_TYPES = {
  text: 'TEXT',
  image: 'IMAGE',
  video: 'VIDEO',
  code: 'CODE',
  quiz: 'QUIZ',
  table: 'TABLE',
  file: 'FILE',
  form: 'FORM',
}

// Add form type to our content types
const FORM_TYPE = 'CUSTOM_FORM';

const DEFAULT_CONTENT = {
  text: { text: '', readOnly: false },
  image: { image: null, readOnly: false },
  video: { video_url: '', readOnly: false },
  code: { code: '', language: 'javascript', readOnly: false },
  quiz: { question: '', answers: ['', ''], correct_answer: null, readOnly: false },
  table: { headers: ['Заголовок 1', 'Заголовок 2'], data: [['', ''], ['', '']], readOnly: false },
  file: { file: null, filename: null, readOnly: false },
  form: { fields: [], readOnly: false },
}

const BLOCK_TYPES = [
  {
    value: 'text',
    label: 'Текстовый блок',
    description: 'Блок для ввода и форматирования текста',
    icon: '📝'
  },
  {
    value: 'image',
    label: 'Изображение',
    description: 'Добавление изображений с подписями',
    icon: '🖼️'
  },
  {
    value: 'video',
    label: 'Видео',
    description: 'Вставка видео с YouTube или других платформ',
    icon: '🎥'
  },
  {
    value: 'code',
    label: 'Код',
    description: 'Блок для демонстрации кода с подсветкой синтаксиса',
    icon: '💻'
  },
  {
    value: 'quiz',
    label: 'Тест',
    description: 'Создание тестовых вопросов с вариантами ответов',
    icon: '❓'
  },
  {
    value: 'table',
    label: 'Таблица',
    description: 'Создание структурированных таблиц',
    icon: '📊'
  },
  {
    value: 'file',
    label: 'Файл',
    description: 'Загрузка файлов для скачивания',
    icon: '📎'
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
    Footer,
  },

  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    const aiStore = useAIStore()

    const article = ref({
      id: route.params.lessonId,
      title: route.query.title || 'Новая работа',
      type: route.query.type || 'article',
    })

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
      const currentContent = contents.value[index]
      contents.value[index] = {
        ...currentContent,
        ...updatedContent,
        updated_at: new Date().toISOString()
      }
      changedIndices.value.add(index)
    }, 500)

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

    const openAIModal = () => {
      aiStore.setSelectedText(selectedText.value)
      showAIButton.value = false
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

    const copyAiResponse = () => {
      navigator.clipboard.writeText(aiStore.aiResponse)
      showToast('Ответ скопирован в буфер обмена.', 'success')
    }

    const closeAiModal = () => {
      aiStore.reset()
      aiUserPrompt.value = ''
      showAIButton.value = false
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
      if (!hasChanges.value && customForms.value.length === 0) {
        showToast('Нет изменений для сохранения.', 'info')
        return
      }

      isSaving.value = true
      const errors = []

      try {
        // Generate IDs for forms that don't have one and ensure all forms have titles
        customForms.value.forEach(form => {
          if (!form.id) {
            form.id = generateUniqueId()
          }
          // Set default title only when saving if title is empty
          if (!form.title || form.title.trim() === '') {
            form.title = 'Новая форма'
          }
        })

        // When using local storage (or when backend endpoints don't exist yet)
        if (useLocalStorage.value) {
          try {
            // Save forms to localStorage
            localStorage.setItem(`article_forms_${article.value.id}`, JSON.stringify(customForms.value))
            
            // Save individual content items if needed
            let allContentSaved = true
            for (const form of customForms.value) {
              for (const content of form.contents) {
                // Check if any content needs special handling (e.g., file uploads)
                if ((content.type === 'file' && content.file instanceof File) || 
                    (content.type === 'image' && content.image instanceof File)) {
                  // Handle file upload errors - in local mode we just mark it as saved
                  // In a real environment, you would handle the upload
                  content.id = content.id || generateUniqueId()
                  
                  // If it's a local testing environment, simulate successful upload
                  if (content.type === 'file') {
                    // Store file name instead of the actual file
                    content.filename = content.file.name
                    content.file = URL.createObjectURL(content.file)
                  } else if (content.type === 'image') {
                    // Store image URL instead of the actual file
                    content.image = URL.createObjectURL(content.image)
                  }
                } else if (!content.id) {
                  // Assign ID to any content that doesn't have one
                  content.id = generateUniqueId()
                }
              }
            }
            
            // Update localStorage again with processed content
            localStorage.setItem(`article_forms_${article.value.id}`, JSON.stringify(customForms.value))
            
            if (allContentSaved) {
              changedIndices.value.clear()
              lastSavedAt.value = new Date()
              showToast('Все изменения сохранены локально.', 'success')
            } else {
              showToast('Некоторые элементы не удалось сохранить.', 'warning')
            }
          } catch (error) {
            console.error('Ошибка локального сохранения:', error)
            showToast('Не удалось сохранить изменения локально.', 'error')
          }
        } else {
          // Original backend saving code
          // Step 1: Save form metadata and structure
          try {
            const formsToSave = customForms.value.map(form => ({
              id: form.id,
              title: form.title || 'Новая форма',
              order: customForms.value.indexOf(form) + 1,
              lesson: article.value.id
            }))
            
            const formsResponse = await api.post(
              `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/forms/batch/`,
              { forms: formsToSave }
            )
            
            // Update the form IDs with what came back from the server
            if (formsResponse.data && formsResponse.data.forms) {
              formsResponse.data.forms.forEach((savedForm, index) => {
                if (index < customForms.value.length) {
                  customForms.value[index].id = savedForm.id
                }
              })
            }
          } catch (error) {
            console.error('Ошибка сохранения форм:', error)
            errors.push('Не удалось сохранить формы: ' + (error.response?.data?.detail || error.message))
          }

          // Step 2: Save all content from all forms
          let formContentMap = new Map() // Map to track which form each content came from
          let allFormContents = []
          
          customForms.value.forEach((form, formIndex) => {
            form.contents.forEach((content, contentIndex) => {
              // Create a deep copy to avoid reference issues
              const contentCopy = JSON.parse(JSON.stringify(content))
              
              // Add form_id to content so we know where to place it later
              contentCopy.form_id = form.id
              contentCopy.order = contentIndex + 1 // Ensure proper ordering
              
              allFormContents.push(contentCopy)
              
              // Track which form this content belongs to
              formContentMap.set(contentCopy, {
                formIndex,
                contentIndex
              })
            })
          })
          
          // Store the original contents to restore later
          const originalContentsBackup = JSON.parse(JSON.stringify(contents.value))
          
          // Set contents to the form contents for saving
          contents.value = allFormContents
          
          const indicesToSave = [...Array(allFormContents.length).keys()] // Save all contents
          const promises = indicesToSave.map(async (index) => {
            const content = contents.value[index]
            const isNewContent = !content.id
            
            // Handle file uploads (File and Image) using FormData
            if ((content.type === 'file' && content.file instanceof File) || 
                (content.type === 'image' && content.image instanceof File)) {
              const formData = new FormData()
              formData.append('lesson', article.value.id)
              formData.append('content_type', CONTENT_TYPES[content.type])
              formData.append('order', content.order)
              
              // Add form_id to the content
              if (content.form_id) {
                formData.append('form_id', content.form_id)
              }

              if (content.type === 'file') {
                formData.append('file', content.file)
                if (content.filename) formData.append('title', content.filename)
              } else if (content.type === 'image') {
                formData.append('image', content.image)
              }

              try {
                const url = isNewContent
                  ? `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`
                  : `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/${content.id}/`
                const method = isNewContent ? 'post' : 'put'
                
                const response = await api[method](url, formData, {
                  headers: { 'Content-Type': 'multipart/form-data' }
                })
                return { success: true, data: response.data, index }
              } catch (error) {
                return { success: false, error, index }
              }
            } else {
              // Handle other content types or updates without file changes
              const payload = {
                lesson: article.value.id,
                content_type: CONTENT_TYPES[content.type],
                order: content.order,
              }
              
              // Add form_id to the content
              if (content.form_id) {
                payload.form_id = content.form_id
              }

              if (content.type === 'text') {
                payload.text = content.text || ''
              } else if (content.type === 'image' && typeof content.image === 'string') {
                // If image is a string (URL), don't send it again unless necessary
              } else if (content.type === 'video') {
                payload.video_url = content.video_url || ''
              } else if (content.type === 'code') {
                payload.text = content.code || ''
                payload.code_language = content.language || 'javascript'
              } else if (content.type === 'quiz') {
                payload.quiz_data = {
                  question: content.question || '',
                  answers: content.answers || ['', ''],
                  correct_answer: content.correct_answer
                }
              } else if (content.type === 'table') {
                payload.table_data = {
                  headers: content.headers || ['Заголовок 1', 'Заголовок 2'],
                  data: content.data || [['', ''], ['', '']]
                }
              } else if (content.type === 'file' && typeof content.file === 'string') {
                 // If file is a string (URL), don't send it again unless necessary
              }

              try {
                const url = isNewContent
                  ? `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`
                  : `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/${content.id}/`
                const method = isNewContent ? 'post' : 'put'

                const response = await api[method](url, payload)
                return { success: true, data: response.data, index }
              } catch (error) {
                return { success: false, error, index }
              }
            }
          })

          const results = await Promise.all(promises)
          const savedContents = []
          
          results.forEach((result) => {
            if (result.success) {
              const { data, index } = result
              
              contents.value[index] = {
                ...contents.value[index],
                id: data.id,
                file: data.file || contents.value[index].file,
                filename: data.title || data.filename || contents.value[index].filename
              }
              savedContents.push(contents.value[index])
            } else {
              const { error, index } = result
              const contentInfo = formContentMap.get(contents.value[index])
              
              if (contentInfo) {
                const { formIndex, contentIndex } = contentInfo
                const content = customForms.value[formIndex].contents[contentIndex]
                const errorMessage = error?.response?.data?.detail || error?.message || 'Неизвестная ошибка'
                errors.push(`Форма ${formIndex + 1}, элемент ${contentIndex + 1} (${getContentTypeName(content.type)}): ${errorMessage}`)
              } else {
                const errorMessage = error.response?.data?.detail || error.message
                errors.push(`Элемент ${index + 1} (${getContentTypeName(contents.value[index].type)}): ${errorMessage}`)
              }
            }
          })

          if (errors.length > 0) {
            showToast(`Ошибки при сохранении: ${errors.join('; ')}`, 'error')
            // Restore original contents if errors occurred
            contents.value = originalContentsBackup
          } else {
            changedIndices.value.clear()
            lastSavedAt.value = new Date()
            
            // Update each form's contents with the saved data
            savedContents.forEach(savedContent => {
              const contentInfo = formContentMap.get(savedContent)
              if (contentInfo) {
                const { formIndex, contentIndex } = contentInfo
                
                // Ensure we maintain the type and other important properties
                const originalType = customForms.value[formIndex].contents[contentIndex].type
                customForms.value[formIndex].contents[contentIndex] = {
                  ...customForms.value[formIndex].contents[contentIndex],
                  ...savedContent,
                  type: originalType // Explicitly preserve original type
                }
              }
            })
            
            // Restore original contents array
            contents.value = originalContentsBackup
            originalContents.value = JSON.parse(JSON.stringify(contents.value))
            
            // Invalidate relevant caches after saving
            api.invalidateContentCache();
            
            showToast('Все изменения успешно сохранены!', 'success')
          }
        }
      } catch (error) {
        console.error('Ошибка сохранения работы:', error)
        showToast(`Ошибка при сохранении: ${error.message}`, 'error')
      } finally {
        isSaving.value = false
      }
    }

    const loadArticle = async () => {
      if (!article.value.id || !route.params.courseSlug || !route.params.moduleId) {
        loadError.value = 'Отсутствуют необходимые параметры (курс, модуль или урок).'
        showToast('Ошибка параметров.', 'error')
        return
      }

      try {
        // Генерируем уникальный ключ запроса для кэширования
        const contentRequestUrl = `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`;
        
        // Load article contents
        const contentsResponse = await api.get(contentRequestUrl)
        contents.value = contentsResponse.data.sort((a, b) => a.order - b.order).map(item => ({
          ...item,
          filename: item.type === 'file' ? item.title : item.filename
        }))
        originalContents.value = JSON.parse(JSON.stringify(contents.value))
        
        // Load forms
        try {
          if (!useLocalStorage.value) {
            // Try loading from backend if endpoints exist
            const formsRequestUrl = `/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/forms/`;
            
            const formsResponse = await api.get(formsRequestUrl)
            
            if (formsResponse.data && Array.isArray(formsResponse.data)) {
              customForms.value = formsResponse.data.map(form => ({
                ...form,
                contents: form.contents || []
              }))
              
              // If we have forms but no active form, set the first one as active
              if (customForms.value.length > 0 && activeFormIndex.value === -1 && mode.value === 'edit') {
                activeFormIndex.value = 0
              }
            } else {
              createDefaultForm()
            }
          } else {
            // Load from localStorage if backend endpoints don't exist yet
            const savedForms = localStorage.getItem(`article_forms_${article.value.id}`)
            if (savedForms) {
              try {
                customForms.value = JSON.parse(savedForms)
                if (customForms.value.length > 0 && mode.value === 'edit') {
                  activeFormIndex.value = 0
                }
                showToast('Формы загружены из локального хранилища.', 'info')
              } catch (e) {
                console.error('Ошибка парсинга сохраненных форм:', e)
                createDefaultForm()
              }
            } else {
              createDefaultForm()
            }
          }
        } catch (error) {
          console.error('Ошибка загрузки форм:', error)
          // Fallback to localStorage if API fails
          const savedForms = localStorage.getItem(`article_forms_${article.value.id}`)
          if (savedForms) {
            try {
              customForms.value = JSON.parse(savedForms)
              if (customForms.value.length > 0 && mode.value === 'edit') {
                activeFormIndex.value = 0
              }
              showToast('Формы загружены из локального хранилища.', 'info')
            } catch (e) {
              console.error('Ошибка парсинга сохраненных форм:', e)
              createDefaultForm()
            }
          } else {
            createDefaultForm()
          }
        }
        
        changedIndices.value.clear()
        lastSavedAt.value = new Date()
        loadError.value = null
        showToast('Контент успешно загружен.', 'success')
      } catch (error) {
        console.error('Ошибка загрузки содержимого:', error)
        if (error.response?.status === 404) {
          loadError.value = 'Урок не найден. Проверьте правильность данных урока.'
        } else if (error.response?.status === 401) {
          loadError.value = 'Не авторизован. Пожалуйста, войдите в систему.'
        } else if (error.response?.status === 403) {
          loadError.value = 'Доступ к уроку запрещён. Проверьте ваши права доступа.'
        } else {
          loadError.value = 'Ошибка загрузки содержимого. Попробуйте позже.'
        }
        showToast(loadError.value, 'error')
        contents.value = []
        originalContents.value = []
        customForms.value = []
      }
    }

    // Helper to create default form
    const createDefaultForm = () => {
      if (contents.value.length > 0) {
        customForms.value = [{
          id: generateUniqueId(),
          title: 'Основная форма',
          contents: contents.value,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }]
        activeFormIndex.value = 0
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
        
        showToast(`Режим изменен на ${mode.value === 'edit' ? 'редактирование' : 'предпросмотр'}.`, 'info')
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
      // Check if a form is currently selected and set currentFormIndex accordingly
      if (activeFormIndex.value >= 0) {
        currentFormIndex.value = activeFormIndex.value;
        showToast(`Добавление элемента в форму "${customForms.value[activeFormIndex.value].title}"`, 'info');
      } else {
        currentFormIndex.value = -1; // Reset to ensure we're not adding to a form
      }
      showBlockModal.value = true
      selectedBlockType.value = ''
    }

    const closeBlockModal = () => {
      showBlockModal.value = false
      selectedBlockType.value = ''
    }

    const addNewBlock = (type) => {
      if (!type) return
      const newContent = {
        id: null,
        type,
        order: contents.value.length + 1,
        ...JSON.parse(JSON.stringify(DEFAULT_CONTENT[type])),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      if (currentFormIndex.value >= 0) {
        const formIndex = currentFormIndex.value
        newContent.order = customForms.value[formIndex].contents.length + 1
        customForms.value[formIndex].contents.push(newContent)
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

    const createNewForm = () => {
      const newForm = {
        id: generateUniqueId(),
        title: 'Новая форма',
        contents: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      customForms.value.push(newForm)
      changedIndices.value.add(`form-${customForms.value.length - 1}`)
      showToast('Новая форма создана.', 'success')
      
      // Automatically select the new form
      activeFormIndex.value = customForms.value.length - 1
    }

    const removeForm = (formIndex) => {
      if (!confirm('Вы уверены, что хотите удалить эту форму?')) return
      
      const form = customForms.value[formIndex]
      
      // If the form has an ID and we're not using localStorage, delete from server
      if (form.id && !useLocalStorage.value) {
        try {
          api.delete(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/forms/${form.id}/`)
            .then(() => {
              showToast('Форма удалена на сервере.', 'success')
            })
            .catch(error => {
              console.error('Ошибка удаления формы:', error)
              showToast('Форма удалена локально, но возникла ошибка при удалении на сервере.', 'warning')
            })
        } catch (error) {
          console.error('Ошибка удаления формы:', error)
        }
      }
      
      // Remove form locally
      customForms.value.splice(formIndex, 1)
      
      // If we're using localStorage, update the stored forms
      if (useLocalStorage.value) {
        localStorage.setItem(`article_forms_${article.value.id}`, JSON.stringify(customForms.value))
      }
      
      // If we deleted the active form, reset active form index
      if (activeFormIndex.value === formIndex) {
        activeFormIndex.value = customForms.value.length > 0 ? 0 : -1
      } else if (activeFormIndex.value > formIndex) {
        // If we deleted a form before the active form, adjust the index
        activeFormIndex.value--
      }
      
      showToast('Форма удалена.', 'success')
    }

    const onFormContentUpdate = debounce((formIndex, elementIndex, updatedContent) => {
      const currentContent = customForms.value[formIndex].contents[elementIndex]
      customForms.value[formIndex].contents[elementIndex] = {
        ...currentContent,
        ...updatedContent,
        updated_at: new Date().toISOString()
      }
      changedIndices.value.add(`form-${formIndex}-${elementIndex}`)
    }, 500)

    const moveFormContentUp = (formIndex, elementIndex) => {
      if (elementIndex > 0) {
        const temp = customForms.value[formIndex].contents[elementIndex]
        customForms.value[formIndex].contents[elementIndex] = customForms.value[formIndex].contents[elementIndex - 1]
        customForms.value[formIndex].contents[elementIndex - 1] = temp
        updateFormContentOrder(formIndex)
      }
    }

    const moveFormContentDown = (formIndex, elementIndex) => {
      if (elementIndex < customForms.value[formIndex].contents.length - 1) {
        const temp = customForms.value[formIndex].contents[elementIndex]
        customForms.value[formIndex].contents[elementIndex] = customForms.value[formIndex].contents[elementIndex + 1]
        customForms.value[formIndex].contents[elementIndex + 1] = temp
        updateFormContentOrder(formIndex)
      }
    }

    const updateFormContentOrder = (formIndex) => {
      customForms.value[formIndex].contents.forEach((content, index) => {
        content.order = index + 1
        changedIndices.value.add(`form-${formIndex}-${index}`)
      })
    }

    const removeFormContent = (formIndex, elementIndex) => {
      if (!confirm('Вы уверены, что хотите удалить этот элемент из формы?')) return
      
      customForms.value[formIndex].contents.splice(elementIndex, 1)
      updateFormContentOrder(formIndex)
      showToast('Элемент формы удален.', 'success')
    }

    const openFormBlockModal = (formIndex) => {
      currentFormIndex.value = formIndex
      showBlockModal.value = true
      selectedBlockType.value = ''
    }

    const selectForm = (formIndex, event) => {
      // Only allow form selection in edit mode
      if (mode.value === 'edit') {
        // Remove the class check, allowing any click within the form to select it
        activeFormIndex.value = formIndex
        
        // Only show toast if it's a direct click on the form (not through child elements)
        if (event.target.classList.contains('custom-form-container')) {
          showToast(`Форма "${customForms.value[formIndex].title}" выбрана.`, 'info')
        }
      }
    }

    const onFormTitleChange = (formIndex) => {
      const form = customForms.value[formIndex]
      changedIndices.value.add(`form-${formIndex}`)
      
      // If using localStorage, update storage
      if (useLocalStorage.value) {
        localStorage.setItem(`article_forms_${article.value.id}`, JSON.stringify(customForms.value))
      }
    }

    const onFormTitleBlur = (formIndex) => {
      // No auto-replacement with default title here, let user input whatever they want
      
      // If using localStorage, update storage
      if (useLocalStorage.value) {
        localStorage.setItem(`article_forms_${article.value.id}`, JSON.stringify(customForms.value))
      }
    }

    const onFormTitleFocus = (formIndex) => {
      // This function is for any actions needed when the title input is focused
      activeFormIndex.value = formIndex
    }

    onMounted(() => {
      document.addEventListener('mouseup', handleGlobalTextSelection)
      window.addEventListener('beforeunload', beforeUnloadHandler)
      
      // Only fetch user profile if not already loaded
      if (!userStore.user || !userStore.user.id) {
        userStore.fetchUserProfile()
      }
      
      if (!route.params.courseSlug || !route.params.moduleId || !route.params.lessonId) {
        loadError.value = 'Ошибка: отсутствуют необходимые параметры маршрута.'
        showToast('Ошибка маршрута.', 'error')
        return
      }
      loadArticle()
    })

    onUnmounted(() => {
      document.removeEventListener('mouseup', handleGlobalTextSelection)
      window.removeEventListener('beforeunload', beforeUnloadHandler)
    })

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
      aiExplainText,
      aiSimplifyText,
      aiExpandText,
      aiAskCustom,
      insertAiResponse,
      copyAiResponse,
      closeAiModal,
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
  transition: background-color 0.3s ease;
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
  background: #f5f9f8;
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
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  background: var(--form-background);
  border-radius: 8px;
  padding: 1.5rem;
  transition: background-color 0.3s ease;
}

.article-title {
  flex: 1;
  font-size: 2rem;
  font-weight: 600;
  padding: 1rem;
  border: none;
  border-bottom: 2px solid #a094b8;
  background: transparent;
  color: var(--text-color);
  outline: none;
  transition: border-color 0.3s, color 0.3s ease;
  margin-right: 2rem;
}

.article-title:focus {
  border-color: #575667;
}

.article-title:read-only {
  border-color: transparent;
  cursor: default;
}

.mode-controls {
  display: flex;
  gap: 1rem;
}

.mode-toggle-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s, transform 0.1s;
}

.mode-toggle-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.mode-toggle-btn.active {
  background: var(--secondary-text);
}

.create-form-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
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
  margin-top: 30px;
  padding: 20px;
  background: var(--form-background);
  border-radius: 8px;
  border: 2px dashed #a094b8;
  transition: background-color 0.3s ease;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  padding-left: 5px;
  border-bottom: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
}

.form-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
  padding: 5px;
  transition: all 0.2s, color 0.3s ease;
  border-radius: 4px;
}

.form-title:not([readonly]):not([disabled]):focus {
  background-color: #fff;
  border: 1px solid #a094b8;
  box-shadow: 0 0 5px rgba(160, 148, 184, 0.3);
}

.form-title:not([readonly]):not([disabled]):hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.form-title[readonly], .form-title[disabled] {
  cursor: default;
  opacity: 0.8;
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

.add-content-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
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
  background: var(--secondary-text);
  color: var(--footer-text);
}

.save-button:hover:not(:disabled) {
  background: #4a4857;
  transform: translateY(-1px);
}

.save-button:disabled {
  background: #d1d5db;
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

.main-heading-style {
  font-size: 36px;
  font-weight: 600;
  color: #24222f;
  margin: 0;
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
  background: var(--accent-color);
}

.toast.error {
  background: var(--error-color);
}

.toast.info {
  background: var(--secondary-text);
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
  border: 2px solid #575667;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.remove-form-btn {
  background: #ef4444;
  color: #f5f9f8;
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
  background: #dc2626;
  transform: translateY(-1px);
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
  align-items: flex-start;
  width: 100%;
  gap: 20px;
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
  margin-top: 1rem;
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
</style>