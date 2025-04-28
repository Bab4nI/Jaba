```vue
<template>
  <div class="image-element" :class="{ 'read-only': readOnly }">
    <div v-if="!localContent.image && !readOnly" class="upload-area" @click="triggerFileInput">
      <span>Нажмите для загрузки изображения</span>
      <input
        type="file"
        ref="fileInput"
        accept="image/*"
        @change="handleFileSelect"
        style="display: none"
      />
    </div>
    <div v-if="localContent.image" class="image-preview-container">
      <img :src="imageUrl" class="image-preview" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

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
  border: 2px dashed #ccc;
  border-radius: 5px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: background 0.3s;
}

.upload-area:hover {
  background: #f5f5f5;
}

.image-preview-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.image-preview {
  max-width: 100%;
  max-height: 300px;
  display: block;
  margin: 0 auto;
  border-radius: 5px;
}

.read-only .image-preview {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.image-controls {
  display: flex;
  gap: 10px;
}

.remove-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
```