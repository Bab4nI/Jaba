<template>
  <div class="content-block" :class="{ 'read-only': readOnly }" ref="blockRef">
    <div v-if="!readOnly && !props.isTimeExpired" class="block-toolbar">
      <div class="block-controls">
        <button @click="moveUp" :disabled="isFirst || props.isTimeExpired" title="Переместить вверх">
          <span class="icon-up">↑</span>
        </button>
        <button @click="moveDown" :disabled="isLast || props.isTimeExpired" title="Переместить вниз">
          <span class="icon-down">↓</span>
        </button>
      </div>
      <div class="block-type">
        <span>{{ blockType }}</span>
      </div>
      <div v-if="!readOnly && !isScoreDisabled" class="block-score">
        <label for="block-max-score">Баллы:</label>
        <input 
          id="block-max-score"
          v-model.number="localContent.max_score" 
          type="number" 
          min="0" 
          max="10"
          class="score-input"
          @input="updateScore" 
          :disabled="props.isTimeExpired"
        />
      </div>
      <button @click="removeBlock" class="remove-btn" title="Удалить блок" :disabled="props.isTimeExpired">
        <span class="icon-remove">×</span>
      </button>
    </div>
    <div class="block-content">
      <component
        :is="contentComponent"
        :content="content"
        :read-only="readOnly || props.isTimeExpired"
        :show-score="true"
        :allow-preview-edit="props.allowPreviewEdit"
        :is-time-expired="props.isTimeExpired"
        :reset-key="props.resetKey"
        @update:content="onContentUpdate"
        @answer-submitted="handleAnswerSubmitted"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, nextTick, onUnmounted } from 'vue';
import TextElement from './TextElement.vue';
import ImageElement from './ImageElement.vue';
import VideoElement from './VideoElement.vue';
import CodeElement from './CodeElement.vue';
import QuizElement from './QuizElement.vue';
import TableElement from './TableElement.vue';
import FileElement from './FileElement.vue';
import FillInElement from './FillInElement.vue';

const props = defineProps({
  content: {
    type: Object,
    required: true
  },
  readOnly: {
    type: Boolean,
    default: false
  },
  isFirst: {
    type: Boolean,
    default: false
  },
  isLast: {
    type: Boolean,
    default: false
  },
  allowPreviewEdit: {
    type: Boolean,
    default: false
  },
  isTimeExpired: {
    type: Boolean,
    default: false
  },
  resetKey: {
    type: Number,
    default: 0
  }
});

const blockRef = ref(null);

const emit = defineEmits(['update:content', 'move-up', 'move-down', 'remove', 'answer-submitted']);

const localContent = ref({
  ...props.content,
  content_data: props.content.content_data || {},
  max_score: props.content.max_score || 0 // Set default score to 1 if not provided
});

watch(() => props.content, (newContent) => {
  localContent.value = {
    ...newContent,
    content_data: newContent.content_data || {},
    max_score: newContent.max_score || 0 // Ensure max_score is always set
  };
}, { deep: true });

const contentComponents = {
  text: TextElement,
  image: ImageElement,
  video: VideoElement,
  code: CodeElement,
  quiz: QuizElement,
  table: TableElement,
  file: FileElement,
  fillin: FillInElement
};

const blockType = computed(() => {
  const types = {
    text: 'Текст',
    image: 'Изображение',
    video: 'Видео',
    code: 'Код',
    quiz: 'Тест',
    table: 'Таблица',
    file: 'Файл',
    fillin: 'Пропущенное слово'
  };
  return types[props.content.type] || props.content.type;
});

const contentComponent = computed(() => {
  return contentComponents[props.content.type] || TextElement;
});

const isScoreDisabled = computed(() => {
  const disabledTypes = ['text', 'image', 'table', 'file'];
  return disabledTypes.includes(props.content.type);
});

const onContentUpdate = (updatedContent) => {
  localContent.value = {
    ...localContent.value,
    ...updatedContent,
    content_data: {
      ...localContent.value.content_data,
      ...updatedContent.content_data
    }
  };

  // Special handling for fillin type
  if (props.content.type === 'fillin') {
    localContent.value.text = updatedContent.text || localContent.value.text;
    localContent.value.answers = updatedContent.answers || localContent.value.answers;
  }

  emit('update:content', localContent.value);
};

const handleAnswerSubmitted = (data) => {
  // Make sure we have the content ID and pass it to the parent
  const contentId = props.content.id;
  
  // Log the submission for debugging
  console.log('ContentBlock received answer submission:', {
    contentId,
    originalData: data
  });
  
  // If data is an object with score and userAnswer
  if (typeof data === 'object' && data !== null) {
    emit('answer-submitted', {
      contentId: contentId,
      score: data.score || 0,
      userAnswer: data.userAnswer || data.answer || data
    });
  } else {
    // If data is just a score value, pass it with empty userAnswer
    emit('answer-submitted', {
      contentId: contentId,
      score: data || 0,
      userAnswer: {}
    });
  }
};

const moveUp = () => {
  emit('move-up');
};

const moveDown = () => {
  emit('move-down');
};

const removeBlock = () => {
  if (props.isTimeExpired) return;
  emit('remove');
};

const updateScore = () => {
  // Ensure score is at least 1 for non-disabled types
  if (!isScoreDisabled.value && localContent.value.max_score < 0) {
    localContent.value.max_score = 0;
  }
  // Set score to 0 for disabled types
  if (isScoreDisabled.value) {
    localContent.value.max_score = 0;
  }
  // Ensure score is an integer
  localContent.value.max_score = Math.floor(localContent.value.max_score);
  
  // Create a new object to ensure reactivity
  const updatedContent = { ...localContent.value };
  
  // Emit the update event with the updated content
  emit('update:content', updatedContent);
};

// Use ResizeObserver to handle width changes
onMounted(() => {
  // Create a ResizeObserver to monitor width changes
  const resizeObserver = new ResizeObserver(entries => {
    // Get the parent container
    const parent = blockRef.value?.parentElement;
    if (!parent) return;
    
    // Find all content blocks in the parent
    const blocks = Array.from(parent.querySelectorAll('.content-block'));
    if (blocks.length === 0) return;
    
    // Find the maximum width
    let maxWidth = 0;
    blocks.forEach(block => {
      // Get the content width without the variable applied
      block.style.width = 'auto'; // Temporarily remove the variable
      const width = block.getBoundingClientRect().width;
      if (width > maxWidth) {
        maxWidth = width;
      }
    });
    
    // Set the CSS variable on the parent
    if (maxWidth > 0) {
      parent.style.setProperty('--content-block-width', `${maxWidth}px`);
      // Restore the variable-based width
      blocks.forEach(block => {
        block.style.width = '';
      });
    }
  });
  
  // Start observing the block
  if (blockRef.value) {
    resizeObserver.observe(blockRef.value);
    
    // Also observe the parent to catch when new blocks are added
    const parent = blockRef.value.parentElement;
    if (parent) {
      resizeObserver.observe(parent);
    }
  }
  
  // Clean up
  onUnmounted(() => {
    resizeObserver.disconnect();
  });
});
</script>

<style scoped>
.content-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 16px 16px 5px;
  background: var(--form-background);
  border-radius: 8px;
  transition: all 0.2s ease, background-color 0.3s ease;
  max-width: 100%;
  margin: 0;
  align-self: flex-start;
  box-sizing: border-box;
  width: var(--content-block-width, auto);
  min-width: fit-content;
}

.content-block:not(.read-only) {
  border: 1px solid #e5e7eb;
}

.content-block:hover {
  box-shadow: none;
}

.block-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: var(--form-background);
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.block-controls {
  display: flex;
  gap: 8px;
}

.block-controls button,
.remove-btn {
  background: var(--form-background);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  transition: all 0.2s;
  color: var(--text-color);
}

.block-controls button:hover:not(:disabled),
.remove-btn:hover {
  background: var(--button-hover);
}

.block-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.block-type {
  font-weight: 600;
  color: var(--text-color);
  font-size: 14px;
  transition: color 0.3s ease;
}

.block-score {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  margin-right: 10px;
}

.block-score label {
  font-size: 14px;
  color: var(--text-color);
}

.block-score .score-input {
  width: 50px;
  padding: 4px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  /* Hide spinner buttons for number inputs */
  -moz-appearance: textfield; /* Firefox */
}

/* Hide spinner buttons for Chrome, Safari, Edge, Opera */
.score-input::-webkit-outer-spin-button,
.score-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.remove-btn {
  background: var(--error-background, #fef2f2);
  border: 1px solid var(--error-border, #fecaca);
  color: var(--error-color, #dc2626);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  margin-left: 8px;
}

.remove-btn:hover:not(:disabled) {
  background: var(--hover-delete-bg, #fee2e2);
  transform: scale(1.1);
}

.remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon-remove {
  line-height: 1;
  font-weight: bold;
}

.block-content {
  min-height: 100px;
  max-height: 600px;
  overflow-y: auto;
  padding: 8px 8px 8px 5px;
  background: var(--form-background);
  width: 100%;
  text-align: left;
  transition: background-color 0.3s ease;
  /* Fixed width for content */
  max-width: 800px;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Apply fixed width to all text elements within content blocks */
:deep(.block-content p),
:deep(.block-content div),
:deep(.block-content span),
:deep(.block-content li),
:deep(.block-content pre),
:deep(.block-content code),
:deep(.block-content textarea),
:deep(.block-content input[type="text"]),
:deep(.question-text),
:deep(.answer-text) {
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.read-only .block-toolbar {
  display: none;
}

.read-only .block-content {
  max-height: none;
  overflow-y: visible;
}

@media (max-width: 768px) {
  .content-block {
    padding: 12px;
  }

  .block-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .block-type {
    flex: 1;
    text-align: center;
  }
  
  .block-content {
    max-width: 100%;
  }
}

:root {
  --error-background: #fef2f2;
  --error-border: #fecaca;
  --error-color: #dc2626;
  --hover-delete-bg: #fee2e2;
}

.dark-theme {
  --error-background: #3a1a1a;
  --error-border: #ff6b6b;
  --error-color: #ff6b6b;
  --hover-delete-bg: #5a2323;
}

.block-max-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  color: var(--text-color);
  font-size: 0.9em;
  opacity: 0.8;
}

.score-input {
  width: 60px;
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 0.9em;
  text-align: center;
  transition: all 0.2s ease;
}

.score-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb), 0.1);
}

.score-input::-webkit-inner-spin-button,
.score-input::-webkit-outer-spin-button {
  opacity: 1;
  height: 24px;
}

.score-input::placeholder {
  color: var(--text-color);
  opacity: 0.5;
}

/* Dark theme support */
:root {
  --accent-color-rgb: 147, 112, 219;
}

.dark-theme .score-input {
  background: var(--background-secondary);
  border-color: var(--border-color-dark);
}

.dark-theme .score-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb), 0.2);
}

.dark-theme .score-label {
  color: var(--text-color-dark);
}
</style> 