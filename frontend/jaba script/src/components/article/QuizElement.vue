```vue
<template>
  <div class="quiz-element" :class="{ 'read-only': readOnly }">
    <input
      v-if="!readOnly"
      v-model="localContent.question"
      placeholder="Введите вопрос"
      @input="emitUpdate"
      class="question-input"
    />
    <div v-else class="question-text">{{ localContent.question || 'Вопрос отсутствует' }}</div>
    <div class="answers-list">
      <div v-for="(answer, index) in localContent.answers" :key="index" class="answer-item">
        <input
          v-if="!readOnly"
          type="radio"
          :name="'quiz-' + _uid"
          :checked="localContent.correct_answer === index"
          @change="setCorrectAnswer(index)"
          class="correct-answer-radio"
        />
        <span v-else class="answer-indicator" :class="{ 'correct-answer': localContent.correct_answer === index }">
          {{ localContent.correct_answer === index ? '✔' : '○' }}
        </span>
        <input
          v-if="!readOnly"
          v-model="localContent.answers[index]"
          @input="emitUpdate"
          :placeholder="'Ответ ' + (index + 1)"
          class="answer-input"
        />
        <span v-else class="answer-text">{{ answer || 'Ответ отсутствует' }}</span>
        <button v-if="!readOnly" @click="removeAnswer(index)" class="remove-answer-btn">×</button>
      </div>
    </div>
    <div v-if="!readOnly" class="quiz-controls">
      <button @click="addAnswer" class="add-answer-btn">+ Добавить ответ</button>
      <span v-if="localContent.answers.length < 2" class="warning-text">Нужно минимум 2 ответа</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ question: '', answers: ['', ''], correct_answer: null })
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:content']);

const localContent = ref({
  question: '',
  answers: ['', ''],
  correct_answer: null,
  ...props.content
});

watch(() => props.content, (newVal) => {
  localContent.value = { ...newVal };
}, { deep: true });

const addAnswer = () => {
  if (props.readOnly) return;
  localContent.value.answers.push('');
  emitUpdate();
};

const removeAnswer = (index) => {
  if (props.readOnly || localContent.value.answers.length <= 2) return;
  localContent.value.answers.splice(index, 1);
  if (localContent.value.correct_answer === index) {
    localContent.value.correct_answer = null;
  } else if (localContent.value.correct_answer > index) {
    localContent.value.correct_answer--;
  }
  emitUpdate();
};

const setCorrectAnswer = (index) => {
  if (props.readOnly) return;
  localContent.value.correct_answer = index;
  emitUpdate();
};

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};
</script>

<style scoped>
.quiz-element {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.question-text {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
}

.read-only .question-text {
  padding: 10px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.answers-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.answer-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.correct-answer-radio {
  margin: 0;
}

.answer-input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.answer-text {
  flex-grow: 1;
  padding: 8px;
  color: #2c3e50;
}

.read-only .answer-text {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.answer-indicator {
  font-size: 18px;
  color: #666;
}

.correct-answer {
  color: #4CAF50;
  font-weight: bold;
}

.remove-answer-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.quiz-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.add-answer-btn {
  background: #a094b8;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.warning-text {
  color: #ff6b6b;
  font-size: 14px;
}
</style>
```