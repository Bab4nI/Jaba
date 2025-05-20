<template>
  <div class="article-header" :class="{'preview-mode': previewMode}">
    <input
      v-model="titleProxy"
      type="text"
      class="article-title"
      :placeholder="isEditMode ? 'Название работы' : ''"
      :readonly="!isEditMode || isTimeExpired"
      :disabled="!isEditMode || isTimeExpired"
      @click="handleTitleClick"
    >
    <div class="mode-controls" v-if="isAdmin && !isTimeExpired">
      <div class="ai-control" v-if="isEditMode">
        <label class="ai-toggle">
          <input 
            type="checkbox" 
            v-model="aiEnabledProxy"
            @change="$emit('ai-toggle', aiEnabledProxy)"
          >
          <span class="ai-toggle-label">AI Чат</span>
        </label>
      </div>
      <button 
        @click="$emit('toggle-mode')" 
        class="mode-toggle-btn"
        :class="{ 'active': isEditMode }"
        style="pointer-events: auto;"
      >
        {{ isEditMode ? 'Предпросмотр' : 'Редактировать' }}
      </button>
    </div>
    <button
      @click="$emit('go-back')"
      class="back-button"
      aria-label="Вернуться к модулям"
      style="margin-left: 16px; pointer-events: auto;"
    >
      <span class="btn-icon">←</span>
      К модулям
    </button>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  title: String,
  isEditMode: Boolean,
  isAdmin: Boolean,
  isTimeExpired: Boolean,
  previewMode: Boolean,
  aiEnabled: Boolean,
});

const emits = defineEmits(['update:title', 'toggle-mode', 'go-back', 'ai-toggle', 'title-click']);

const titleProxy = ref(props.title);
watch(() => props.title, val => titleProxy.value = val);
watch(titleProxy, val => emits('update:title', val));

const aiEnabledProxy = ref(props.aiEnabled);
watch(() => props.aiEnabled, val => aiEnabledProxy.value = val);
watch(aiEnabledProxy, val => emits('ai-toggle', val));

const handleTitleClick = (e) => {
  emits('title-click', e);
};
</script>

<style scoped>
.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  background: var(--form-background);
  border-radius: 8px;
  padding: 1.5rem;
  transition: background-color 0.5s ease, box-shadow 0.4s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.article-title {
  flex: 1;
  font-size: 2rem;
  font-weight: 600;
  padding: 1rem;
  border: none;
  border-bottom: 2px solid var(--accent-color);
  background: transparent;
  color: var(--text-color);
  outline: none;
  transition: border-color 0.4s, color 0.4s ease, transform 0.3s;
  margin-right: 2rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  max-width: 100%;
}

.article-title:focus:not(:disabled) {
  border-color: var(--secondary-text);
  transform: translateY(-2px);
}

.article-title:read-only,
.article-title:disabled {
  border-color: transparent;
  cursor: default;
  opacity: 1;
  background-color: transparent;
  pointer-events: none;
  -webkit-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.mode-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.mode-toggle-btn,
.back-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: all 0.2s ease;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.mode-toggle-btn::before,
.back-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.2));
  transform: translateX(-100%);
  transition: transform 0.4s ease-out;
}

.mode-toggle-btn:hover::before,
.back-button:hover::before {
  transform: translateX(0);
}

.mode-toggle-btn:hover:not(:disabled),
.back-button:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.mode-toggle-btn:active,
.back-button:active {
  transform: translateY(0);
}

.mode-toggle-btn.active {
  background: var(--secondary-text);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
}

.ai-control {
  display: flex;
  align-items: center;
  margin-right: 15px;
}

.ai-toggle {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  position: relative;
  padding: 4px;
  border-radius: 20px;
  transition: background-color 0.3s ease;
}

.ai-toggle:hover {
  background-color: rgba(160, 148, 184, 0.1);
}

.ai-toggle input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.ai-toggle-label {
  font-size: 14px;
  color: var(--text-color);
  transition: color var(--transition-speed) var(--transition-timing);
  margin-left: 32px;
  position: relative;
}

.ai-toggle-label::before {
  content: '';
  position: absolute;
  left: -32px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 14px;
  background-color: var(--border-color);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.ai-toggle-label::after {
  content: '';
  position: absolute;
  left: -30px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  background-color: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.ai-toggle input[type="checkbox"]:checked + .ai-toggle-label::before {
  background-color: var(--accent-color);
}

.ai-toggle input[type="checkbox"]:checked + .ai-toggle-label::after {
  left: -16px;
}

.ai-toggle input[type="checkbox"]:focus + .ai-toggle-label::before {
  box-shadow: 0 0 0 2px rgba(160, 148, 184, 0.3);
}

:global(.dark-theme) .ai-toggle-label {
  color: var(--text-color);
}

:global(.dark-theme) .ai-toggle-label::before {
  background-color: var(--border-color);
}

:global(.dark-theme) .ai-toggle-label::after {
  background-color: var(--background-color);
}

.back-button {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: background-color 0.2s, transform 0.1s;
  min-width: 120px;
}

.back-button:hover:not(:disabled) {
  background: #8b7ca5;
  transform: translateY(-1px);
}

.back-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.back-button .btn-icon {
  font-size: 18px;
  line-height: 1;
}
</style> 