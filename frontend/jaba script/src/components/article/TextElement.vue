```vue
<template>
  <div class="text-element" :class="{ 'read-only': readOnly }">
    <textarea
      v-if="!readOnly"
      v-model="localContent.text"
      class="text-element-input"
      placeholder="Введите текст..."
      @input="emitUpdate"
    ></textarea>
    <div v-else class="text-content" v-html="renderedText"></div>
    <div v-if="!readOnly" class="formatting-toolbar">
      <button @click="insertMarkdown('**', '**')" title="Жирный">B</button>
      <button @click="insertMarkdown('_', '_')" title="Курсив">I</button>
      <button @click="insertMarkdown('[', '](url)')" title="Ссылка">🔗</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import {marked} from 'marked';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ text: '' })
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:content']);

const localContent = ref({ ...props.content });

const renderedText = computed(() => {
  return marked(localContent.value.text || '');
});

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal };
}, { deep: true });

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};

const insertMarkdown = (prefix, suffix) => {
  if (props.readOnly) return;
  const textarea = document.querySelector('.text-element-input');
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = localContent.value.text.substring(start, end);

  localContent.value.text =
    localContent.value.text.substring(0, start) +
    prefix +
    selectedText +
    suffix +
    localContent.value.text.substring(end);

  emitUpdate();

  nextTick(() => {
    textarea.focus();
    textarea.setSelectionRange(
      start + prefix.length,
      end + prefix.length
    );
  });
};
</script>

<style scoped>
.text-element {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.text-element-input {
  width: 100%;
  min-height: 150px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.text-content {
  padding: 10px;
  color: #2c3e50;
  line-height: 1.6;
}

.read-only .text-content {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.formatting-toolbar {
  display: flex;
  gap: 5px;
}

.formatting-toolbar button {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 3px 8px;
  cursor: pointer;
}

.formatting-toolbar button:hover {
  background: #e0e0e0;
}
</style>
```