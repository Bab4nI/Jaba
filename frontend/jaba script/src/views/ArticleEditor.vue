<template>
  <div class="article-editor-container">
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

    <!-- AI Modal -->
    <div v-if="aiStore.modalVisible" class="ai-modal" role="dialog" aria-labelledby="ai-modal-title">
      <div class="ai-modal-content">
        <button class="ai-modal-close" @click="closeAiModal" aria-label="Закрыть модальное окно">×</button>
        <h3 id="ai-modal-title">Работа с выделенным текстом</h3>
        <div class="selected-text-preview">{{ aiStore.selectedText }}</div>

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

        <div v-if="aiStore.isLoading" class="ai-loading">
          <span class="spinner"></span> Идет обработка запроса...
        </div>
        <div v-else-if="aiStore.error" class="ai-error">Ошибка AI: {{ aiStore.error }}</div>
        <div v-else-if="aiStore.aiResponse" class="ai-response">
          <h4>Ответ:</h4>
          <div class="ai-response-content">{{ aiStore.aiResponse }}</div>
          <div class="ai-response-actions">
            <button @click="insertAiResponse" class="ai-insert-btn">Вставить в статью</button>
            <button @click="copyAiResponse" class="ai-copy-btn">Копировать</button>
          </div>
        </div>

        <div class="ai-modal-footer">
          <button @click="closeAiModal" class="ai-close-btn">Закрыть</button>
        </div>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="editor-header">
      <h1>{{ article.title }}</h1>
      <div class="header-controls">
        <button
          v-if="userStore.role === 'admin'"
          @click="toggleMode"
          class="mode-toggle-button"
          :aria-label="mode === 'edit' ? 'Переключить на предпросмотр' : 'Переключить на редактирование'"
        >
          {{ mode === 'edit' ? 'Предпросмотр' : 'Редактировать' }}
        </button>
        <button @click="goBack" class="back-button" aria-label="Вернуться к модулям">← Назад к модулям</button>
      </div>
    </div>

    <div class="contents-list">
      <div v-if="mode === 'edit' && userStore.role === 'admin'" class="editable-content">
        <div
          v-for="(element, index) in contents"
          :key="element.id || `temp-${index}`"
          class="content-item"
          :class="{ 'editable': !isContentReadOnly }"
        >
          <div class="content-toolbar">
            <div class="order-controls">
              <button
                :disabled="index === 0"
                @click="moveContentUp(index)"
                class="order-btn"
                title="Переместить вверх"
                aria-label="Переместить элемент вверх"
              >
                ↑
              </button>
              <button
                :disabled="index === contents.length - 1"
                @click="moveContentDown(index)"
                class="order-btn"
                title="Переместить вниз"
                aria-label="Переместить элемент вниз"
              >
                ↓
              </button>
            </div>
            <span class="content-type">{{ getContentTypeName(element.type) }}</span>
            <button
              @click="removeContent(index)"
              class="remove-content-btn"
              aria-label="Удалить элемент"
            >
              ×
            </button>
          </div>

          <component
            :is="getContentComponent(element.type)"
            :content="element"
            :lesson-id="article.id"
            :read-only="isContentReadOnly"
            @update:content="onContentUpdate(index, $event)"
            @text-selected="handleTextSelection"
          />
        </div>
      </div>
      <div v-else class="preview-content">
        <div v-for="(element, index) in contents" :key="element.id || index" class="content-item">
          <component
            :is="getContentComponent(element.type)"
            :content="element"
            :lesson-id="article.id"
            :read-only="true"
            @text-selected="handleTextSelection"
          />
        </div>
      </div>
    </div>

    <div v-if="mode === 'edit' && userStore.role === 'admin'" class="editor-toolbar">
      <select
        v-model="selectedContentType"
        class="content-type-select"
        aria-label="Выбрать тип контента"
      >
        <option value="">Добавить элемент...</option>
        <option value="text">Текст</option>
        <option value="image">Изображение</option>
        <option value="video">Видео</option>
        <option value="code">Код</option>
        <option value="quiz">Тест</option>
        <option value="table">Таблица</option>
        <option value="file">Файл</option>
      </select>

      <button
        @click="addContent"
        class="add-content-btn"
        :disabled="!selectedContentType"
        aria-label="Добавить новый элемент контента"
      >
        Добавить
      </button>
    </div>

    <div v-if="mode === 'edit' && userStore.role === 'admin'" class="editor-footer">
      <button
        @click="saveAllChanges"
        class="save-button"
        :disabled="isSaving || !hasChanges"
        aria-label="Сохранить все изменения"
      >
        <span v-if="isSaving" class="spinner"></span>
        {{ isSaving ? 'Сохранение...' : 'Сохранить работу' }}
        <span v-if="hasChanges" class="changes-indicator">*</span>
      </button>
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
  </div>
</template>

<script>
// The script section remains unchanged unless additional logic is needed for UX improvements.
// For brevity, I'll assume the original script logic is sufficient, with minor additions for toast dismissal.

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAIStore } from '@/stores/aiStore'
import api from '@/api'
import { debounce } from 'lodash-es'

// Components
import TextElement from '@/components/article/TextElement.vue'
import ImageElement from '@/components/article/ImageElement.vue'
import VideoElement from '@/components/article/VideoElement.vue'
import CodeElement from '@/components/article/CodeElement.vue'
import QuizElement from '@/components/article/QuizElement.vue'
import TableElement from '@/components/article/TableElement.vue'
import FileElement from '@/components/article/FileElement.vue'

const CONTENT_TYPES = {
  text: 'TEXT',
  image: 'IMAGE',
  video: 'VIDEO',
  code: 'CODE',
  quiz: 'QUIZ',
  table: 'TABLE',
  file: 'FILE',
}

const DEFAULT_CONTENT = {
  text: { text: '', readOnly: true },
  image: { image: null, readOnly: true },
  video: { video_url: '', readOnly: true },
  code: { code: '', language: 'javascript', readOnly: false },
  quiz: { question: '', answers: ['', ''], correct_answer: null, readOnly: true },
  table: { headers: ['Заголовок 1', 'Заголовок 2'], data: [['', ''], ['', '']], readOnly: true },
  file: { file: null, filename: null, readOnly: true },
}

export default {
  components: {
    TextElement,
    ImageElement,
    VideoElement,
    CodeElement,
    QuizElement,
    TableElement,
    FileElement,
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

    const isContentReadOnly = computed(() => {
      return mode.value !== 'edit' || userStore.role !== 'admin'
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
      if (!hasChanges.value) {
        showToast('Нет изменений для сохранения.', 'info')
        return
      }

      isSaving.value = true
      const errors = []

      try {
        const indicesToSave = [...changedIndices.value]
        const promises = indicesToSave.map(async (index) => {
          const content = contents.value[index]

          if (content.type === 'file' && content.file instanceof File) {
            const formData = new FormData()
            formData.append('file', content.file)
            formData.append('lesson', article.value.id)
            if (content.filename) formData.append('title', content.filename)

            try {
              const response = await api.post(`/api/lessons/${article.value.id}/files/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
              })
              return { success: true, data: response.data, index }
            } catch (error) {
              return { success: false, error, index }
            }
          } else {
            const payload = {
              lesson: article.value.id,
              content_type: CONTENT_TYPES[content.type],
              order: content.order,
            }

            if (content.type === 'text') {
              payload.text = content.text || ''
            } else if (content.type === 'image') {
              payload.image = content.image
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
            } else if (content.type === 'file') {
              payload.file = content.file
              payload.title = content.filename
            }

            try {
              const response = await (content.id
                ? api.put(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/${content.id}/`, payload)
                : api.post(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`, payload)
              )
              return { success: true, data: response.data, index }
            } catch (error) {
              return { success: false, error, index }
            }
          }
        })

        const results = await Promise.all(promises)
        results.forEach((result) => {
          if (result.success) {
            const { data, index } = result
            contents.value[index] = {
              ...contents.value[index],
              id: data.id,
              file: data.file || contents.value[index].file,
              filename: data.title || data.filename || contents.value[index].filename
            }
            changedIndices.value.delete(index)
          } else {
            const { error, index } = result
            const errorMessage = error.response?.data?.detail || error.message
            errors.push(`Элемент ${index + 1} (${getContentTypeName(contents.value[index].type)}): ${errorMessage}`)
          }
        })

        if (errors.length > 0) {
          showToast(`Ошибки при сохранении: ${errors.join('; ')}`, 'error')
        } else {
          originalContents.value = JSON.parse(JSON.stringify(contents.value))
          changedIndices.value.clear()
          lastSavedAt.value = new Date()
          await saveOrder()
          showToast('Все изменения успешно сохранены!', 'success')
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
        const response = await api.get(`/courses/${route.params.courseSlug}/modules/${route.params.moduleId}/lessons/${article.value.id}/contents/`)
        contents.value = response.data.sort((a, b) => a.order - b.order).map(item => ({
          ...item,
          filename: item.type === 'file' ? item.title : item.filename
        }))
        originalContents.value = JSON.parse(JSON.stringify(contents.value))
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

    onMounted(() => {
      document.addEventListener('mouseup', handleGlobalTextSelection)
      window.addEventListener('beforeunload', beforeUnloadHandler)
      userStore.fetchUserProfile()
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
    }
  },
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.article-editor-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.editor-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
  width: 100%;
}

.editor-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  flex: 1 1 100%;
  margin-bottom: 16px;
}

.header-controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  width: 100%;
  justify-content: flex-end;
}

.mode-toggle-button,
.back-button {
  background: #6b7280;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.mode-toggle-button:hover,
.back-button:hover {
  background: #4b5563;
  transform: translateY(-1px);
}

.back-button {
  background: #a094b8;
}

.back-button:hover {
  background: #8b7ca5;
}

.editor-toolbar {
  display: flex;
  gap: 16px;
  margin: 32px 0;
  align-items: center;
  width: 100%;
  flex-wrap: wrap;
}

.content-type-select {
  flex: 1;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  background: #fff;
  min-width: 200px;
}

.add-content-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.add-content-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.add-content-btn:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.contents-list {
  margin: 32px 0;
  width: 100%;
}

.editable-content,
.preview-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.content-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
}

.content-item.editable {
  border-color: #4a6fa5;
  background: #f9fafb;
}

.content-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  width: 100%;
}

.order-controls {
  display: flex;
  gap: 12px;
  margin-right: 16px;
}

.order-btn {
  background: #6b7280;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.1s;
}

.order-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.order-btn:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-1px);
}

.content-type {
  flex-grow: 1;
  font-weight: 600;
  color: #374151;
  font-size: 16px;
}

.remove-content-btn {
  background: #ef4444;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: background 0.2s, transform 0.1s;
}

.remove-content-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.preview-mode .content-item {
  border: none;
  padding: 16px 0;
  background: transparent;
}

.preview-mode .content-toolbar {
  display: none;
}

.editor-footer {
  margin-top: 40px;
  text-align: center;
  width: 100%;
}

.save-button {
  background: #a094b8;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: background 0.2s, transform 0.1s;
  min-width: 200px;
  margin: 0 auto;
}

.save-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.save-button:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.changes-indicator {
  color: #ef4444;
  font-weight: bold;
  margin-left: 8px;
}

.ai-modal {
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

.ai-modal-content {
  background: white;
  padding: 32px;
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  position: relative;
}

.ai-modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #ef4444;
  color: white;
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

.selected-text-preview {
  background: #f3f4f6;
  padding: 16px;
  border-radius: 8px;
  margin: 20px 0;
  font-style: italic;
  border-left: 4px solid #4a6fa5;
  color: #1f2937;
  max-height: 150px;
  overflow-y: auto;
}

.ai-prompt-input {
  width: 100%;
  min-height: 120px;
  padding: 14px;
  margin: 20px 0;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-family: inherit;
  resize: vertical;
  font-size: 16px;
}

.ai-quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.ai-action-btn {
  background: #4a6fa5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s, transform 0.1s;
  min-width: 100px;
}

.ai-action-btn:hover {
  background: #3a5a80;
  transform: translateY(-1px);
}

.ai-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #6b7280;
  font-style: italic;
  margin: 24px 0;
  text-align: center;
}

.ai-error {
  color: #dc2626;
  margin: 24px 0;
  padding: 16px;
  background: #fef2f2;
  border-radius: 8px;
}

.ai-response {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.ai-response-content {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  white-space: pre-wrap;
  font-size: 16px;
  color: #1f2937;
}

.ai-response-actions {
  display: flex;
  gap: 16px;
  margin-top: 20px;
}

.ai-insert-btn,
.ai-copy-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.ai-insert-btn:hover,
.ai-copy-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.ai-copy-btn {
  background: #3b82f6;
}

.ai-copy-btn:hover {
  background: #2563eb;
}

.ai-modal-footer {
  margin-top: 24px;
  text-align: right;
}

.ai-close-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.ai-close-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.ai-floating-btn {
  position: absolute;
  background: #4a6fa5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 999;
  transition: background 0.2s, transform 0.1s;
}

.ai-floating-btn:hover {
  background: #3a5a80;
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
  color: #dc2626;
  background: #fef2f2;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: center;
  font-size: 16px;
  width: 100%;
}

.retry-button {
  background: #4a6fa5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 16px;
  transition: background 0.2s, transform 0.1s;
  min-width: 120px;
}

.retry-button:hover {
  background: #3a5a80;
  transform: translateY(-1px);
}

.spinner {
  border: 3px solid #e5e7eb;
  border-top: 3px solid #4a6fa5;
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
  border-radius: 8px;
  color: white;
  font-size: 16px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 90%;
}

.toast.success {
  background: #10b981;
}

.toast.error {
  background: #ef4444;
}

.toast.info {
  background: #3b82f6;
}

.toast-close {
  background: transparent;
  color: white;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
}

@media (max-width: 768px) {
  .article-editor-container {
    padding: 16px;
  }

  .editor-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .editor-header h1 {
    font-size: 28px;
  }

  .header-controls {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .mode-toggle-button,
  .back-button {
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

  .ai-modal-content {
    padding: 24px;
    width: 95%;
    max-width: 95%;
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
  .editor-header h1 {
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

  .ai-modal-content {
    padding: 16px;
  }

  .ai-prompt-input {
    font-size: 14px;
  }

  .selected-text-preview {
    font-size: 14px;
  }
}
</style>