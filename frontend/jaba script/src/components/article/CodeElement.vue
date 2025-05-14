<template>
  <div class="code-element" :class="{ 'read-only': readOnly && !allowPreviewEdit, 'preview-editable': readOnly && allowPreviewEdit, [currentTheme]: true }">
    <!-- Score display at the top when in read-only mode -->
    <div v-if="readOnly && showScore" class="element-score-display">
      <template v-if="userScore !== null">
        <span :class="{'score-success': userScore === localContent.max_score, 'score-fail': userScore < localContent.max_score}">
          {{ userScore }}/{{ localContent.max_score }}
        </span>
        <button @click="resetSubmission" class="reset-score-btn" title="Сбросить баллы">×</button>
      </template>
      <template v-else>
        <span class="score-pending">{{ localContent.max_score }} баллов</span>
      </template>
    </div>
    
    <!-- Task Description Section -->
    <div class="task-description">
      <h4>Описание задания:</h4>
      <div v-if="!readOnly || allowPreviewEdit" class="description-editor">
        <textarea 
          v-model="localContent.taskDescription" 
          @input="autoSaveChanges" 
          placeholder="Введите описание задания..."
          class="description-input no-resize"
          :readonly="readOnly && !allowPreviewEdit"
        ></textarea>
      </div>
      <div v-else class="description-preview">
        <div v-html="localContent.taskDescription || 'Нет описания задания'"></div>
      </div>
    </div>

    <div class="controls">
      <div class="selector-group">
        <!-- Language selector always visible -->
        <select
          v-model="localContent.language"
          @change="emitUpdate"
          class="language-selector"
          :aria-label="readOnly ? 'Выбрать язык программирования (предпросмотр)' : 'Выбрать язык программирования'"
          :disabled="readOnly && !allowPreviewEdit"
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
          v-if="!readOnly || allowPreviewEdit"
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

        <!-- Theme selector -->
        <select v-if="manualThemeSelection" v-model="currentTheme" class="theme-selector" aria-label="Выбрать тему редактора">
          <option value="vs-light">VS Light</option>
          <option value="vs-dark">VS Dark</option>
          <option value="vs-high-contrast">VS High Contrast</option>
        </select>
        <div v-else class="theme-info">
          <span>{{ currentTheme === 'vs-dark' ? 'Dark Theme' : 'Light Theme' }}</span>
        </div>
      </div>

      <div class="button-group">
        <button
          v-if="canRunCode"
          @click.prevent="runCode"
          class="run-button"
          :disabled="isRunning || !refreshStore.isAuthenticated"
        >
          <span class="icon">▶️</span> {{ isRunning ? 'Running...' : 'Run' }}
        </button>
        
        <!-- Submit button for score in view mode -->
        <button
          v-if="readOnly && !allowPreviewEdit && canRunCode && !codeSubmitted && refreshStore.isAuthenticated"
          @click.prevent="submitCode"
          class="submit-button"
          :disabled="isRunning"
        >
          <span class="icon">✓</span> Отправить на проверку
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
      <textarea
        v-if="allowPreviewEdit"
        v-model="localContent.code"
        @input="autoSaveChanges"
        @keydown="handleKeydown"
        class="code-input"
        aria-label="Редактировать код в предпросмотре"
      ></textarea>
      <pre v-else><code :class="'language-' + localContent.language">{{ localContent.code }}</code></pre>
    </div>

    <!-- Expected Result Section -->
    <div class="expected-result">
      <h4>Ожидаемый результат:</h4>
      <div v-if="!readOnly || allowPreviewEdit" class="expected-editor">
        <textarea 
          v-model="localContent.expectedResult" 
          @input="autoSaveChanges" 
          placeholder="Введите ожидаемый результат..."
          class="expected-input no-resize"
          :readonly="readOnly && !allowPreviewEdit"
        ></textarea>
      </div>
      <div v-else class="expected-preview">
        <pre>{{ localContent.expectedResult || 'Не указан ожидаемый результат' }}</pre>
      </div>
    </div>

    <div v-if="executionResult" class="execution-result" :class="{ error: executionError }">
      <h4>Результат выполнения:</h4>
      <pre>{{ executionResult }}</pre>
      
      <!-- Show comparison with expected result only if not already submitted -->
      <div v-if="localContent.expectedResult && !executionError && !codeSubmitted" class="result-comparison">
        <div v-if="resultMatches" class="result-matches">
          <span class="icon-success">✓</span> Результат совпадает с ожидаемым
        </div>
        <div v-else class="result-differs">
          <span class="icon-error">✗</span> Результат не совпадает с ожидаемым
        </div>
      </div>
    </div>
    
    <!-- Score result after submission -->
    <div v-if="codeSubmitted && userScore !== null" class="submission-result" :class="{ 'success': userScore === localContent.max_score, 'partial': userScore > 0 && userScore < localContent.max_score, 'fail': userScore === 0 }">
      <h4>Результат проверки:</h4>
      <div class="score-result">
        <div class="score-value">{{ userScore }}/{{ localContent.max_score }}</div>
        <div class="score-message">
          <template v-if="userScore === localContent.max_score">
            Отлично! Вы получили максимальный балл.
          </template>
          <template v-else-if="userScore > 0">
            Неплохо, но можно лучше. Попробуйте улучшить ваше решение.
          </template>
          <template v-else>
            Не засчитано. Ваше решение не соответствует требованиям.
          </template>
        </div>
        <button v-if="codeSubmitted" @click="resetSubmission" class="retry-button">
          Попробовать снова
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useRefreshStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/themeStore'

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ 
      language: 'javascript', 
      code: '', 
      interpreter: 'default',
      max_score: 5,
      taskDescription: '',
      expectedResult: ''
    })
  },
  readOnly: {
    type: Boolean,
    default: false
  },
  manualThemeSelection: {
    type: Boolean,
    default: false
  },
  showScore: {
    type: Boolean,
    default: true
  },
  allowPreviewEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:content', 'answer-submitted'])
const router = useRouter()
const refreshStore = useRefreshStore()
const themeStore = useThemeStore()

const localContent = ref({
  code: props.content.code || '',
  language: props.content.language || 'javascript',
  interpreter: props.content.interpreter || 'default',
  max_score: props.content.max_score || 5,
  taskDescription: props.content.taskDescription || '',
  expectedResult: props.content.expectedResult || ''
})

// For code submission scoring
const codeSubmitted = ref(false);
const userScore = ref(null);

const showPreview = ref(props.readOnly)
const executionResult = ref(null)
const executionError = ref(false)
const isRunning = ref(false)

onMounted(() => {
  refreshStore.ready() // Initialize tokens
  loadSavedContent()
  
  // Initialize theme based on site preference
  if (!props.manualThemeSelection) {
    themeValue.value = themeStore.isDarkMode ? 'vs-dark' : 'vs-light'
  }
  
  // Log content ID for debugging
  console.log('CodeElement mounted with content ID:', props.content.id);
  
  // Initialize from localStorage if there's saved progress
  if (props.readOnly && props.content.id) {
    const savedData = localStorage.getItem(`code_${props.content.id}`);
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        codeSubmitted.value = data.codeSubmitted;
        userScore.value = data.userScore;
        console.log(`Loaded saved state for code ${props.content.id}:`, { codeSubmitted: codeSubmitted.value, userScore: userScore.value });
        
        // If we have a saved score, emit it to update the parent in the same format as QuizElement
        if (userScore.value !== null) {
          emit('answer-submitted', {
            contentId: props.content.id,
            score: userScore.value,
            maxScore: localContent.value.max_score
          });
        }
      } catch (e) {
        console.error('Error loading code state:', e);
      }
    } else {
      console.log(`No saved state found for code ${props.content.id}`);
    }
  }
  
  // Set theme based on system preference or store
  updateTheme();
})

// Submit code for scoring
const submitCode = () => {
  if (!localContent.value.code) return;
  
  // Save current scroll position
  const scrollPosition = window.scrollY;
  
  // If we already have execution results, use them directly
  if (executionResult.value !== null) {
    calculateAndSubmitScore();
    
    // Restore scroll position
    setTimeout(() => {
      window.scrollTo({
        top: scrollPosition,
        behavior: 'auto'
      });
    }, 50);
  } else {
    // Run the code first to get the result
    runCode().then(() => {
      calculateAndSubmitScore();
      
      // Restore scroll position
      setTimeout(() => {
        window.scrollTo({
          top: scrollPosition,
          behavior: 'auto'
        });
      }, 50);
    });
  }
};

// Calculate score and submit it
const calculateAndSubmitScore = () => {
  // Calculate score based on matching expected result
  let score = 0;
  
  // If we have an expected result and the execution was successful
  if (localContent.value.expectedResult && !executionError.value) {
    // If result matches expected result, award full points
    if (resultMatches.value) {
      score = localContent.value.max_score;
    } else {
      // Partial score for code that runs without errors but doesn't match
      score = Math.floor(localContent.value.max_score * 0.3);
    }
  } else if (!executionError.value) {
    // If no expected result defined but code runs without errors
    score = Math.floor(localContent.value.max_score * 0.5);
  }
  
  // Update state
  codeSubmitted.value = true;
  userScore.value = score;
  
  // Save to localStorage
  if (props.content.id) {
    localStorage.setItem(`code_${props.content.id}`, JSON.stringify({
      codeSubmitted: codeSubmitted.value,
      userScore: userScore.value
    }));
  }
  
  // Debug logs
  console.log('Submitting score with:', {
    contentId: props.content.id,
    score: userScore.value,
    type: 'code'
  });
  
  // Emit event for parent components in the same format as QuizElement
  emit('answer-submitted', {
    contentId: props.content.id,
    code: localContent.value.code,
    score: userScore.value,
    maxScore: localContent.value.max_score,
    resultMatches: resultMatches.value
  });
  
  // Log the submission for debugging
  console.log('Code submitted:', {
    contentId: props.content.id,
    code: localContent.value.code,
    score: userScore.value,
    maxScore: localContent.value.max_score,
    resultMatches: resultMatches.value
  });
};

// Reset submission to try again
const resetSubmission = () => {
  codeSubmitted.value = false;
  userScore.value = null;
  
  // Clear saved state
  if (props.content.id) {
    localStorage.removeItem(`code_${props.content.id}`);
  }
  
  // Emit event to reset score in parent component in the same format as QuizElement
  emit('answer-submitted', {
    contentId: props.content.id,
    score: 0,
    maxScore: localContent.value.max_score
  });
  
  console.log('Reset submission for:', props.content.id);
};

const loadSavedContent = () => {
  const savedContent = localStorage.getItem('code-editor-content')
  if (savedContent) {
    try {
      const parsedContent = JSON.parse(savedContent)
      localContent.value = {
        code: parsedContent.code || '',
        language: parsedContent.language || 'javascript',
        interpreter: parsedContent.interpreter || 'default',
        max_score: 10,
        taskDescription: parsedContent.taskDescription || '',
        expectedResult: parsedContent.expectedResult || ''
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
    interpreter: localContent.value.interpreter,
    max_score: localContent.value.max_score,
    taskDescription: localContent.value.taskDescription,
    expectedResult: localContent.value.expectedResult
  })
  localStorage.setItem('code-editor-content', JSON.stringify(localContent.value))
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
      localContent.value.code = textarea.value
      emitUpdate()
    }
  }
}

const runCode = async () => {
  if (!canRunCode.value || !refreshStore.isAuthenticated) {
    return Promise.reject(new Error('Cannot run code'));
  }

  // Save current scroll position
  const scrollPosition = window.scrollY;
  
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
      
      // Check if result matches expected result after setting executionResult
      // This is important because resultMatches is a computed property based on executionResult
      const matches = resultMatches.value;
      console.log('Code execution result matches expected:', matches);
      
      // Auto-submit score if there's an expected result and it matches
      if (localContent.value.expectedResult && props.readOnly && !codeSubmitted.value) {
        // If result matches expected result, auto-submit
        if (matches) {
          calculateAndSubmitScore();
        }
      }
    } else {
      executionError.value = true
      executionResult.value = result.stderr || result.compile_output || `Error: ${result.status}`
    }
    
    // Restore scroll position after a short delay to ensure DOM updates
    setTimeout(() => {
      window.scrollTo({
        top: scrollPosition,
        behavior: 'auto'
      });
    }, 50);
    
    return Promise.resolve();
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
    
    // Restore scroll position even in case of error
    setTimeout(() => {
      window.scrollTo({
        top: scrollPosition,
        behavior: 'auto'
      });
    }, 50);
    
    return Promise.reject(error);
  } finally {
    isRunning.value = false
  }
}

// Watch for theme changes in themeStore
watch(() => themeStore.isDarkMode, (isDark) => {
  if (!props.manualThemeSelection) {
    themeValue.value = isDark ? 'vs-dark' : 'vs-light'
  }
})

watch(() => props.content, (newVal) => {
  const savedContent = localStorage.getItem('code-editor-content')
  if (!savedContent) {
    localContent.value = {
      code: newVal.code || '',
      language: newVal.language || 'javascript',
      interpreter: newVal.interpreter || 'default',
      max_score: newVal.max_score || 5,
      taskDescription: newVal.taskDescription || '',
      expectedResult: newVal.expectedResult || ''
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

const autoSaveChanges = () => {
  emitUpdate();
}

// Check if execution result matches expected result
const resultMatches = computed(() => {
  if (!executionResult.value || !localContent.value.expectedResult || executionError.value) {
    return false;
  }
  // Trim whitespace and normalize line endings for comparison
  const normalizedResult = executionResult.value.trim().replace(/\r\n/g, '\n');
  const normalizedExpected = localContent.value.expectedResult.trim().replace(/\r\n/g, '\n');
  return normalizedResult === normalizedExpected;
});

const currentTheme = computed(() => {
  // Automatically use site theme if manualThemeSelection is false
  if (!props.manualThemeSelection) {
    return themeStore.isDarkMode ? 'vs-dark' : 'vs-light'
  }
  // Otherwise use the selected theme
  return themeValue.value
})
const themeValue = ref('vs-dark') // For manual selection

const updateTheme = () => {
  currentTheme.value = themeStore.isDarkMode ? 'vs-dark' : 'vs-light';
};
</script>

<style scoped>
.code-element {
  display: flex;
  flex-direction: column;
  width: 100%;
  font-family: 'Raleway', sans-serif;
  background: var(--form-background);
  border-radius: 8px;
  transition: all 0.3s ease, background-color 0.3s ease;
  /* Fixed width for code elements */
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.code-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: var(--code-header-bg);
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.language-selector {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--form-background);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  max-width: 150px;
}

.code-container {
  position: relative;
  width: 100%;
  overflow: auto;
  /* Ensure code container has proper width */
  max-width: 100%;
}

.code-editor {
  width: 100%;
  min-height: 100px;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  background: var(--code-bg);
  color: var(--code-text);
  border: none;
  border-radius: 0 0 8px 8px;
  resize: vertical;
  tab-size: 4;
  -moz-tab-size: 4;
  transition: background-color 0.3s ease, color 0.3s ease;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.code-editor:focus {
  outline: none;
}

.code-editor.read-only {
  background: var(--code-bg);
  cursor: default;
}

.code-display {
  width: 100%;
  min-height: 100px;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  background: var(--code-bg);
  color: var(--code-text);
  border: none;
  border-radius: 0 0 8px 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  transition: background-color 0.3s ease, color 0.3s ease;
  /* Ensure code display has proper width */
  max-width: 100%;
}

/* Task Description Styles */
.task-description {
  padding: 1rem;
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-color);
}

.task-description h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.description-input, .expected-input {
  width: 100%;
  min-height: 5rem;
  padding: 0.75rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: #ffffff;
  color: #1f2937;
  resize: vertical;
}

.vs-dark .description-input, .vs-dark .expected-input {
  background: #1a1a1a;
  color: #e5e7eb;
  border-color: #4b4b4b;
}

.description-preview, .expected-preview {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.375rem;
}

/* Expected Result Styles */
.expected-result {
  padding: 1rem;
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-color);
}

.expected-result h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

/* Result Comparison Styles */
.result-comparison {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.result-matches {
  color: #15803d;
  font-weight: 500;
}

.result-differs {
  color: #b91c1c;
  font-weight: 500;
}

.icon-success {
  color: #15803d;
  margin-right: 0.5rem;
}

.icon-error {
  color: #b91c1c;
  margin-right: 0.5rem;
}

.code-element.vs-light {
  background: #f8fafc;
  color: var(--text-color);
}

.code-element.vs-dark {
  background: #1a1a1a;
  color: #e5e7eb;
}

.code-element.vs-high-contrast {
  background: #000000;
  color: #ffffff;
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
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.theme-info {
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--form-background);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.read-only .language-selector {
  background: #e5e7eb;
}

.vs-dark .language-selector,
.vs-dark .interpreter-selector,
.vs-dark .theme-selector,
.vs-dark .theme-info {
  background: #2d2d2d;
  color: #e5e7eb;
  border-color: #4b4b4b;
}

.read-only.vs-dark .language-selector {
  background: #2d2d2d;
}

.vs-high-contrast .language-selector,
.vs-high-contrast .interpreter-selector,
.vs-high-contrast .theme-selector,
.vs-high-contrast .theme-info {
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
  background: var(--accent-color);
  color: var(--footer-text);
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

.run-button:disabled:hover {
  cursor: not-allowed;
  background-color: #444;
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
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease, color 0.2s ease;
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
  position: relative;
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  box-sizing: border-box;
  word-break: break-all;
  transition: all 0.3s ease;
}

.code-preview pre {
  margin: 0;
  background: #1e293b;
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.code-preview pre code {
  color: #e5e7eb;
  transition: color 0.3s ease;
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
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: 0.5rem;
  transition: border-color 0.3s ease;
}

.preview-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: flex-end;
}

.execution-result {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  background: #e5e7eb;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  word-break: break-all;
  transition: background-color 0.3s ease, color 0.3s ease;
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

.vs-dark .execution-result.error {
  background: #4c1d1d;
  color: #fca5a5;
}

.vs-high-contrast .execution-result.error {
  background: #300000;
  color: #ff8080;
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
  transition: background-color 0.3s ease, color 0.3s ease;
}

.vs-dark .auth-warning {
  background: #3f3000;
  color: #fcd34d;
}

.vs-high-contrast .auth-warning {
  background: #2a2000;
  color: #fde68a;
}

.auth-warning a {
  color: #1d4ed8;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.vs-dark .auth-warning a {
  color: #93c5fd;
}

.vs-high-contrast .auth-warning a {
  color: #bfdbfe;
}

.score-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.score-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.score-display {
  padding: 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.score-success {
  color: #2e8b33;
  font-weight: 700;
}

.score-fail {
  color: var(--error-color, #da1f38);
  font-weight: 700;
}

.score-pending {
  color: var(--secondary-text, #575667);
}

.submission-result {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  background: #e5e7eb;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  word-break: break-all;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.vs-dark .submission-result {
  background: #2d2d2d;
  color: #e5e7eb;
}

.vs-high-contrast .submission-result {
  background: #1a1a1a;
  color: #ffffff;
}

.submission-result h4 {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.score-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-value {
  font-weight: 600;
}

.score-message {
  margin-left: 0.5rem;
}

.retry-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: #6b7280;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background-color: #5b6370;
}

.submit-button {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: #10b981;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-button:hover {
  background-color: #059669;
  transform: translateY(-1px);
}

.submit-button:disabled {
  background-color: #6b7280;
  cursor: not-allowed;
  opacity: 0.7;
}

.submit-button:disabled:hover {
  cursor: not-allowed;
  background-color: #6b7280;
  transform: none;
}

.preview-edit-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: flex-end;
}

.save-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.save-button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.cancel-button {
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.cancel-button:hover {
  background: #4b5563;
  transform: translateY(-1px);
}

.description-input:read-only, .expected-input:read-only {
  cursor: pointer;
  background-color: rgba(0, 0, 0, 0.03);
}

.vs-dark .description-input:read-only, .vs-dark .expected-input:read-only {
  background-color: rgba(255, 255, 255, 0.05);
}

.description-input:read-only:hover, .expected-input:read-only:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.vs-dark .description-input:read-only:hover, .vs-dark .expected-input:read-only:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Hint for double-click to edit */
.description-input:read-only::after, .expected-input:read-only::after {
  content: "Двойной клик для редактирования";
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  font-size: 0.75rem;
  color: #6b7280;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.description-input:read-only:hover::after, .expected-input:read-only:hover::after {
  opacity: 1;
}

/* Admin edit indicator styles - removing as they're not used */

.code-element.preview-editable {
  border: 2px dashed var(--accent-color);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.code-element.preview-editable:hover {
  border-color: #8b7ca5;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.15);
}

.vs-dark .code-element.preview-editable {
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}

.vs-dark .code-element.preview-editable:hover {
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.15);
}

.no-resize {
  resize: none;
}

.element-score-display {
  width: 100%;
  text-align: left;
  padding: 8px 12px;
  margin-bottom: 10px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.05);
  font-weight: bold;
  color: var(--text-color, #24222f);
  align-self: stretch;
  box-sizing: border-box;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vs-dark .element-score-display {
  background: rgba(255, 255, 255, 0.08);
  color: #e5e7eb;
}

.vs-dark .score-success {
  color: #6bdb70;
}

.vs-dark .score-fail {
  color: #ff6b6b;
}

.vs-high-contrast .element-score-display {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.reset-score-btn {
  background: var(--error-color, #da1f38);
  color: white;
  border: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
  flex-shrink: 0;
  opacity: 0.7;
}

.reset-score-btn:hover {
  background: var(--hover-delete, #c62828);
  transform: scale(1.1);
  opacity: 1;
}

.vs-dark .reset-score-btn {
  background: #ff4d4d;
}

.vs-dark .reset-score-btn:hover {
  background: #ff3333;
}
</style>