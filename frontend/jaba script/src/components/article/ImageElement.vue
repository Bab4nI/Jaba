```vue
<template>
  <div class="image-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    
    <!-- Upload area when no image -->
    <div v-if="!localContent.image_path && !readOnly" class="upload-area" @click="triggerFileInput">
      <span>Нажмите для загрузки изображения</span>
    </div>
    <!-- Preview with replace/remove controls -->
    <div v-else-if="localContent.image_path" class="image-preview-container">
      <img :src="imageUrl" class="image-preview" />
      <div v-if="!readOnly" class="image-controls">
        <button class="replace-btn" @click="triggerFileInput" title="Заменить изображение">Заменить</button>
      </div>
    </div>
    <!-- Always-available hidden file input -->
    <input
      type="file"
      ref="fileInput"
      accept="image/*"
      @change="handleFileSelect"
      style="display: none"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import api from '@/api';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ 
      image_path: '',
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
const apiBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const getContentData = (content) => {
  if (typeof content.content_data === 'string') {
    try {
      return JSON.parse(content.content_data);
    } catch {
      return {};
    }
  }
  return content.content_data || {};
};

const localContent = ref({
  ...props.content,
  image_path: getContentData(props.content).image_path || props.content.image_path || ''
});
const fileInput = ref(null);

const imageUrl = computed(() => {
  const path = localContent.value.image_path;
  if (!path) return null;
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  if (path.startsWith('/media/')) {
    return `${apiBaseUrl}${path}`;
  }
  // Если путь относительный, добавляем /media/
  return `${apiBaseUrl}/media/${path.replace(/^\/+/, '')}`;
});

watch(() => props.content, (newContent) => {
  localContent.value = {
    ...newContent,
    image_path: getContentData(newContent).image_path || newContent.image_path || ''
  };
}, { deep: true });

onMounted(() => {
  localContent.value.image_path = getContentData(props.content).image_path || props.content.image_path || '';
});

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
    formData.append('image', file);

    const response = await api.post('/upload-media/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.data.success && response.data.image_path) {
      localContent.value.image_path = response.data.image_path;
      emitUpdate();
    } else {
      throw new Error('Failed to upload image');
    }
  } catch (error) {
    console.error('Error uploading image:', error);
    // You might want to show an error message to the user here
  }

  fileInput.value.value = '';
};

const removeImage = () => {
  if (props.readOnly) return;
  localContent.value.image_path = '';
  emitUpdate();
};

const emitUpdate = () => {
  emit('update:content', {
    ...props.content,
    content_data: {
      ...getContentData(props.content),
      image_path: localContent.value.image_path
    }
  });
};
</script>

<style scoped>
.file-element {
  font-family: inherit;
}

.image-element {
  font-family: inherit;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 5px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
  color: var(--text-color);
  background: var(--form-background);
}

.upload-area:hover {
  background: var(--hover-background);
}

.image-preview-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.image-preview {
  width: auto;           /* don't force full width */
  max-width: 80%;        /* scale to 80% of container width */
  height: auto;          /* maintain aspect ratio */
  max-height: 80vh;      /* scale to 80% of viewport height for tall images */
  object-fit: contain;   /* ensure image fits within bounds */
  display: block;
  margin: 0 auto;
  border-radius: 5px;
  transition: border-radius 0.3s ease, box-shadow 0.3s ease;
}

.image-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.replace-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.replace-btn:hover {
  background: var(--hover-accent);
}

.remove-btn {
  background: var(--error-color);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.remove-btn:hover {
  background: var(--hover-delete);
}

.read-only .image-preview {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Additional dark mode specific styling */
:root.dark-theme .read-only .image-preview {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
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
```