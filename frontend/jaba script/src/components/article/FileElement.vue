<template>
  <div class="file-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    
    <div v-if="!localContent.file && !readOnly" class="file-upload-area" @click="triggerFileInput">
      <span>Нажмите для загрузки файла</span>
    </div>
    <div v-if="localContent.file" class="file-preview-container">
      <div class="file-info">
        <span class="file-icon">📄</span>
        <span class="file-name">{{ displayFileName }}</span>
        <span v-if="!readOnly" class="file-size">{{ fileSize }}</span>
        <button class="download-btn" @click="downloadFile" title="Скачать файл">
          <img src="@/assets/images/download.png" alt="Скачать файл" class="download-icon">
        </button>
        <div v-if="!readOnly" class="file-controls">
          <button class="replace-btn" @click="triggerFileInput" title="Заменить файл">Заменить</button>
        </div>
      </div>
    </div>
    <input
      type="file"
      ref="fileInput"
      @change="handleFileSelect"
      style="display: none"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import api from '@/api';

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
  // Helper function to extract file info from nested content_data
  const extractFileInfo = (content) => {
    if (!content) return '';
    
    // First check direct file and filename
    if (content.file) {
      if (typeof content.file === 'string') {
        const fileName = content.filename || content.file.split('/').pop();
        try {
          return decodeURIComponent(fileName);
        } catch (e) {
          return fileName;
        }
      }
      return content.file.name;
    }
    
    // Then check nested content_data
    if (content.content_data) {
      // If content_data is an object with file
      if (content.content_data.file) {
        if (typeof content.content_data.file === 'string') {
          const fileName = content.content_data.filename || content.content_data.file.split('/').pop();
          try {
            return decodeURIComponent(fileName);
          } catch (e) {
            return fileName;
          }
        }
        return content.content_data.file.name;
      }
      
      // If content_data has nested content_data
      if (content.content_data.content_data) {
        return extractFileInfo(content.content_data.content_data);
      }
    }
    
    return '';
  };

  return extractFileInfo(localContent.value);
});

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const fileUrl = computed(() => {
  // Helper function to extract file path from nested content_data
  const extractFilePath = (content) => {
    if (!content) return '#';
    
    // First check direct file
    if (content.file) {
      if (typeof content.file === 'string') {
        return content.file;
      }
      return '#';
    }
    
    // Then check nested content_data
    if (content.content_data) {
      // If content_data is an object with file
      if (content.content_data.file) {
        if (typeof content.content_data.file === 'string') {
          return content.content_data.file;
        }
        return '#';
      }
      
      // If content_data has nested content_data
      if (content.content_data.content_data) {
        return extractFilePath(content.content_data.content_data);
      }
    }
    
    return '#';
  };

  const path = extractFilePath(localContent.value);
  if (path === '#') return path;
  
  if (path.startsWith('http') || path.startsWith('blob:')) {
    return path;
  }
  if (path.startsWith('/media/')) {
    return `${apiBaseUrl}${path}`;
  }
  return `${apiBaseUrl}/media/${path}`;
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

const handleFileSelect = async (event) => {
  if (props.readOnly) return;
  const file = event.target.files[0];
  if (!file) return;
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload-media/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    if (response.data.success && response.data.file_path) {
      localContent.value.file = response.data.file_path;
      localContent.value.filename = file.name;
      emitUpdate();
    } else {
      throw new Error('Failed to upload file');
    }
  } catch (error) {
    console.error('Error uploading file:', error);
    // Можно добавить отображение ошибки пользователю
  }
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

const removeFile = () => {
  if (props.readOnly) return;
  localContent.value.file = null;
  localContent.value.filename = null;
  emitUpdate();
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

.file-controls {
  display: flex;
  gap: 8px;
  margin-left: 12px;
}
.replace-btn {
  background: var(--accent-color, #a094b8);
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.replace-btn:hover {
  background: #8275a0;
}
.remove-btn {
  background: var(--error-color, #ef4444);
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.remove-btn:hover {
  background: var(--hover-delete, #dc2626);
}
</style>