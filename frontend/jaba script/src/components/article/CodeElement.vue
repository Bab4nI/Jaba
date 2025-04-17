```vue
<template>
  <div class="code-element">
    <select
      v-if="!readOnly"
      v-model="localContent.language"
      @change="emitUpdate"
      class="language-selector"
    >
      <option value="javascript">JavaScript</option>
      <option value="html">HTML</option>
      <option value="css">CSS</option>
      <option value="python">Python</option>
      <option value="java">Java</option>
      <option value="php">PHP</option>
      <option value="csharp">C#</option>
      <option value="cpp">C++</option>
      <option value="ruby">Ruby</option>
      <option value="bash">Bash</option>
      <option value="sql">SQL</option>
      <option value="json">JSON</option>
      <option value="markdown">Markdown</option>
    </select>
    <span v-else class="language-label">{{ localContent.language.toUpperCase() }}</span>
    <textarea
      v-if="!readOnly"
      v-model="localContent.code"
      @input="emitUpdate"
      placeholder="Введите ваш код..."
      class="code-input"
    ></textarea>
    <div v-if="localContent.code" class="code-preview">
      <pre><code :class="'language-' + localContent.language">{{ localContent.code }}</code></pre>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ language: 'javascript', code: '' })
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:content']);

const localContent = ref({ ...props.content });

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal };
}, { deep: true });

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};
</script>

<style scoped>
.code-element {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.language-selector {
  align-self: flex-start;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
}

.language-label {
  align-self: flex-start;
  padding: 6px 10px;
  background: #e5e7eb;
  border-radius: 4px;
  font-size: 14px;
  color: #374151;
}

.code-input {
  width: 100%;
  min-height: 150px;
  padding: 10px;
  font-family: 'Courier New', monospace;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  background: #f8f8f8;
}

.code-preview {
  margin-top: 10px;
  padding: 10px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(.code-preview pre) {
  margin: 0;
}

:deep(.code-preview code) {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
}

/* Preview mode styles */
.code-element.read-only .code-preview {
  background: #ffffff;
  border: none;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
```