<template>
  <div class="video-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    <div v-if="readOnly && showScore" class="element-score-display" :class="{ 'visible': videoWatched }">
      <template v-if="userScore !== null">
        <span :class="{'score-success': userScore === localContent.max_score, 'score-fail': userScore < localContent.max_score}">
          {{ userScore }}/{{ localContent.max_score }}
        </span>
        <button v-if="!readOnly" @click="resetVideo" class="reset-score-btn" title="Сбросить баллы">×</button>
      </template>
      <template v-else>
        <span class="score-pending">{{ localContent.max_score }} баллов</span>
      </template>
    </div>
    
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
      <div class="video-controls">
        <button v-if="!readOnly" @click="removeVideo" class="remove-video-btn">Удалить видео</button>
      </div>
    </div>
    
    <!-- Mark as watched button in read-only mode -->
    <div v-if="readOnly && !videoWatched && localContent.video_url" class="video-submit">
      <button 
        @click="markVideoWatched" 
        class="submit-btn"
      >
        Отметить видео как просмотренное
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ 
      video_url: '',
      max_score: 1 
    })
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

const emit = defineEmits(['update:content', 'answer-submitted']);
const themeStore = useThemeStore();

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
  video_url: getContentData(props.content).video_url || props.content.video_url || ''
});
const videoUrl = ref('');
const videoWatched = ref(false);
const userScore = ref(null);
const videoFrame = ref(null);
const watchProgress = ref(0);
const isWatched = ref(false);
const progressCheckInterval = ref(null);

// Generate a unique ID for this component instance
const uniqueId = ref(`video-${Date.now()}-${Math.floor(Math.random() * 10000)}`);

const embedCode = computed(() => {
  if (!localContent.value.video_url) return '';
  if (localContent.value.video_url.includes('youtube.com') || localContent.value.video_url.includes('youtu.be')) {
    const videoId = extractYouTubeId(localContent.value.video_url);
    return `<iframe width="100%" height="100%" src="https://www.youtube.com/embed/${videoId}?enablejsapi=1&origin=${window.location.origin}" frameborder="0" allowfullscreen></iframe>`;
  }
  if (localContent.value.video_url.includes('vimeo.com')) {
    const videoId = localContent.value.video_url.split('/').pop();
    return `<iframe src="https://player.vimeo.com/video/${videoId}?api=1&player_id=vimeo_player" width="100%" height="100%" frameborder="0" allowfullscreen></iframe>`;
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

// Initialize from localStorage if there's saved progress
onMounted(() => {
  if (props.readOnly && props.content.id) {
    const savedData = localStorage.getItem(`video_${props.content.id}`);
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        videoWatched.value = data.videoWatched;
        userScore.value = data.userScore;
        
        console.log(`Loaded saved state for video ${props.content.id}:`, { 
          videoWatched: videoWatched.value, 
          userScore: userScore.value 
        });
        
        // If we have a saved score, emit it to update the parent
        if (userScore.value !== null) {
          emit('answer-submitted', {
            contentId: props.content.id,
            score: userScore.value,
            maxScore: localContent.value.max_score
          });
        }
      } catch (e) {
        console.error('Error loading video state:', e);
      }
    }
  }
});

watch(() => props.content, (newContent) => {
  localContent.value = {
    ...newContent,
    video_url: getContentData(newContent).video_url || newContent.video_url || ''
  };
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

const markVideoWatched = () => {
  videoWatched.value = true;
  userScore.value = localContent.value.max_score;
  
  // Emit event for parent components
  emit('answer-submitted', {
    contentId: props.content.id,
    score: userScore.value,
    maxScore: localContent.value.max_score
  });
};

// Reset video watched state
const resetVideo = () => {
  videoWatched.value = false;
  userScore.value = null;
  watchProgress.value = 0;
  isWatched.value = false;
  
  // Emit event to reset score in parent component
  emit('answer-submitted', {
    contentId: props.content.id,
    score: 0,
    maxScore: localContent.value.max_score
  });
  
  console.log('Reset video state for:', props.content.id);
};

const emitUpdate = () => {
  emit('update:content', {
    ...props.content,
    content_data: {
      ...getContentData(props.content),
      video_url: localContent.value.video_url
    }
  });
};

const onVideoLoad = () => {
  if (!props.readOnly || !videoFrame.value) return;
  
  // Initialize video progress tracking
  startProgressTracking();
  
  // Load saved progress
  loadSavedProgress();
};

const startProgressTracking = () => {
  // Clear any existing interval
  if (progressCheckInterval.value) {
    clearInterval(progressCheckInterval.value);
  }
  
  // Check progress every second
  progressCheckInterval.value = setInterval(() => {
    if (!videoFrame.value) return;
    
    try {
      const player = videoFrame.value.contentWindow;
      if (player) {
        if (localContent.value.video_url.includes('youtube.com') || localContent.value.video_url.includes('youtu.be')) {
          // YouTube API
          player.postMessage('{"event":"listening"}', '*');
          player.postMessage('{"method":"getCurrentTime"}', '*');
        } else if (localContent.value.video_url.includes('vimeo.com')) {
          // Vimeo API
          player.postMessage('{"method":"getCurrentTime"}', '*');
        }
      }
    } catch (error) {
      console.error('Error tracking video progress:', error);
    }
  }, 1000);
};

const handleVideoProgress = (event) => {
  if (!event.data) return;
  
  try {
    const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
    
    if (data.event === 'onReady' || data.event === 'onStateChange') {
      // Video player is ready
      if (videoFrame.value) {
        videoFrame.value.contentWindow.postMessage('{"method":"getDuration"}', '*');
      }
    }
    else if (data.event === 'onVideoProgress') {
      // Update progress
      const progress = (data.data.currentTime / data.data.duration) * 100;
      watchProgress.value = Math.min(100, Math.max(0, progress));
      
      // Check if video is watched enough (80% or more)
      if (watchProgress.value >= 80 && !isWatched.value) {
        isWatched.value = true;
        markVideoWatched(); // Automatically mark as watched
      }
      
      // Save progress
      saveProgress();
    }
  } catch (error) {
    console.error('Error handling video progress:', error);
  }
};

const saveProgress = () => {
  // No need to save to localStorage, as we're not using localStorage anymore
};

const loadSavedProgress = () => {
  // No need to load from localStorage, as we're not using localStorage anymore
};

// Add event listener for video progress
onMounted(() => {
  window.addEventListener('message', handleVideoProgress);
});

onUnmounted(() => {
  if (progressCheckInterval.value) {
    clearInterval(progressCheckInterval.value);
  }
  window.removeEventListener('message', handleVideoProgress);
});
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
  align-items: center;
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

.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.remove-video-btn {
  background: var(--error-color);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.remove-video-btn:hover {
  background: var(--hover-delete);
}

.score-display {
  min-width: 80px;
  text-align: center;
  padding: 8px 12px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.05);
  font-weight: bold;
  color: var(--text-color, #24222f);
}

.score-success {
  color: #2e8b33;
  font-weight: 700;
}

.score-pending {
  color: var(--secondary-text, #575667);
}

.video-submit {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.submit-btn {
  background: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #43a047;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* Dark theme specific adjustments */
:global(.dark-theme) .read-only .video-embed {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

:global(.dark-theme) .score-display {
  background: rgba(255, 255, 255, 0.08);
}

:global(.dark-theme) .score-success {
  color: #6bdb70;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .video-url-input {
    font-size: 14px;
  }

  .add-video-btn,
  .remove-video-btn,
  .submit-btn {
    font-size: 14px;
    padding: 6px 12px;
  }

  .video-element {
    padding: 0 10px;
  }
  
  .video-controls {
    flex-direction: column;
    align-items: flex-start;
  }
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:global(.dark-theme) .element-score-display {
  background: rgba(255, 255, 255, 0.08);
  color: #e5e7eb;
}

:global(.dark-theme) .score-success {
  color: #6bdb70;
}

:global(.dark-theme) .score-fail {
  color: #ff6b6b;
}

.reset-score-btn {
  background: var(--error-color, #da1f38);
  color: white;
  border: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
  flex-shrink: 0;
  opacity: 0.7;
}

.reset-score-btn:hover {
  background: var(--hover-delete, #c62828);
  transform: scale(1.1);
  opacity: 1;
}

:global(.dark-theme) .reset-score-btn {
  background: #ff4d4d;
}

:global(.dark-theme) .reset-score-btn:hover {
  background: #ff3333;
}
</style>