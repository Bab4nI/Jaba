<template>
  <div class="code-element" :class="{ 'read-only': readOnly, [currentTheme]: true }">
    <div class="controls">
      <div class="selector-group">
        <!-- Language selector always visible -->
        <select
          v-model="localContent.language"
          @change="emitUpdate"
          class="language-selector"
          :aria-label="readOnly ? 'Выбрать язык программирования (предпросмотр)' : 'Выбрать язык программирования'"
        >
          <option value="javascript">JavaScript</option>
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="kotlin">Kotlin</option>
          <option value="go">Go</option>
          <option value="rust">Rust</option>
          <option value="cpp">C++</option>
          <option value="csharp">C#</option>
          <option value="php">PHP</option>
          <option value="ruby">Ruby</option>
          <option value="swift">Swift</option>
          <option value="scala">Scala</option>
        </select>

        <!-- Interpreter selector only in edit mode, label in preview mode -->
        <select
          v-if="!readOnly"
          v-model="localContent.interpreter"
          @change="emitUpdate"
          class="interpreter-selector"
          aria-label="Выбрать интерпретатор"
        >
          <option value="default">Default</option>
          <option v-if="localContent.language === 'javascript'" value="node">Node.js</option>
          <option v-if="localContent.language === 'python'" value="cpython">CPython</option>
          <option v-if="localContent.language === 'python'" value="pypy">PyPy</option>
          <option v-if="localContent.language === 'java'" value="openjdk">OpenJDK</option>
          <option v-if="localContent.language === 'kotlin'" value="kotlin-jvm">Kotlin JVM</option>
          <option v-if="localContent.language === 'go'" value="go">Go</option>
          <option v-if="localContent.language === 'rust'" value="rustc">Rustc</option>
          <option v-if="localContent.language === 'cpp'" value="g++">G++</option>
          <option v-if="localContent.language === 'csharp'" value="mono">Mono</option>
          <option v-if="localContent.language === 'php'" value="php">PHP</option>
          <option v-if="localContent.language === 'ruby'" value="mri">MRI</option>
          <option v-if="localContent.language === 'swift'" value="swift">Swift</option>
          <option v-if="localContent.language === 'scala'" value="scala">Scala</option>
        </select>
        <span v-else-if="localContent.interpreter && localContent.interpreter !== 'default'" class="interpreter-label">{{ interpreterLabel }}</span>

        <select v-model="currentTheme" class="theme-selector" aria-label="Выбрать тему редактора">
          <option value="vs-light">VS Light</option>
          <option value="vs-dark">VS Dark</option>
          <option value="vs-high-contrast">VS High Contrast</option>
        </select>
      </div>

      <div class="button-group">
        <button
          v-if="canRunCode"
          @click="runCode"
          class="run-button"
          :disabled="isRunning || !refreshStore.isAuthenticated"
        >
          <span class="icon">▶️</span> {{ isRunning ? 'Running...' : 'Run' }}
        </button>
      </div>
    </div>

    <div v-if="!refreshStore.isAuthenticated && canRunCode" class="auth-warning">
      <p>Please <a href="/login">log in</a> to run code.</p>
    </div>

    <textarea
      v-if="!readOnly && !showPreview"
      v-model="localContent.code"
      @input="emitUpdate"
      @keydown="handleKeydown"
      placeholder="Enter your code..."
      class="code-input"
      aria-label="Редактировать код"
    ></textarea>

    <div v-if="localContent.code && (readOnly || showPreview)" class="code-preview">
      <pre v-if="!isEditingPreview"><code :class="'language-' + localContent.language">{{ localContent.code }}</code></pre>
      <textarea
        v-else
        v-model="editingCode"
        @input="updateEditingCode"
        @blur="savePreviewChanges"
        @keydown="handleKeydown"
        @keydown.ctrl.enter="saveAndRun"
        class="code-input"
        aria-label="Редактировать код в предпросмотре"
      ></textarea>
      <div class="preview-controls" v-if="showPreview && !readOnly">
        <button @click="toggleEditPreview" class="edit-button">
          {{ isEditingPreview ? 'Save' : 'Edit' }}
        </button>
        <button
          v-if="isEditingPreview"
          @click="saveAndRun"
          class="run-button"
          :disabled="isRunning || !refreshStore.isAuthenticated"
        >
          <span class="icon">▶️</span> Save and Run
        </button>
      </div>
    </div>

    <div v-if="executionResult" class="execution-result" :class="{ error: executionError }">
      <h4>Execution Result:</h4>
      <pre>{{ executionResult }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useRefreshStore } from '@/stores/auth'

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ language: 'javascript', code: '', interpreter: 'default' })
  },
  readOnly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:content'])
const router = useRouter()
const refreshStore = useRefreshStore()

const localContent = ref({
  code: props.content.code || '',
  language: props.content.language || 'javascript',
  interpreter: props.content.interpreter || 'default'
})
const showPreview = ref(props.readOnly)
const executionResult = ref(null)
const executionError = ref(false)
const isRunning = ref(false)
const isEditingPreview = ref(false)
const editingCode = ref('')
const currentTheme = ref('vs-dark')

onMounted(() => {
  refreshStore.ready() // Initialize tokens
  loadSavedContent()
})

const loadSavedContent = () => {
  const savedContent = localStorage.getItem('code-editor-content')
  if (savedContent) {
    try {
      const parsedContent = JSON.parse(savedContent)
      localContent.value = {
        code: parsedContent.code || '',
        language: parsedContent.language || 'javascript',
        interpreter: parsedContent.interpreter || 'default'
      }
      emitUpdate()
    } catch (error) {
      console.error('Error parsing saved content:', error)
    }
  }
}

const languageLabel = computed(() => {
  const labels = {
    javascript: 'JavaScript',
    python: 'Python',
    java: 'Java',
    kotlin: 'Kotlin',
    go: 'Go',
    rust: 'Rust',
    cpp: 'C++',
    csharp: 'C#',
    php: 'PHP',
    ruby: 'Ruby',
    swift: 'Swift',
    scala: 'Scala'
  }
  return labels[localContent.value.language] || localContent.value.language.toUpperCase()
})

const interpreterLabel = computed(() => {
  const labels = {
    default: 'Default',
    node: 'Node.js',
    cpython: 'CPython',
    pypy: 'PyPy',
    openjdk: 'OpenJDK',
    'kotlin-jvm': 'Kotlin JVM',
    go: 'Go',
    rustc: 'Rustc',
    'g++': 'G++',
    mono: 'Mono',
    php: 'PHP',
    mri: 'MRI',
    swift: 'Swift',
    scala: 'Scala'
  }
  return labels[localContent.value.interpreter] || localContent.value.interpreter
})

const canRunCode = computed(() => {
  const executableLanguages = ['javascript', 'python', 'java', 'kotlin', 'go', 'rust', 'cpp', 'csharp', 'php', 'ruby', 'swift', 'scala']
  return executableLanguages.includes(localContent.value.language) && localContent.value.code
})

const emitUpdate = () => {
  emit('update:content', {
    code: localContent.value.code,
    language: localContent.value.language,
    interpreter: localContent.value.interpreter
  })
  localStorage.setItem('code-editor-content', JSON.stringify(localContent.value))
}

const toggleEditPreview = () => {
  isEditingPreview.value = !isEditingPreview.value
  if (isEditingPreview.value) {
    editingCode.value = localContent.value.code
  } else {
    savePreviewChanges()
  }
}

const updateEditingCode = () => {
  // Update editingCode without immediately saving to localContent
}

const savePreviewChanges = () => {
  if (isEditingPreview.value) {
    localContent.value.code = editingCode.value
    isEditingPreview.value = false
    emitUpdate()
  }
}

const saveAndRun = () => {
  savePreviewChanges()
  runCode()
}

const handleKeydown = (event) => {
  if (event.key === 'Tab') {
    event.preventDefault()
    const textarea = event.target
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const value = textarea.value

    textarea.value = value.substring(0, start) + '  ' + value.substring(end)
    textarea.selectionStart = textarea.selectionEnd = start + 2

    if (!showPreview.value) {
      localContent.value.code = textarea.value
      emitUpdate()
    } else {
      editingCode.value = textarea.value
    }
  }
}

const runCode = async () => {
  if (!canRunCode.value || !refreshStore.isAuthenticated) {
    return
  }

  isRunning.value = true
  executionResult.value = null
  executionError.value = false

  try {
    const token = refreshStore.accessToken
    if (!token) {
      throw new Error('Authentication token missing')
    }

    const response = await axios.post(
      'http://localhost:8000/api/execute-code/',
      {
        source_code: localContent.value.code,
        language_id: localContent.value.language,
        interpreter: localContent.value.interpreter,
        stdin: ''
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const result = response.data

    if (result.status === 'Accepted') {
      executionResult.value = result.stdout || 'Program executed without output.'
    } else {
      executionError.value = true
      executionResult.value = result.stderr || result.compile_output || `Error: ${result.status}`
    }
  } catch (error) {
    console.error('Code execution error:', error)
    executionError.value = true

    if (error.response) {
      if (error.response.status === 401) {
        executionResult.value = 'Authentication error. Trying to refresh token...'
        try {
          await refreshStore.refreshToken()
          if (refreshStore.isAuthenticated) {
            executionResult.value = 'Token refreshed. Please try running the code again.'
          } else {
            executionResult.value = 'Authentication failed. Please log in again.'
            router.push('/login')
          }
        } catch (refreshError) {
          executionResult.value = 'Failed to refresh token. Please log in again.'
          router.push('/login')
        }
      } else if (error.response.status === 400) {
        executionResult.value = error.response.data.error || 'Invalid request. Check data.'
      } else if (error.response.status === 408) {
        executionResult.value = 'Timeout. Program took too long to execute.'
      } else {
        executionResult.value = 'Error executing code. Try again later.'
      }
    } else {
      executionResult.value = 'Failed to connect to server. Check connection.'
    }
  } finally {
    isRunning.value = false
  }
}

watch(() => props.content, (newVal) => {
  const savedContent = localStorage.getItem('code-editor-content')
  if (!savedContent) {
    localContent.value = {
      code: newVal.code || '',
      language: newVal.language || 'javascript',
      interpreter: newVal.interpreter || 'default'
    }
  }
}, { deep: true })

watch(() => localContent.value.language, (newLang) => {
  const validInterpreters = getValidInterpreters(newLang)
  if (!validInterpreters.includes(localContent.value.interpreter)) {
    localContent.value.interpreter = 'default'
    emitUpdate()
  }
})

const getValidInterpreters = (language) => {
  const interpreterMap = {
    javascript: ['default', 'node'],
    python: ['default', 'cpython', 'pypy'],
    java: ['default', 'openjdk'],
    kotlin: ['default', 'kotlin-jvm'],
    go: ['default', 'go'],
    rust: ['default', 'rustc'],
    cpp: ['default', 'g++'],
    csharp: ['default', 'mono'],
    php: ['default', 'php'],
    ruby: ['default', 'mri'],
    swift: ['default', 'swift'],
    scala: ['default', 'scala']
  }
  return interpreterMap[language] || ['default']
}
</script>

<style scoped>
.code-element {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  font-family: 'Inter', sans-serif;
  max-width: 100%;
  box-sizing: border-box;
}

.code-element.vs-light {
  background: #f8fafc;
}

.code-element.vs-dark {
  background: #1a1a1a;
}

.code-element.vs-high-contrast {
  background: #000000;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.selector-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.language-selector,
.interpreter-selector,
.theme-selector {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: #ffffff;
  font-size: 0.875rem;
  color: #374151;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.read-only .language-selector {
  background: #e5e7eb;
}

.vs-dark .language-selector,
.vs-dark .interpreter-selector,
.vs-dark .theme-selector {
  background: #2d2d2d;
  color: #e5e7eb;
  border-color: #4b4b4b;
}

.read-only.vs-dark .language-selector {
  background: #2d2d2d;
}

.vs-high-contrast .language-selector,
.vs-high-contrast .interpreter-selector,
.vs-high-contrast .theme-selector {
  background: #1a1a1a;
  color: #ffffff;
  border-color: #ffffff;
}

.read-only.vs-high-contrast .language-selector {
  background: #1a1a1a;
}

.language-selector:focus,
.interpreter-selector:focus,
.theme-selector:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.language-label,
.interpreter-label {
  padding: 0.5rem 0.75rem;
  background: #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
}

.vs-dark .language-label,
.vs-dark .interpreter-label {
  background: #2d2d2d;
  color: #e5e7eb;
}

.vs-high-contrast .language-label,
.vs-high-contrast .interpreter-label {
  background: #1a1a1a;
  color: #ffffff;
}

.button-group {
  display: flex;
  gap: 0.5rem;
}

.run-button,
.edit-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.run-button {
  background: #3b82f6;
  color: white;
}

.edit-button {
  background: #6b7280;
  color: white;
}

.run-button:hover,
.edit-button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.run-button:active,
.edit-button:active {
  transform: translateY(0);
}

.run-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.icon {
  font-size: 1rem;
}

.code-input {
  width: 100%;
  min-height: 15rem;
  padding: 0.75rem;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: #ffffff;
  color: #1f2937;
  resize: vertical;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
  word-break: break-all;
  overflow-x: hidden;
}

.vs-dark .code-input {
  background: #1a1a1a;
  color: #e5e7eb;
  border-color: #4b4b4b;
}

.vs-high-contrast .code-input {
  background: #000000;
  color: #ffffff;
  border-color: #ffffff;
}

.code-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.code-preview {
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: hidden;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  box-sizing: border-box;
  word-break: break-all;
}

.code-preview pre {
  margin: 0;
  background: #1e293b;
  padding: 1rem;
  border-radius: 0.375rem;
}

.code-preview pre code {
  color: #e5e7eb;
}

.vs-light .code-preview pre {
  background: #f8fafc;
}

.vs-light .code-preview pre code {
  color: #1f2937;
}

.vs-dark .code-preview pre {
  background: #1a1a1a;
}

.vs-dark .code-preview pre code {
  color: #e5e7eb;
}

.vs-high-contrast .code-preview pre {
  background: #000000;
}

.vs-high-contrast .code-preview pre code {
  color: #ffffff;
}

.code-element.read-only .code-preview {
  border: 1px solid #d1d5db;
  padding: 1rem;
  border-radius: 0.5rem;
}

.execution-result {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  background: #e5e7eb;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  word-break: break-all;
}

.vs-dark .execution-result {
  background: #2d2d2d;
  color: #e5e7eb;
}

.vs-high-contrast .execution-result {
  background: #1a1a1a;
  color: #ffffff;
}

.execution-result.error {
  background: #fee2e2;
  color: #b91c1c;
}

.execution-result h4 {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.execution-result pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.auth-warning {
  padding: 0.5rem;
  background: #fef3c7;
  border-radius: 0.25rem;
  color: #92400e;
  font-size: 0.875rem;
}

.auth-warning a {
  color: #1d4ed8;
  text-decoration: underline;
}
</style>