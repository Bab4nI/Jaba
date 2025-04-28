<template>
  <div class="table-element" :class="{ 'read-only': readOnly }">
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
import { ref, watch } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({
      headers: ['Заголовок 1', 'Заголовок 2'],
      data: [['', ''], ['', '']],
    })
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

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal };
}, { deep: true });

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
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
  background: #a094b8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.control-btn:hover {
  background: #8a7ea3;
}

.control-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.table-wrapper {
  overflow-x: auto;
  width: 100%;
  border: 1px solid #d1d5db; /* Slightly darker border for better visibility */
  border-radius: 6px;
}

.read-only .table-wrapper {
  border: none; /* Keep it borderless in read-only mode per Stepik style */
  background: #ffffff;
  padding: 10px;
}

.editable-table {
  width: 100%;
  border-collapse: separate; /* Use separate to allow for spacing */
  border-spacing: 0;
}

.editable-table th,
.editable-table td {
  border: 1px solid #d1d5db; /* More pronounced borders for clarity */
  padding: 12px; /* Increased padding for better readability */
  text-align: left;
  min-width: 120px; /* Ensure cells have a minimum width for better layout */
}

.read-only .editable-table th,
.read-only .editable-table td {
  border: 1px solid #e5e7eb; /* Subtle borders in read-only mode */
}

.editable-table th {
  background-color: #f3f4f6; /* Slightly darker header background for contrast */
  font-weight: 600;
  color: #1f2937; /* Darker text for headers */
}

.read-only .editable-table th {
  background-color: #f9fafb; /* Lighter header in read-only mode */
}

.header-input {
  width: 100%;
  padding: 6px;
  border: 1px solid #d1d5db;
  border-radius: 3px;
  font-weight: bold;
  background: transparent;
}

.header-text {
  font-weight: 600;
  color: #1f2937;
}

.cell-input {
  width: 100%;
  padding: 6px;
  border: 1px solid #e5e7eb;
  border-radius: 3px;
  background: transparent;
}

.cell-text {
  color: #374151;
}

.cell-input:focus,
.header-input:focus {
  outline: none;
  border-color: #a094b8;
  background: white;
}

.empty-table-message {
  padding: 20px;
  text-align: center;
  color: #666;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px dashed #ddd;
}

.read-only .empty-table-message {
  background: #ffffff;
  border: none;
}
</style>