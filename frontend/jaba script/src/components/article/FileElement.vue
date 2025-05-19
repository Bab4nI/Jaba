<template>
  <div class="file-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    
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
        <span class="file-name">{{ displayFileName }}</span>
        <span v-if="!readOnly" class="file-size">{{ fileSize }}</span>
        <button class="download-btn" @click="downloadFile" title="Скачать файл">
          <img src="@/assets/images/download.png" alt="Скачать файл" class="download-icon">
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ 
      file: null, 
      filename: null,
      max_score: 1 
    })
  },
  lessonId: {
    type: Number,
    required: true
  },
  readOnly: {
    type: Boolean,
    default: false
  },
  showScore: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:content']);
const themeStore = useThemeStore();

const localContent = ref({ 
  file: null, 
  filename: null,
  max_score: 1,
  ...props.content 
});
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
  localContent.value = { 
    ...newVal,
    max_score: newVal.max_score || 1
  };
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

const downloadFile = () => {
  if (fileUrl.value !== '#') {
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
  border: 1px solid var(--border-color);
  background: var(--form-background);
  border-radius: 5px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;
  color: var(--text-color);
}

.file-upload-area:hover {
  background: var(--hover-background);
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
  background: var(--form-background);
  border-radius: 5px;
  border: 1px solid var(--border-color);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.read-only .file-info {
  background: transparent;
  padding: 15px;
  border-radius: 8px;
}

.file-icon {
  font-size: 24px;
}

.file-name {
  font-weight: normal;
  flex-grow: 1;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.file-size {
  color: var(--secondary-text);
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.download-btn {
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  line-height: 1;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.download-btn:hover {
  background-color: var(--hover-background);
}

.download-icon {
  width: 20px;
  height: 20px;
  transition: opacity 0.2s ease, filter 0.3s ease;
}

/* Apply a filter for the download icon in dark mode */
:root.dark-theme .download-icon {
  filter: invert(1);
}

.download-btn:hover .download-icon {
  opacity: 0.7;
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
}

.score-pending {
  color: var(--secondary-text, #575667);
}

:global(.dark-theme) .element-score-display {
  background: rgba(255, 255, 255, 0.08);
}
</style>