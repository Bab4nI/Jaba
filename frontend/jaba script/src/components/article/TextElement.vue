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
      <select @change="insertHeader($event.target.value)" title="Заголовок">
        <option value="">Заголовок</option>
        <option value="# ">H1</option>
        <option value="## ">H2</option>
        <option value="### ">H3</option>
        <option value="#### ">H4</option>
        <option value="##### ">H5</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import { marked } from 'marked';

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

const insertHeader = (prefix) => {
  if (!prefix || props.readOnly) return;
  const textarea = document.querySelector('.text-element-input');
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = localContent.value.text.substring(start, end);

  if (start === end) {
    localContent.value.text =
      localContent.value.text.substring(0, start) +
      prefix +
      localContent.value.text.substring(end);
    
    emitUpdate();

    nextTick(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        start + prefix.length
      );
      textarea.closest('.text-element').querySelector('select').value = '';
    });
  } else {
    localContent.value.text =
      localContent.value.text.substring(0, start) +
      prefix +
      selectedText +
      localContent.value.text.substring(end);

    emitUpdate();

    nextTick(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        end + prefix.length
      );
      textarea.closest('.text-element').querySelector('select').value = '';
    });
  }
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
  border: none;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  background: #f8f9fa;
  outline: none;
}

.text-content {
  padding: 10px;
  color: #2c3e50;
  line-height: 1.6;
  border: none;
}

.read-only .text-content {
  background: #ffffff;
  border-radius: 8px;
  /* Убрана тень box-shadow */
}

.formatting-toolbar {
  display: flex;
  gap: 5px;
  align-items: center;
}

.formatting-toolbar button, 
.formatting-toolbar select {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 3px 8px;
  cursor: pointer;
  box-shadow: none; /* Убрана тень у кнопок */
}

.formatting-toolbar button:hover, 
.formatting-toolbar select:hover {
  background: #e0e0e0;
}

.text-content h1 {
  text-align: center;
  text-shadow: none; /* Убрана тень у текста */
}
.text-content h2, 
.text-content h3, 
.text-content h4, 
.text-content h5 {
  text-align: left;
  margin: 1em 0 0.5em 0;
  text-shadow: none; /* Убрана тень у текста */
}
</style>