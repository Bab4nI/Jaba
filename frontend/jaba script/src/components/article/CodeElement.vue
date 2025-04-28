<template>
  <div class="code-element" :class="{ 'read-only': readOnly, [currentTheme]: true }">
    <div class="controls">
      <div class="selector-group">
        <select
          v-if="!readOnly"
          v-model="localContent.language"
          @change="emitUpdate"
          class="language-selector"
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
        <span v-else class="language-label">{{ languageLabel }}</span>

        <select
          v-if="!readOnly"
          v-model="localContent.interpreter"
          @change="emitUpdate"
          class="interpreter-selector"
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
        <span v-else-if="localContent.interpreter" class="interpreter-label">{{ interpreterLabel }}</span>

        <select v-model="currentTheme" class="theme-selector">
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
          :disabled="isRunning || !isAuthenticated"
        >
          <span class="icon">▶️</span> {{ isRunning ? 'Running...' : 'Run' }}
        </button>
      </div>
    </div>

    <div v-if="!isAuthenticated && canRunCode" class="auth-warning">
      <p>Please <a href="/login">log in</a> to run code.</p>
    </div>

    <textarea
      v-if="!readOnly && !showPreview"
      v-model="localContent.code"
      @input="emitUpdate"
      @keydown="handleKeydown"
      placeholder="Enter your code..."
      class="code-input"
    ></textarea>
    
    <div v-if="localContent.code && (readOnly || showPreview)" class="code-preview">
      <pre v-if="!isEditingPreview"><code :class="'language-' + localContent.language">{{ localContent.code }}</code></pre>
      <textarea
        v-else
        v-model="editingCode"
        @blur="savePreviewChanges"
        @keydown="handleKeydown"
        @keydown.ctrl.enter="saveAndRun"
        class="code-input"
      ></textarea>
      <div class="preview-controls" v-if="showPreview && !readOnly">
        <button @click="toggleEditPreview" class="edit-button">
          {{ isEditingPreview ? 'Save' : 'Edit' }}
        </button>
        <button 
          v-if="isEditingPreview"
          @click="saveAndRun"
          class="run-button"
          :disabled="isRunning || !isAuthenticated"
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
import { ref, watch, computed, onMounted } from 'vue';
import axios from 'axios';
import Prism from 'prismjs';
import 'prismjs/themes/prism.css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-kotlin';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-php';
import 'prismjs/components/prism-ruby';
import 'prismjs/components/prism-swift';
import 'prismjs/components/prism-scala';
import { useRouter } from 'vue-router';

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
});

const emit = defineEmits(['update:content']);
const router = useRouter();

const localContent = ref({ ...props.content, interpreter: props.content.interpreter || 'default' });
const showPreview = ref(false);
const executionResult = ref(null);
const executionError = ref(false);
const isRunning = ref(false);
const isAuthenticated = ref(false);
const isEditingPreview = ref(false);
const editingCode = ref('');
const currentTheme = ref('vs-dark');

onMounted(() => {
  checkAuthStatus();
  applyTheme();
  Prism.highlightAll();
});

const checkAuthStatus = () => {
  const token = localStorage.getItem('access_token');
  isAuthenticated.value = !!token;
};

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
  };
  return labels[localContent.value.language] || localContent.value.language.toUpperCase();
});

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
  };
  return labels[localContent.value.interpreter] || localContent.value.interpreter;
});

const canRunCode = computed(() => {
  const executableLanguages = ['javascript', 'python', 'java', 'kotlin', 'go', 'rust', 'cpp', 'csharp', 'php', 'ruby', 'swift', 'scala'];
  return executableLanguages.includes(localContent.value.language) && localContent.value.code;
});

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};

const togglePreview = () => {
  showPreview.value = !showPreview.value;
  if (showPreview.value) {
    setTimeout(() => Prism.highlightAll(), 0);
  }
};

const toggleEditPreview = () => {
  if (isEditingPreview.value) {
    savePreviewChanges();
  } else {
    editingCode.value = localContent.value.code;
    isEditingPreview.value = true;
  }
};

const savePreviewChanges = () => {
  localContent.value.code = editingCode.value;
  isEditingPreview.value = false;
  emitUpdate();
};

const saveAndRun = () => {
  savePreviewChanges();
  runCode();
};

const applyTheme = () => {
  document.documentElement.setAttribute('data-theme', currentTheme.value);
  Prism.highlightAll();
};

const handleKeydown = (event) => {
  if (event.key === 'Tab') {
    event.preventDefault();
    const textarea = event.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const value = textarea.value;

    textarea.value = value.substring(0, start) + '  ' + value.substring(end);
    textarea.selectionStart = textarea.selectionEnd = start + 2;

    if (!showPreview.value) {
      localContent.value.code = textarea.value;
    } else {
      editingCode.value = textarea.value;
    }
    emitUpdate();
  }
};

const runCode = async () => {
  if (!canRunCode.value || !isAuthenticated.value) {
    return;
  }

  isRunning.value = true;
  executionResult.value = null;
  executionError.value = false;

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication token missing');
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
    );

    const result = response.data;

    if (result.status === 'Accepted') {
      executionResult.value = result.stdout || 'Program executed without output.';
    } else {
      executionError.value = true;
      executionResult.value = result.stderr || result.compile_output || `Error: ${result.status}`;
    }
  } catch (error) {
    console.error('Code execution error:', error);
    executionError.value = true;

    if (error.response) {
      if (error.response.status === 401) {
        executionResult.value = 'Authentication error. Please log in again.';
        router.push('/login');
      } else if (error.response.status === 400) {
        executionResult.value = error.response.data.error || 'Invalid request. Check data.';
      } else if (error.response.status === 408) {
        executionResult.value = 'Timeout. Program took too long to execute.';
      } else {
        executionResult.value = 'Error executing code. Try again later.';
      }
    } else {
      executionResult.value = 'Failed to connect to server. Check connection.';
    }
  } finally {
    isRunning.value = false;
  }
};

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal, interpreter: newVal.interpreter || 'default' };
}, { deep: true });

watch(() => localContent.value.language, (newLang) => {
  const validInterpreters = getValidInterpreters(newLang);
  if (!validInterpreters.includes(localContent.value.interpreter)) {
    localContent.value.interpreter = 'default';
    emitUpdate();
  }
});

watch(currentTheme, () => {
  applyTheme();
});

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
  };
  return interpreterMap[language] || ['default'];
};
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

.vs-dark .language-selector,
.vs-dark .interpreter-selector,
.vs-dark .theme-selector {
  background: #2d2d2d;
  color: #e5e7eb;
  border-color: #4b4b4b;
}

.vs-high-contrast .language-selector,
.vs-high-contrast .interpreter-selector,
.vs-high-contrast .theme-selector {
  background: #1a1a1a;
  color: #ffffff;
  border-color: #ffffff;
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
  background: #1e293b;
  border-radius: 0.375rem;
  overflow-x: hidden;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  box-sizing: border-box;
  word-break: break-all;
}

.vs-light .code-preview {
  background: #f8fafc;
}

.vs-dark .code-preview {
  background: #1a1a1a;
}

.vs-high-contrast .code-preview {
  background: #000000;
}

:deep(.code-preview pre) {
  margin: 0;
  word-break: break-all;
}

:deep(.code-preview code) {
  white-space: pre-wrap;
  word-break: break-all;
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

/* Custom Prism.js styles for VS Code-like syntax highlighting */
:deep(.token.comment),
:deep(.token.prolog),
:deep(.token.doctype),
:deep(.token.cdata) {
  color: #6b7280;
}

:deep(.token.punctuation) {
  color: #9ca3af;
}

:deep(.token.property),
:deep(.token.tag),
:deep(.token.constant),
:deep(.token.symbol),
:deep(.token.deleted) {
  color: #f43f5e;
}

:deep(.token.boolean),
:deep(.token.number) {
  color: #60a5fa;
}

:deep(.token.selector),
:deep(.token.attr-name),
:deep(.token.string),
:deep(.token.char),
:deep(.token.builtin),
:deep(.token.inserted) {
  color: #34d399;
}

:deep(.token.operator),
:deep(.token.entity),
:deep(.token.url),
:deep(.token.variable) {
  color: #f59e0b;
}

:deep(.token.atrule),
:deep(.token.attr-value),
:deep(.token.function),
:deep(.token.class-name) {
  color: #facc15;
}

:deep(.token.keyword) {
  color: #3b82f6;
}

:deep(.token.regex),
:deep(.token.important) {
  color: #fb923c;
}

.vs-light :deep(.token.comment),
.vs-light :deep(.token.prolog),
.vs-light :deep(.token.doctype),
.vs-light :deep(.token.cdata) {
  color: #a3a3a3;
}

.vs-light :deep(.token.punctuation) {
  color: #4b4b4b;
}

.vs-light :deep(.token.property),
.vs-light :deep(.token.tag),
.vs-light :deep(.token.constant),
.vs-light :deep(.token.symbol),
.vs-light :deep(.token.deleted) {
  color: #e11d48;
}

.vs-light :deep(.token.boolean),
.vs-light :deep(.token.number) {
  color: #2563eb;
}

.vs-light :deep(.token.selector),
.vs-light :deep(.token.attr-name),
.vs-light :deep(.token.string),
.vs-light :deep(.token.char),
.vs-light :deep(.token.builtin),
.vs-light :deep(.token.inserted) {
  color: #059669;
}

.vs-light :deep(.token.operator),
.vs-light :deep(.token.entity),
.vs-light :deep(.token.url),
.vs-light :deep(.token.variable) {
  color: #b45309;
}

.vs-light :deep(.token.atrule),
.vs-light :deep(.token.attr-value),
.vs-light :deep(.token.function),
.vs-light :deep(.token.class-name) {
  color: #b91c1c;
}

.vs-light :deep(.token.keyword) {
  color: #1d4ed8;
}

.vs-light :deep(.token.regex),
.vs-light :deep(.token.important) {
  color: #c2410c;
}
</style>