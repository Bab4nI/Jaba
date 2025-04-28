<template>
  <div class="file-element" :class="{ 'read-only': readOnly }">
    <div v-if="!localContent.file && !readOnly" class="file-upload-area" @click="triggerFileInput">
      <span>Нажмите для загрузки файла</span>
      <input
        type="file"
        ref="fileInput"
        @change="handleFileSelect"
        style="display: none"
      />
    </div>
    <div v-if="localContent.file" class="file-preview-container">
      <div class="file-info">
        <span class="file-icon">📄</span>
        <a
          :href="fileUrl"
          :download="displayFileName"
          class="file-name"
          target="_blank"
          @click.prevent="downloadFile"
        >
          {{ displayFileName }}
        </a>
        <span v-if="!readOnly" class="file-size">{{ fileSize }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ file: null, filename: null })
  },
  lessonId: {
    type: Number,
    required: true
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:content']);

const localContent = ref({ ...props.content });
const fileInput = ref(null);

const displayFileName = computed(() => {
  if (!localContent.value.file) return '';
  if (typeof localContent.value.file === 'string') {
    const fileName = localContent.value.filename || localContent.value.file.split('/').pop();
    try {
      return decodeURIComponent(fileName);
    } catch (e) {
      return fileName;
    }
  }
  return localContent.value.file.name;
});

const fileUrl = computed(() => {
  if (!localContent.value.file || typeof localContent.value.file !== 'string') return '#';
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return localContent.value.file.startsWith('http') ? localContent.value.file : `${baseUrl}${localContent.value.file}`;
});

const fileSize = computed(() => {
  if (!localContent.value.file || typeof localContent.value.file === 'string') return '';
  const size = localContent.value.file.size || 0;
  if (size < 1024) return `${size} Б`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} КБ`;
  return `${(size / (1024 * 1024)).toFixed(1)} МБ`;
});

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal };
}, { deep: true });

const triggerFileInput = () => {
  if (props.readOnly) return;
  fileInput.value.click();
};

const handleFileSelect = (event) => {
  if (props.readOnly) return;
  const file = event.target.files[0];
  if (!file) return;
  localContent.value.file = file;
  localContent.value.filename = file.name;
  emitUpdate();
  fileInput.value.value = '';
};

const removeFile = () => {
  if (props.readOnly) return;
  localContent.value.file = null;
  localContent.value.filename = null;
  emitUpdate();
};

const downloadFile = (event) => {
  if (fileUrl.value !== '#') {
    event.preventDefault();
    const link = document.createElement('a');
    link.href = fileUrl.value;
    link.download = displayFileName.value;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};
</script>

<style scoped>
.file-element {
  font-family: inherit;
}

.file-upload-area {
  border: none;
  background: #f8f9fa;
  border-radius: 5px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: background 0.3s;
  color: #2c3e50;
}

.file-upload-area:hover {
  background: #e9ecef;
}

.file-preview-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 5px;
}

.read-only .file-info {
  background: #ffffff;
  padding: 15px;
  border-radius: 8px;
  /* Убрана тень */
}

.file-icon {
  font-size: 24px;
}

.file-name {
  font-weight: normal; /* Уменьшил жирность */
  flex-grow: 1;
  color: #2c3e50;
  text-decoration: none;
  text-shadow: none; /* Убрана тень у текста */
}

.file-name:hover {
  text-decoration: underline;
}

.file-size {
  color: #666;
  font-size: 0.9em;
}

.file-controls {
  display: flex;
  gap: 10px;
}

.remove-file-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: normal;
  text-shadow: none; /* Убрана тень у текста */
}
</style>