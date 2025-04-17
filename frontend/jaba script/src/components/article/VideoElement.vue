```vue
<template>
  <div class="video-element" :class="{ 'read-only': readOnly }">
    <div v-if="!localContent.video_url && !readOnly" class="video-input-container">
      <input
        v-model="videoUrl"
        placeholder="Вставьте ссылку на YouTube или Vimeo"
        class="video-url-input"
      />
      <button @click="addVideo" class="add-video-btn" :disabled="!isValidVideoUrl">Добавить</button>
    </div>
    <div v-if="localContent.video_url" class="video-preview-container">
      <div class="video-embed" v-html="embedCode"></div>
      <button v-if="!readOnly" @click="removeVideo" class="remove-video-btn">Удалить видео</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ video_url: '' })
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:content']);

const localContent = ref({ ...props.content });
const videoUrl = ref('');

const embedCode = computed(() => {
  if (!localContent.value.video_url) return '';
  if (localContent.value.video_url.includes('youtube.com') || localContent.value.video_url.includes('youtu.be')) {
    const videoId = extractYouTubeId(localContent.value.video_url);
    return `<iframe width="100%" height="315" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>`;
  }
  if (localContent.value.video_url.includes('vimeo.com')) {
    const videoId = localContent.value.video_url.split('/').pop();
    return `<iframe src="https://player.vimeo.com/video/${videoId}" width="100%" height="360" frameborder="0" allowfullscreen></iframe>`;
  }
  return '<p>Неподдерживаемый видео-сервис</p>';
});

const isValidVideoUrl = computed(() => {
  if (!videoUrl.value) return false;
  return (
    videoUrl.value.includes('youtube.com') ||
    videoUrl.value.includes('youtu.be') ||
    videoUrl.value.includes('vimeo.com')
  );
});

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal };
}, { deep: true });

const extractYouTubeId = (url) => {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  return match && match[2].length === 11 ? match[2] : null;
};

const addVideo = () => {
  if (props.readOnly || !isValidVideoUrl.value) return;
  localContent.value.video_url = videoUrl.value;
  emitUpdate();
  videoUrl.value = '';
};

const removeVideo = () => {
  if (props.readOnly) return;
  localContent.value.video_url = '';
  emitUpdate();
};

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};
</script>

<style scoped>
.video-input-container {
  display: flex;
  gap: 10px;
}

.video-url-input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-video-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.add-video-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.video-preview-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.video-embed {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
  overflow: hidden;
}

.video-embed iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.read-only .video-embed {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.remove-video-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-start;
}
</style>
```