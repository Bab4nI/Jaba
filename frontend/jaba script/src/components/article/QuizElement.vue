<template>
  <div class="quiz-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    <div v-if="readOnly && showScore" class="element-score-display">
      <template v-if="userScore !== null">
        <span :class="{'score-success': userScore === localContent.max_score, 'score-fail': userScore < localContent.max_score}">
          {{ userScore }}/{{ localContent.max_score }}
        </span>
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
        <input
          type="radio"
          :name="'quiz-' + uniqueId"
          :checked="localContent.correct_answer === index"
          @change="setCorrectAnswer(index)"
          class="correct-answer-radio"
        />
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
      <div v-else v-for="(answer, index) in localContent.answers" :key="'view-'+index" class="answer-item view-mode">
        <input
          type="radio"
          :name="'quiz-' + uniqueId"
          :checked="selectedAnswer === index"
          @change="selectAnswer(index)"
          class="correct-answer-radio"
          :disabled="quizSubmitted"
        />
        <div class="answer-text" :class="{
          'correct-answer': quizSubmitted && localContent.correct_answer === index,
          'wrong-answer': quizSubmitted && selectedAnswer === index && localContent.correct_answer !== index
        }">
          {{ answer || 'Ответ отсутствует' }}
          <span v-if="quizSubmitted && localContent.correct_answer === index" class="answer-feedback">✓ Правильно</span>
          <span v-if="quizSubmitted && selectedAnswer === index && localContent.correct_answer !== index" class="answer-feedback">✗ Неверно</span>
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
        :disabled="selectedAnswer === null"
      >
        Отправить ответ
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({ 
      question: '', 
      answers: ['', ''], 
      correct_answer: null,
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

// Generate a unique ID for this component instance
const uniqueId = ref(`quiz-${Date.now()}-${Math.floor(Math.random() * 10000)}`);

const localContent = ref({
  question: '',
  answers: ['', ''],
  correct_answer: null,
  max_score: 2,
  ...props.content
});

// User interaction state
const selectedAnswer = ref(null);
const quizSubmitted = ref(false);
const userScore = ref(null);

// Initialize from localStorage if there's saved progress
onMounted(() => {
  if (props.readOnly && props.content.id) {
    const savedData = localStorage.getItem(`quiz_${props.content.id}`);
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        selectedAnswer.value = data.selectedAnswer;
        quizSubmitted.value = data.quizSubmitted;
        userScore.value = data.userScore;
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
    correct_answer: null,
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

// Interaction functions for view mode
const selectAnswer = (index) => {
  if (quizSubmitted.value) return;
  selectedAnswer.value = index;
};

const submitQuiz = () => {
  if (selectedAnswer.value === null) return;
  
  quizSubmitted.value = true;
  userScore.value = selectedAnswer.value === localContent.value.correct_answer 
    ? localContent.value.max_score 
    : 0;
  
  // Save progress to localStorage
  if (props.content.id) {
    localStorage.setItem(`quiz_${props.content.id}`, JSON.stringify({
      selectedAnswer: selectedAnswer.value,
      quizSubmitted: quizSubmitted.value,
      userScore: userScore.value
    }));
  }
  
  // Emit event for parent components
  emit('answer-submitted', {
    contentId: props.content.id,
    selectedAnswer: selectedAnswer.value,
    isCorrect: selectedAnswer.value === localContent.value.correct_answer,
    score: userScore.value,
    maxScore: localContent.value.max_score
  });

  // Log the submission for debugging
  console.log('Quiz submitted:', {
    contentId: props.content.id,
    selectedAnswer: selectedAnswer.value,
    correctAnswer: localContent.value.correct_answer,
    isCorrect: selectedAnswer.value === localContent.value.correct_answer,
    score: userScore.value,
    maxScore: localContent.value.max_score
  });
};

const resetQuiz = () => {
  selectedAnswer.value = null;
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
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border-color, #c5c8cc);
  border-radius: 6px;
  background: var(--background-color, #ebefef);
  transition: all 0.3s ease;
  width: 100%;
  overflow: hidden;
  flex-wrap: wrap; /* Allow wrapping of content */
}

.answer-item.view-mode {
  cursor: pointer;
  transition: all 0.2s ease;
}

.answer-item.view-mode:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.answer-item .correct-answer-radio {
  margin: 0;
  width: 18px;
  height: 18px;
  accent-color: var(--accent-color, #a094b8);
  flex-shrink: 0;
  cursor: pointer;
  margin-top: 3px;
}

.answer-input {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #c5c8cc);
  border-radius: 4px;
  font-size: 15px;
  background: var(--background-color, #ebefef);
  color: var(--text-color, #24222f);
  transition: all 0.3s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-height: 20px;
  resize: vertical;
  line-height: 1.5;
  /* Ensure text wrapping */
  max-width: 100%;
  width: calc(100% - 60px); /* Account for radio button and remove button */
  overflow: hidden; /* Remove scrolling */
  white-space: pre-wrap; /* Preserve line breaks */
}

.answer-text {
  flex-grow: 1;
  padding: 8px 12px;
  color: var(--text-color, #24222f);
  font-size: 15px;
  transition: all 0.3s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
  position: relative;
  /* Ensure text wrapping */
  max-width: 100%;
  display: block; /* Ensure block display for proper wrapping */
}

.answer-feedback {
  margin-left: 8px;
  font-size: 14px;
  font-weight: bold;
}

.correct-answer {
  color: #2e8b33;
  background-color: rgba(76, 175, 80, 0.15);
  border-radius: 4px;
  font-weight: 600;
}

.wrong-answer {
  color: var(--error-color, #da1f38);
  background-color: rgba(244, 67, 54, 0.15);
  border-radius: 4px;
  font-weight: 600;
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
}

:global(.dark-theme) .element-score-display {
  background: rgba(255, 255, 255, 0.08);
}
</style>