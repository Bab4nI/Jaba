<template>
  <div class="content-block" :class="{ 'read-only': readOnly }" ref="blockRef">
    <div v-if="!readOnly" class="block-toolbar">
      <div class="block-controls">
        <button @click="moveUp" :disabled="isFirst" title="Переместить вверх">
          <span class="icon-up">↑</span>
        </button>
        <button @click="moveDown" :disabled="isLast" title="Переместить вниз">
          <span class="icon-down">↓</span>
        </button>
      </div>
      <div class="block-type">
        <span>{{ blockType }}</span>
      </div>
      <div class="block-score">
        <label for="block-max-score">Баллы:</label>
        <input 
          id="block-max-score"
          v-model.number="localContent.max_score" 
          type="number" 
          min="1" 
          max="10"
          class="score-input"
          @input="updateScore" 
        />
      </div>
      <button @click="removeBlock" class="remove-btn" title="Удалить блок">
        <span class="icon-remove">×</span>
      </button>
    </div>
    <div class="block-content">
      <component
        :is="contentComponent"
        :content="content"
        :read-only="readOnly"
        :show-score="true"
        :allow-preview-edit="props.allowPreviewEdit"
        @update:content="updateContent"
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
  }
});

const blockRef = ref(null);

const emit = defineEmits(['update:content', 'move-up', 'move-down', 'remove', 'answer-submitted']);

const localContent = ref({ 
  ...props.content,
  max_score: props.content.max_score || 1 // Set default score to 1 if not provided
});

watch(() => props.content, (newContent) => {
  localContent.value = { 
    ...newContent,
    max_score: newContent.max_score || 1 // Ensure max_score is always set
  };
}, { deep: true });

const contentComponents = {
  text: TextElement,
  image: ImageElement,
  video: VideoElement,
  code: CodeElement,
  quiz: QuizElement,
  table: TableElement,
  file: FileElement
};

const blockType = computed(() => {
  const types = {
    text: 'Текст',
    image: 'Изображение',
    video: 'Видео',
    code: 'Код',
    quiz: 'Тест',
    table: 'Таблица',
    file: 'Файл'
  };
  return types[props.content.type] || props.content.type;
});

const contentComponent = computed(() => {
  return contentComponents[props.content.type] || TextElement;
});

const updateContent = (newContent) => {
  // Preserve the max_score when updating content
  const updatedContent = {
    ...newContent,
    max_score: newContent.max_score || localContent.value.max_score || 1
  };
  emit('update:content', updatedContent);
};

const handleAnswerSubmitted = (data) => {
  // Make sure we have the content ID and pass it to the parent
  const contentId = props.content.id;
  
  // Log the submission for debugging
  console.log('ContentBlock received answer submission:', {
    contentId,
    originalData: data
  });
  
  // If data is an object with score, pass it along with the content ID
  if (typeof data === 'object' && data !== null) {
    if (data.score !== undefined) {
      // If the object already has a contentId property, use it directly
      if (data.contentId !== undefined) {
        // Pass the object as is to the parent
        emit('answer-submitted', data);
      } else {
        // Add the contentId and pass to the parent
        emit('answer-submitted', contentId, data.score);
      }
    } else {
      emit('answer-submitted', contentId, 0);
    }
  } else {
    // If data is just a score value or something else, pass it directly
    emit('answer-submitted', contentId, data);
  }
};

const moveUp = () => {
  emit('move-up');
};

const moveDown = () => {
  emit('move-down');
};

const removeBlock = () => {
  emit('remove');
};

const updateScore = () => {
  // Ensure score is at least 1
  if (localContent.value.max_score < 1) {
    localContent.value.max_score = 1;
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
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.remove-btn:hover {
  background: var(--hover-delete-bg, #fee2e2);
  color: var(--error-color, #dc2626);
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
</style> 