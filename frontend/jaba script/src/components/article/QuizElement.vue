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
  font-family: Arial, sans-serif;
}

.question-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  background: #f8f9fa;
}

.question-text {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  padding: 8px 0;
  border-bottom: 2px solid #f0f0f0;
}

.answers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
}

.answer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #fff;
}

.correct-answer-radio {
  margin: 0;
  width: 18px;
  height: 18px;
}

.answer-input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 15px;
  background: #f8f9fa;
}

.answer-text {
  flex-grow: 1;
  padding: 10px;
  color: #333;
  font-size: 15px;
}

.answer-indicator {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.correct-answer {
  color: #2e7d32;
}

.remove-answer-btn {
  background: #ff4444;
  color: white;
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiz-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.add-answer-btn {
  background: #5c6bc0;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.warning-text {
  color: #ff4444;
  font-size: 14px;
  font-weight: 500;
}

/* Улучшенные состояния при наведении */
.question-input:hover,
.answer-input:hover {
  border-color: #bdbdbd;
}

.add-answer-btn:hover {
  background: #3f51b5;
}

.remove-answer-btn:hover {
  background: #cc0000;
}
</style>