```vue
<template>
  <div class="image-element" :class="{ 'read-only': readOnly }">
    <!-- Upload area when no image -->
    <div v-if="!localContent.image && !readOnly" class="upload-area" @click="triggerFileInput">
      <span>Нажмите для загрузки изображения</span>
    </div>
    <!-- Preview with replace/remove controls -->
    <div v-else-if="localContent.image" class="image-preview-container">
      <img :src="imageUrl" class="image-preview" />
      <div v-if="!readOnly" class="image-controls">
        <button class="replace-btn" @click="triggerFileInput" title="Заменить изображение">Заменить</button>
        <button class="remove-btn" @click="removeImage" title="Удалить изображение">Удалить</button>
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
import { ref, computed, watch } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ image: null })
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
const themeStore = useThemeStore();

const localContent = ref({ ...props.content });
const fileInput = ref(null);

const imageUrl = computed(() => {
  if (!localContent.value.image) return '';
  if (typeof localContent.value.image === 'string') return localContent.value.image;
  return URL.createObjectURL(localContent.value.image);
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
  localContent.value.image = file;
  emitUpdate();
  fileInput.value.value = '';
};

const removeImage = () => {
  if (props.readOnly) return;
  localContent.value.image = null;
  emitUpdate();
};

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};
</script>

<style scoped>
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
</style>
```