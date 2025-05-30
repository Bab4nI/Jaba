<template>
  <div class="table-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    
    <div v-if="!readOnly" class="table-controls">
      <button @click="addRow" class="control-btn">+ Строка</button>
      <button @click="addColumn" class="control-btn">+ Колонка</button>
      <button
        @click="removeRow"
        class="control-btn"
        :disabled="localContent.data.length <= 1"
      >
        - Строка
      </button>
      <button
        @click="removeColumn"
        class="control-btn"
        :disabled="localContent.data[0]?.length <= 1"
      >
        - Колонка
      </button>
    </div>
    <div class="table-wrapper" v-if="localContent.data.length > 0">
      <table class="editable-table">
        <thead>
          <tr>
            <th v-for="(header, colIndex) in localContent.headers" :key="colIndex">
              <input
                v-if="!readOnly"
                v-model="localContent.headers[colIndex]"
                @input="emitUpdate"
                placeholder="Заголовок"
                class="header-input"
              />
              <span v-else class="header-text">{{ header || 'Заголовок' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in localContent.data" :key="rowIndex">
            <td v-for="(cell, colIndex) in row" :key="colIndex">
              <input
                v-if="!readOnly"
                v-model="localContent.data[rowIndex][colIndex]"
                @input="emitUpdate"
                class="cell-input"
              />
              <span v-else class="cell-text">{{ cell || '' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-table-message">
      Таблица пуста. Добавьте строки и колонки.
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({
      headers: ['Заголовок 1', 'Заголовок 2'],
      data: [['', ''], ['', '']],
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
  headers: getContentData(props.content).headers || props.content.headers || [],
  data: getContentData(props.content).data || props.content.data || []
});

watch(() => props.content, (newContent) => {
  localContent.value = {
    ...newContent,
    headers: getContentData(newContent).headers || newContent.headers || [],
    data: getContentData(newContent).data || newContent.data || []
  };
}, { deep: true });

onMounted(() => {
  localContent.value.headers = getContentData(props.content).headers || props.content.headers || [];
  localContent.value.data = getContentData(props.content).data || props.content.data || [];
});

const emitUpdate = () => {
  emit('update:content', {
    ...props.content,
    content_data: {
      ...getContentData(props.content),
      headers: localContent.value.headers,
      data: localContent.value.data
    }
  });
};

const addRow = () => {
  if (props.readOnly) return;
  const newRow = new Array(localContent.value.data[0].length).fill('');
  localContent.value.data.push(newRow);
  emitUpdate();
};

const addColumn = () => {
  if (props.readOnly) return;
  localContent.value.headers.push(`Заголовок ${localContent.value.headers.length + 1}`);
  localContent.value.data.forEach(row => row.push(''));
  emitUpdate();
};

const removeRow = () => {
  if (props.readOnly || localContent.value.data.length <= 1) return;
  localContent.value.data.pop();
  emitUpdate();
};

const removeColumn = () => {
  if (props.readOnly || localContent.value.data[0].length <= 1) return;
  localContent.value.headers.pop();
  localContent.value.data.forEach(row => row.pop());
  emitUpdate();
};
</script>

<style scoped>
.table-element {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.table-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.control-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.control-btn:hover {
  background: var(--hover-accent);
}

.control-btn:disabled {
  background: var(--secondary-text);
  cursor: not-allowed;
  opacity: 0.5;
}

.table-wrapper {
  overflow-x: auto;
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  transition: border-color 0.3s ease, background-color 0.3s ease;
}

.read-only .table-wrapper {
  border: none;
  background: var(--form-background);
  padding: 10px;
}

.editable-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.editable-table th,
.editable-table td {
  border: 1px solid var(--border-color);
  padding: 12px;
  text-align: left;
  min-width: 120px;
  transition: border-color 0.3s ease, background-color 0.3s ease, color 0.3s ease;
}

.read-only .editable-table th,
.read-only .editable-table td {
  border: 1px solid var(--border-color);
  border-opacity: 0.5;
}

.editable-table th {
  background-color: var(--form-background);
  font-weight: 600;
  color: var(--text-color);
}

.read-only .editable-table th {
  background-color: var(--background-color);
}

.header-input {
  width: 100%;
  padding: 6px;
  border: 1px solid var(--border-color);
  border-radius: 3px;
  font-weight: bold;
  background: transparent;
  color: var(--text-color);
  transition: border-color 0.3s ease, background-color 0.3s ease, color 0.3s ease;
}

.header-text {
  font-weight: 600;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.cell-input {
  width: 100%;
  padding: 6px;
  border: 1px solid var(--border-color);
  border-radius: 3px;
  background: transparent;
  color: var(--text-color);
  transition: border-color 0.3s ease, background-color 0.3s ease, color 0.3s ease;
}

.cell-text {
  color: var(--text-color);
  transition: color 0.3s ease;
}

.cell-input:focus,
.header-input:focus {
  outline: none;
  border-color: var(--accent-color);
  background: var(--form-background);
}

.empty-table-message {
  padding: 20px;
  text-align: center;
  color: var(--secondary-text);
  background: var(--background-color);
  border-radius: 6px;
  border: 1px dashed var(--border-color);
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}

.read-only .empty-table-message {
  background: var(--form-background);
  border: none;
}

/* Dark mode specific overrides for better contrast */
:root.dark-theme .editable-table th {
  background-color: var(--hover-background);
}

:root.dark-theme .read-only .editable-table th {
  background-color: var(--form-background);
}

:root.dark-theme .cell-input:focus,
:root.dark-theme .header-input:focus {
  background-color: var(--hover-background);
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