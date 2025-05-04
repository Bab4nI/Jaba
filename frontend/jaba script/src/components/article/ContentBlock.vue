<template>
  <div class="content-block" :class="{ 'read-only': readOnly }">
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
      <button @click="removeBlock" class="remove-btn" title="Удалить блок">
        <span class="icon-remove">×</span>
      </button>
    </div>
    <div class="block-content">
      <component
        :is="contentComponent"
        :content="content"
        :read-only="readOnly"
        @update:content="updateContent"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
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
  }
});

const emit = defineEmits(['update:content', 'move-up', 'move-down', 'remove']);

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
  emit('update:content', newContent);
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
</script>

<style scoped>
.content-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #f5f9f8;
  border-radius: 8px;
  transition: all 0.2s ease;
  max-width: 800px;
  margin: 0 auto;
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
  background: #f5f9f8;
  border-radius: 6px;
}

.block-controls {
  display: flex;
  gap: 8px;
}

.block-controls button,
.remove-btn {
  background: #f5f9f8;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  transition: all 0.2s;
}

.block-controls button:hover:not(:disabled),
.remove-btn:hover {
  background: #e5e7eb;
}

.block-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.block-type {
  font-weight: 600;
  color: #24222f;
  font-size: 14px;
}

.remove-btn {
  background: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}

.remove-btn:hover {
  background: #fee2e2;
}

.block-content {
  min-height: 100px;
  max-height: 600px;
  overflow-y: auto;
  padding: 8px;
  background: #f5f9f8;
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
}
</style> 