<template>
  <div class="fill-in-element" :class="{ 'read-only': readOnly }">
    <!-- Score display -->
    <div v-if="readOnly && showScore" class="element-score-display" :class="{ 'visible': quizSubmitted }">
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

    <!-- Edit Mode -->
    <div v-if="!readOnly" class="edit-mode">
      <textarea
        v-model="localContent.text"
        placeholder="Введите текст с пропусками. Используйте _ для обозначения пропуска."
        @input="emitUpdate"
        class="text-input"
        rows="4"
      ></textarea>
      <div class="answers-section">
        <div v-for="(answer, index) in localContent.answers" :key="index" class="answer-item">
          <input
            type="text"
            v-model="localContent.answers[index]"
            :placeholder="'Правильный ответ ' + (index + 1)"
            class="answer-input"
          />
          <button @click="removeAnswer(index)" class="remove-answer-btn">×</button>
        </div>
        <button @click="addAnswer" class="add-answer-btn">+ Добавить вариант ответа</button>
      </div>
    </div>

    <!-- View Mode -->
    <div v-else class="view-mode">
      <div class="text-content" v-html="formattedText"></div>
      <div v-if="!isSubmitted" class="answer-inputs">
        <input
          v-for="(_, index) in blankCount"
          :key="index"
          type="text"
          v-model="userAnswers[index]"
          :placeholder="'Ответ ' + (index + 1)"
          class="fill-in-input"
          :disabled="isSubmitted"
        />
      </div>
      <div v-if="isSubmitted" class="answer-feedback">
        <div v-for="(answer, index) in userAnswers" :key="index" class="feedback-item">
          <span :class="{
            'correct-answer': isAnswerCorrect(answer, index),
            'wrong-answer': !isAnswerCorrect(answer, index)
          }">
            {{ answer }}
            <span v-if="isAnswerCorrect(answer, index)" class="answer-feedback">✓ Правильно</span>
            <span v-else class="answer-feedback">✗ Неверно</span>
          </span>
        </div>
      </div>
      <button 
        v-if="!isSubmitted" 
        @click="submitAnswers" 
        class="submit-btn"
        :disabled="!areAllAnswersFilled"
      >
        Проверить ответы
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps({
  content: {
    type: Object,
    required: true,
    default: () => ({
      text: '',
      answers: [],
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
  text: getContentData(props.content).text || props.content.text || '',
  answers: getContentData(props.content).answers || props.content.answers || []
});

// User interaction state
const userAnswers = ref([]);
const isSubmitted = ref(false);
const userScore = ref(null);

// Generate a unique ID for this component instance
const uniqueId = ref(`fillin-${Date.now()}-${Math.floor(Math.random() * 10000)}`);

// Initialize from localStorage if there's saved progress
onMounted(() => {
  if (props.readOnly && props.content.id) {
    const savedData = localStorage.getItem(`fillin_${props.content.id}`);
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        userAnswers.value = data.userAnswers;
        isSubmitted.value = data.isSubmitted;
        userScore.value = data.userScore;
        
        // If we have saved answers, emit them to update the parent score
        if (isSubmitted.value && userScore.value !== null) {
          emit('answer-submitted', {
            contentId: props.content.id,
            userAnswers: userAnswers.value,
            score: userScore.value,
            maxScore: localContent.value.max_score
          });
        }
      } catch (e) {
        console.error('Error loading fill-in state:', e);
        // Reset state if there's an error loading saved data
        resetQuiz();
      }
    } else {
      // Reset state if no saved data exists
      resetQuiz();
    }
  }
});

const blankCount = computed(() => {
  return (localContent.value.text.match(/_/g) || []).length;
});

const formattedText = computed(() => {
  if (!localContent.value.text) return '';
  return localContent.value.text.replace(/_/g, '<span class="blank-space">_____</span>');
});

const areAllAnswersFilled = computed(() => {
  return userAnswers.value.length === blankCount.value && 
         userAnswers.value.every(answer => answer.trim() !== '');
});

const addAnswer = () => {
  if (props.readOnly) return;
  localContent.value.answers.push('');
  emitUpdate();
};

const removeAnswer = (index) => {
  if (props.readOnly) return;
  localContent.value.answers.splice(index, 1);
  emitUpdate();
};

const emitUpdate = () => {
  emit('update:content', localContent.value);
};

const normalizeAnswer = (answer) => {
  if (!answer) return '';
  return answer.trim().toLowerCase()
    .replace(/,/g, '.') // Replace commas with dots for numbers
    .replace(/\s+/g, ' '); // Normalize spaces
};

const isAnswerCorrect = (userAnswer, index) => {
  const normalizedUserAnswer = normalizeAnswer(userAnswer);
  return localContent.value.answers.some(correctAnswer => 
    normalizeAnswer(correctAnswer) === normalizedUserAnswer
  );
};

const submitAnswers = () => {
  if (isSubmitted.value) return;
  
  isSubmitted.value = true;
  const correctAnswers = userAnswers.value.filter((answer, index) => 
    isAnswerCorrect(answer, index)
  ).length;
  
  const totalBlanks = blankCount.value;
  userScore.value = Math.round((correctAnswers / totalBlanks) * localContent.value.max_score);
  
  // Save state to localStorage
  if (props.content.id) {
    localStorage.setItem(`fillin_${props.content.id}`, JSON.stringify({
      userAnswers: userAnswers.value,
      isSubmitted: true,
      userScore: userScore.value
    }));
  }
  
  // Emit the result
  emit('answer-submitted', {
    contentId: props.content.id,
    userAnswers: userAnswers.value,
    score: userScore.value,
    maxScore: localContent.value.max_score
  });
};

const resetQuiz = () => {
  userAnswers.value = [];
  isSubmitted.value = false;
  userScore.value = null;
  
  // Clear localStorage
  if (props.content.id) {
    localStorage.removeItem(`fillin_${props.content.id}`);
  }
  
  // Emit reset
  emit('answer-submitted', {
    contentId: props.content.id,
    userAnswers: [],
    score: 0,
    maxScore: localContent.value.max_score
  });
};

watch(() => props.content, (newContent) => {
  localContent.value = {
    ...newContent,
    text: getContentData(newContent).text || newContent.text || '',
    answers: getContentData(newContent).answers || newContent.answers || []
  };
}, { deep: true });

// Add watch for readOnly prop to handle reset
watch(() => props.readOnly, (newVal) => {
  if (newVal) {
    // Reset the component state when readOnly changes to true
    userAnswers.value = [];
    isSubmitted.value = false;
    userScore.value = null;
    
    // Clear localStorage
    if (props.content.id) {
      localStorage.removeItem(`fillin_${props.content.id}`);
    }
    
    // Emit reset
    emit('answer-submitted', {
      contentId: props.content.id,
      userAnswers: [],
      score: 0,
      maxScore: localContent.value.max_score
    });
  }
});
</script>

<style scoped>
.fill-in-element {
  background: var(--form-background);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.element-score-display {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
}

.score-success {
  color: #2e8b33;
  font-weight: 600;
}

.score-fail {
  color: #dc2626;
  font-weight: 600;
}

.score-pending {
  color: var(--text-color);
  opacity: 0.7;
}

.reset-score-btn {
  background: none;
  border: none;
  color: var(--text-color);
  opacity: 0.5;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.reset-score-btn:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

.text-input {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin-bottom: 15px;
  font-family: inherit;
  resize: vertical;
  background: var(--background-color);
  color: var(--text-color);
}

.answers-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.answer-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.answer-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-color);
}

.remove-answer-btn {
  background: var(--error-background);
  color: var(--error-color);
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-answer-btn:hover {
  background: var(--hover-delete-bg);
}

.add-answer-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  align-self: flex-start;
  transition: all 0.2s;
}

.add-answer-btn:hover {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.text-content {
  margin-bottom: 20px;
  line-height: 1.6;
  color: var(--text-color);
}

.blank-space {
  display: inline-block;
  min-width: 100px;
  border-bottom: 2px solid var(--text-color);
  margin: 0 4px;
}

.answer-inputs {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.fill-in-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-color);
}

.submit-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.answer-feedback {
  margin-top: 15px;
}

.feedback-item {
  margin-bottom: 8px;
}

.correct-answer {
  color: #2e8b33;
  font-weight: 500;
}

.wrong-answer {
  color: #dc2626;
  font-weight: 500;
}

.answer-feedback {
  margin-left: 8px;
  font-size: 0.9em;
}

:root {
  --error-background: #fef2f2;
  --error-color: #dc2626;
  --hover-delete-bg: #fee2e2;
}

.dark-theme {
  --error-background: #3a1a1a;
  --error-color: #ff6b6b;
  --hover-delete-bg: #5a2323;
}
</style> 