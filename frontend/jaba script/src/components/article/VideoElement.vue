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
import { useThemeStore } from '@/stores/themeStore';

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
const themeStore = useThemeStore();

const localContent = ref({ ...props.content });
const videoUrl = ref('');

const embedCode = computed(() => {
  if (!localContent.value.video_url) return '';
  if (localContent.value.video_url.includes('youtube.com') || localContent.value.video_url.includes('youtu.be')) {
    const videoId = extractYouTubeId(localContent.value.video_url);
    return `<iframe width="100%" height="100%" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>`;
  }
  if (localContent.value.video_url.includes('vimeo.com')) {
    const videoId = localContent.value.video_url.split('/').pop();
    return `<iframe src="https://player.vimeo.com/video/${videoId}" width="100%" height="100%" frameborder="0" allowfullscreen></iframe>`;
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
.video-element {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.video-input-container {
  display: flex;
  gap: 10px;
  width: 100%;
  flex-wrap: wrap;
}

.video-url-input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 16px;
  min-width: 200px;
  background-color: var(--form-background);
  color: var(--text-color);
  transition: border-color 0.3s ease, background-color 0.3s ease, color 0.3s ease;
}

.video-url-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.add-video-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  white-space: nowrap;
  transition: background-color 0.3s ease;
}

.add-video-btn:hover:not(:disabled) {
  background: var(--hover-accent);
}

.add-video-btn:disabled {
  background: var(--secondary-text);
  opacity: 0.5;
  cursor: not-allowed;
}

.video-preview-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.video-embed {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: 8px;
  background-color: var(--background-color);
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
}

.video-embed iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.read-only .video-embed {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.remove-video-btn {
  background: var(--error-color);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-start;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.remove-video-btn:hover {
  background: var(--hover-delete);
}

/* Dark theme specific adjustments */
:root.dark-theme .read-only .video-embed {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .video-url-input {
    font-size: 14px;
  }

  .add-video-btn,
  .remove-video-btn {
    font-size: 14px;
    padding: 6px 12px;
  }

  .video-element {
    padding: 0 10px;
  }
}
</style>
```