<template>
  <div class="quiz-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    <div v-if="readOnly && showScore && quizSubmitted" class="element-score-display" :class="{ 'visible': quizSubmitted }">
      <template v-if="userScore !== null">
        <span :class="{'score-success': userScore === localContent.max_score, 'score-fail': userScore < localContent.max_score}">
          {{ userScore }}/{{ localContent.max_score }}
        </span>
        <button v-if="!readOnly" @click="resetQuiz" class="reset-score-btn" title="Сбросить баллы">×</button>
      </template>
      <template v-else>
        <span class="score-pending">{{ localContent.max_score }} баллов</span>
      </template>
    </div>
    
    <!-- Edit Mode - Question Input -->
    <div class="question-header" v-if="!readOnly">
      <textarea
        v-model="localContent.question"
        placeholder="Введите вопрос"
        @input="emitUpdate"
        class="question-input"
        rows="2"
        @keyup="autoGrow($event)"
      ></textarea>
    </div>
    
    <!-- View Mode - Question Display -->
    <div v-else class="question-header">
      <div class="question-text">{{ localContent.question || 'Вопрос отсутствует' }}</div>
    </div>
    
    <!-- Answers List -->
    <div class="answers-list">
      <!-- Edit Mode - Answer Items -->
      <div v-if="!readOnly" v-for="(answer, index) in localContent.answers" :key="index" class="answer-item">
        <div class="checkbox-wrapper">
          <input
            type="checkbox"
            :id="'correct-answer-' + index"
            :checked="localContent.correct_answers.includes(index)"
            @change="setCorrectAnswer(index)"
            class="correct-answer-checkbox"
          />
          <label :for="'correct-answer-' + index" class="checkbox-label">
            <span class="checkbox-custom"></span>
          </label>
        </div>
        <textarea
          v-model="localContent.answers[index]"
          @input="emitUpdate"
          :placeholder="'Ответ ' + (index + 1)"
          class="answer-input"
          rows="1"
          @keyup="autoGrow($event)"
        ></textarea>
        <button @click="removeAnswer(index)" class="remove-answer-btn">×</button>
      </div>
      
      <!-- View Mode - Answer Items -->
      <div v-else v-for="(answer, index) in localContent.answers" :key="'view-'+index" 
        class="answer-item view-mode" 
        :class="{
          'selected': selectedAnswers.includes(index),
          'correct': quizSubmitted && localContent.correct_answers.includes(index),
          'incorrect': quizSubmitted && selectedAnswers.includes(index) && !localContent.correct_answers.includes(index)
        }"
      >
        <input
          v-if="!quizSubmitted"
          type="checkbox"
          :id="'quiz-view-checkbox-' + index"
          :checked="selectedAnswers.includes(index)"
          @change="selectAnswer(index)"
          class="correct-answer-checkbox"
        />
        <label v-if="!quizSubmitted" :for="'quiz-view-checkbox-' + index" class="checkbox-label">
          <span class="checkbox-custom"></span>
        </label>
        <div class="answer-text">
          {{ answer || 'Ответ отсутствует' }}
          <span v-if="quizSubmitted && localContent.correct_answers.includes(index)" class="correct-feedback">✓ Правильно</span>
          <span v-if="quizSubmitted && selectedAnswers.includes(index) && !localContent.correct_answers.includes(index)" class="incorrect-feedback">✗ Неверно</span>
        </div>
      </div>
    </div>
    
    <!-- Quiz Controls -->
    <div v-if="!readOnly" class="quiz-controls">
      <button @click="addAnswer" class="add-answer-btn">+ Добавить ответ</button>
      <span v-if="localContent.answers.length < 2" class="warning-text">Нужно минимум 2 ответа</span>
    </div>
    
    <!-- Submit Button for View Mode -->
    <div v-if="readOnly && !quizSubmitted" class="quiz-submit">
      <button 
        @click="submitQuiz" 
        class="submit-btn" 
        :disabled="selectedAnswers.length === 0"
      >
        Отправить ответ
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, computed } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ 
      question: '', 
      answers: ['', ''], 
      correct_answers: [],
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
  },
  resetKey: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['update:content', 'answer-submitted']);
const themeStore = useThemeStore();

// Generate a unique ID for this component instance
const uniqueId = ref(`quiz-${Date.now()}-${Math.floor(Math.random() * 10000)}`);

const localContent = ref({
  question: '',
  answers: ['', ''],
  correct_answers: [],
  max_score: 2,
  ...props.content
});

// User interaction state
const selectedAnswers = ref([]);
const quizSubmitted = ref(false);
const userScore = ref(null);

// Initialize from localStorage if there's saved progress
onMounted(() => {
  // Load saved state from localStorage if available
  if (props.readOnly && props.content.id) {
    const savedData = localStorage.getItem(`quiz_${props.content.id}`);
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        selectedAnswers.value = Array.isArray(data.selectedAnswers) ? data.selectedAnswers : [];
        quizSubmitted.value = data.quizSubmitted;
        userScore.value = data.userScore;
        console.log(`Loaded saved state for quiz ${props.content.id}:`, { selectedAnswers: selectedAnswers.value, quizSubmitted: quizSubmitted.value, userScore: userScore.value });
        // If we have a saved answer, emit it to update the parent score
        if (quizSubmitted.value && selectedAnswers.value.length > 0) {
          const correctSet = new Set(localContent.value.correct_answers);
          const userSet = new Set(selectedAnswers.value);
          const correctCount = localContent.value.correct_answers.filter(idx => userSet.has(idx)).length;
          const totalCorrect = localContent.value.correct_answers.length;
          const score = totalCorrect > 0 ? Math.round((correctCount / totalCorrect) * localContent.value.max_score) : 0;
          emit('answer-submitted', {
            contentId: props.content.id,
            selectedAnswers: selectedAnswers.value,
            score: score,
            maxScore: localContent.value.max_score
          });
        }
      } catch (e) {
        console.error('Error loading quiz state:', e);
      }
    }
  }
});

watch(() => props.content, (newVal) => {
  localContent.value = { 
    question: '',
    answers: ['', ''],
    correct_answers: [],
    max_score: 1,
    ...newVal 
  };
}, { deep: true });

const addAnswer = () => {
  if (props.readOnly) return;
  localContent.value.answers.push('');
  emitUpdate();
};

const removeAnswer = (index) => {
  if (props.readOnly || localContent.value.answers.length <= 2) return;
  localContent.value.answers.splice(index, 1);
  if (localContent.value.correct_answers.includes(index)) {
    const answerIndex = localContent.value.correct_answers.indexOf(index);
    localContent.value.correct_answers.splice(answerIndex, 1);
  }
  emitUpdate();
};

const setCorrectAnswer = (index) => {
  if (props.readOnly) return;
  const answerIndex = localContent.value.correct_answers.indexOf(index);
  if (answerIndex === -1) {
    localContent.value.correct_answers.push(index);
  } else {
    localContent.value.correct_answers.splice(answerIndex, 1);
  }
  emitUpdate();
};

const emitUpdate = () => {
  if (props.readOnly) return;
  emit('update:content', { ...localContent.value });
};

// Interaction functions for view mode
const selectAnswer = (index) => {
  if (quizSubmitted.value) return;
  const idx = selectedAnswers.value.indexOf(index);
  if (idx === -1) {
    selectedAnswers.value.push(index);
  } else {
    selectedAnswers.value.splice(idx, 1);
  }
};

const submitQuiz = () => {
  if (selectedAnswers.value.length === 0) return;
  quizSubmitted.value = true;
  // Calculate score: (number of correct selected / total correct) * max_score
  const correctSet = new Set(localContent.value.correct_answers);
  const userSet = new Set(selectedAnswers.value);
  const correctCount = localContent.value.correct_answers.filter(idx => userSet.has(idx)).length;
  const totalCorrect = localContent.value.correct_answers.length;
  userScore.value = totalCorrect > 0 ? Math.round((correctCount / totalCorrect) * localContent.value.max_score) : 0;
  // Save progress to localStorage
  if (props.content.id) {
    localStorage.setItem(`quiz_${props.content.id}`, JSON.stringify({
      selectedAnswers: selectedAnswers.value,
      quizSubmitted: quizSubmitted.value,
      userScore: userScore.value
    }));
  }
  // Emit event for parent components
  emit('answer-submitted', {
    contentId: props.content.id,
    selectedAnswers: selectedAnswers.value,
    score: userScore.value,
    maxScore: localContent.value.max_score
  });
  // Log the submission for debugging
  console.log('Quiz submitted:', {
    contentId: props.content.id,
    selectedAnswers: selectedAnswers.value,
    correctAnswers: localContent.value.correct_answers,
    score: userScore.value,
    maxScore: localContent.value.max_score
  });
};

const resetQuiz = () => {
  selectedAnswers.value = [];
  quizSubmitted.value = false;
  userScore.value = null;
  
  // Clear saved progress
  if (props.content.id) {
    localStorage.removeItem(`quiz_${props.content.id}`);
  }
};

// Auto-resize textarea to fit content
const autoGrow = (event) => {
  const textarea = event.target;
  textarea.style.height = 'auto';
  textarea.style.height = (textarea.scrollHeight) + 'px';
};

// Add autoGrow to question input as well
watch(() => localContent.value.question, () => {
  nextTick(() => {
    const questionInput = document.querySelector('.question-input');
    if (questionInput && questionInput.tagName === 'TEXTAREA') {
      questionInput.style.height = 'auto';
      questionInput.style.height = (questionInput.scrollHeight) + 'px';
    }
  });
});

// Apply autoGrow to all answers on change
watch(() => localContent.value.answers, () => {
  nextTick(() => {
    document.querySelectorAll('.answer-input').forEach(textarea => {
      textarea.style.height = 'auto';
      textarea.style.height = (textarea.scrollHeight) + 'px';
    });
  });
}, { deep: true });

// Watch for resetKey changes
watch(() => props.resetKey, () => {
  selectedAnswers.value = [];
  quizSubmitted.value = false;
  userScore.value = null;
  if (props.content.id) {
    localStorage.removeItem(`quiz_${props.content.id}`);
  }
});
</script>

<style scoped>
.quiz-element {
  display: flex;
  flex-direction: column;
  gap: 15px;
  font-family: Arial, sans-serif;
  width: 100%;
  max-width: 100%;
  background: var(--form-background, #f5f9f8);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  position: relative;
  /* Fixed width for quiz elements */
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 15px;
  width: 100%;
}

.question-input {
  flex: 1;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #c5c8cc);
  border-radius: 6px;
  font-size: 16px;
  background: var(--background-color, #ebefef);
  color: var(--text-color, #24222f);
  transition: all 0.3s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-height: 50px;
  white-space: pre-wrap; /* Ensure line breaks are preserved */
  resize: vertical; /* Allow vertical resizing */
  overflow: hidden; /* Remove scrolling */
}

.question-text {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #24222f);
  padding: 12px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  width: 100%;
  line-height: 1.5;
  /* Ensure text wrapping */
  max-width: 100%;
  display: block; /* Ensure block display for proper wrapping */
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

.score-fail {
  color: var(--error-color, #da1f38);
  font-weight: 700;
}

.score-pending {
  color: var(--secondary-text, #575667);
}

.answers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
  width: 100%;
}

.answer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--background-color, #ffffff);
  border: 2px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  transition: all 0.3s ease;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  resize: none;
  min-height: 50px;
  max-height: 200px;
}

.answer-item:hover {
  border-color: var(--accent-color, #a094b8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.answer-item.selected {
  border-color: var(--accent-color, #a094b8);
  background: rgba(160, 148, 184, 0.1);
  box-shadow: 0 4px 12px rgba(160, 148, 184, 0.15);
}

.answer-item.correct {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.answer-item.incorrect {
  border-color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

.answer-item input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.answer-item .checkbox-custom {
  position: relative;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.answer-item:hover .checkbox-custom {
  border-color: var(--accent-color);
  transform: scale(1.1);
}

.answer-item input[type="checkbox"]:checked + .checkbox-custom {
  border-color: var(--accent-color);
  background: var(--accent-color);
}

.answer-item input[type="checkbox"]:focus + .checkbox-custom {
  box-shadow: 0 0 0 3px rgba(160, 148, 184, 0.3);
}

.answer-item.correct .checkbox-custom {
  border-color: #4CAF50;
  background: #4CAF50;
}

.answer-item.incorrect .checkbox-custom {
  border-color: #f44336;
  background: #f44336;
}

.answer-item.correct input[type="checkbox"]:checked + .checkbox-custom::after,
.answer-item.incorrect input[type="checkbox"]:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.answer-text {
  flex-grow: 1;
  font-size: 16px;
  color: var(--text-color, #24222f);
  transition: color 0.3s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.answer-item.selected .answer-text {
  font-weight: 500;
  color: var(--accent-color, #a094b8);
}

.answer-item.correct .answer-text {
  color: #4CAF50;
}

.answer-item.incorrect .answer-text {
  color: #f44336;
}

.answer-controls {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.answer-item:hover .answer-controls {
  opacity: 1;
}

.answer-control-btn {
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.answer-control-btn:hover {
  background: rgba(160, 148, 184, 0.1);
  color: var(--accent-color);
  transform: scale(1.1);
}

.answer-control-btn.remove {
  color: var(--error-color);
}

.answer-control-btn.remove:hover {
  background: rgba(244, 67, 54, 0.1);
}

.remove-answer-btn {
  background: var(--error-color, #da1f38);
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
  transition: background-color 0.3s ease;
  flex-shrink: 0;
}

.remove-answer-btn:hover {
  background: var(--hover-delete, #c62828);
  transform: scale(1.1);
}

.quiz-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.add-answer-btn, .submit-btn, .retry-btn {
  background: var(--accent-color, #a094b8);
  color: var(--footer-text, #fff);
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.add-answer-btn:hover, .submit-btn:hover, .retry-btn:hover {
  background: var(--hover-accent, #7b68a7);
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.submit-btn {
  background: #4caf50;
  font-weight: 600;
  padding: 10px 20px;
}

.submit-btn:hover {
  background: #43a047;
}

.submit-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.retry-btn {
  background: #2196f3;
}

.retry-btn:hover {
  background: #1e88e5;
}

.quiz-submit {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.warning-text {
  color: var(--error-color, #da1f38);
  font-size: 14px;
  transition: color 0.3s ease;
}

.read-only.quiz-element {
  box-shadow: none;
}

/* Dark theme adjustments */
:global(.dark-theme) .quiz-element {
  --form-background: #23222b;
  --background-color: #2d2c38;
  --text-color: #f5f9f8;
  --secondary-text: #adadad;
  --border-color: #3e3d49;
  --thead-background: #2d2c38;
  --error-color: #ff4d4d;
  --accent-color: #a094b8;
  --hover-accent: #7b68a7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

:global(.dark-theme) .question-text,
:global(.dark-theme) .score-display {
  background: rgba(255, 255, 255, 0.08);
}

:global(.dark-theme) .correct-answer {
  background-color: rgba(76, 175, 80, 0.25);
  color: #6bdb70;
}

:global(.dark-theme) .wrong-answer {
  background-color: rgba(244, 67, 54, 0.25);
}

:global(.dark-theme) .answer-item.view-mode:hover {
  background: rgba(255, 255, 255, 0.1);
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
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.element-score-display.visible {
  opacity: 1;
  transform: translateY(0);
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

.correct-feedback {
  margin-left: 8px;
  font-weight: 500;
  color: #4CAF50;
}

.incorrect-feedback {
  margin-left: 8px;
  font-weight: 500;
  color: #f44336;
}

/* Dark theme styles */
:global(.dark-theme) .correct-feedback {
  color: #6bdb70;
}

:global(.dark-theme) .incorrect-feedback {
  color: #ff6b6b;
}

.answer-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 6px;
  background: var(--background-color, #ffffff);
  color: var(--text-color, #24222f);
  resize: none;
  min-height: 50px;
  max-height: 200px;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.answer-input:focus {
  outline: none;
  border-color: var(--accent-color, #a094b8);
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.2);
}

/* Dark theme styles */
:global(.dark-theme) .answer-input {
  background: var(--background-color, #2d2c38);
  border-color: var(--border-color, #3e3d49);
  color: var(--text-color, #f5f9f8);
}

:global(.dark-theme) .answer-input:focus {
  border-color: var(--accent-color, #a094b8);
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.3);
}

:global(.dark-theme) .answer-input::placeholder {
  color: var(--secondary-text, #adadad);
}

.checkbox-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  margin-right: 10px;
}

.correct-answer-checkbox {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-custom {
  position: relative;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  background: var(--background-color);
  transition: all 0.2s ease;
}

.correct-answer-checkbox:checked + .checkbox-label .checkbox-custom {
  background: var(--accent-color);
  border-color: var(--accent-color);
}

.correct-answer-checkbox:checked + .checkbox-label .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
}

.checkbox-label:hover .checkbox-custom {
  border-color: var(--accent-color);
}
</style>