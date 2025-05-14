<template>
  <div class="text-element" :class="{ 'read-only': readOnly }">
    <!-- Score display at the top when in read-only mode -->
    
    <div v-if="!readOnly" class="formatting-toolbar">
      <button @click="formatText('bold')" title="Жирный">
        <span class="icon-bold">B</span>
      </button>
      <button @click="formatText('italic')" title="Курсив">
        <span class="icon-italic">I</span>
      </button>
      <button @click="formatText('underline')" title="Подчеркнутый">
        <span class="icon-underline">U</span>
      </button>
      <div class="toolbar-divider"></div>
      <button @click="formatText('justifyLeft')" title="Выровнять по левому краю">
        <span class="icon-align-left">←</span>
      </button>
      <button @click="formatText('justifyCenter')" title="Выровнять по центру">
        <span class="icon-align-center">↔</span>
      </button>
      <button @click="formatText('justifyRight')" title="Выровнять по правному краю">
        <span class="icon-align-right">→</span>
      </button>
      <div class="toolbar-divider"></div>
      <button @click="formatText('insertOrderedList')" title="Нумерованный список">
        <span class="icon-ordered-list">1.</span>
      </button>
      <button @click="formatText('insertUnorderedList')" title="Маркированный список">
        <span class="icon-unordered-list">•</span>
      </button>
    </div>
    <div
      ref="editor"
      class="text-editor"
      :contenteditable="!readOnly"
      :class="{ 'read-only': readOnly }"
      @input="onInput"
      @keydown="onKeyDown"
      @paste="onPaste"
      @mouseup="onSelectionChange"
      @focus="onFocus"
      @blur="onBlur"
    ></div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'

export default {
  name: 'TextElement',
  props: {
    content: {
      type: Object,
      required: true
    },
    readOnly: {
      type: Boolean,
      default: false
    },
    showScore: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:content'],
  setup(props, { emit }) {
    const editor = ref(null)
    const isFocused = ref(false)
    const localContent = ref({
      text: '',
      max_score: 1,
      ...props.content
    })

    const onInput = () => {
      if (!editor.value) return
      
      // Save cursor position
      const selection = window.getSelection();
      let savedRange = null;
      
      if (selection.rangeCount > 0) {
        savedRange = selection.getRangeAt(0).cloneRange();
      }
      
      const html = editor.value.innerHTML
      localContent.value.text = html
      emit('update:content', { ...localContent.value })
      
      // Restore cursor position after a short delay to ensure DOM updates
      if (savedRange) {
        setTimeout(() => {
          try {
            selection.removeAllRanges();
            selection.addRange(savedRange);
          } catch (e) {
            console.error('Failed to restore cursor position after input:', e);
          }
        }, 0);
      }
    }

    const onKeyDown = (event) => {
      if (event.key === 'Enter') {
        const selection = window.getSelection()
        const range = selection.getRangeAt(0)
        const parentList = range.startContainer.parentElement.closest('ol, ul')

        if (parentList) {
          if (!event.shiftKey) {
            event.preventDefault()
            const listItem = range.startContainer.parentElement.closest('li')
            const isAtStartOfListItem = range.startOffset === 0

            if (isAtStartOfListItem) {
              const newListItem = document.createElement('li')
              listItem.parentNode.insertBefore(newListItem, listItem)
              selection.removeAllRanges()
              const newRange = document.createRange()
              newRange.selectNodeContents(newListItem)
              newRange.collapse(true)
              selection.addRange(newRange)
            } else if (listItem.textContent.trim() === '') {
              document.execCommand('outdent')
            } else {
              document.execCommand('insertHTML', false, '<li></li>')
            }
          }
        } else if (!event.shiftKey) {
          event.preventDefault()
          document.execCommand('insertLineBreak')
        }
      }
    }

    const onPaste = (event) => {
      event.preventDefault()
      const text = event.clipboardData.getData('text/plain')
      const html = event.clipboardData.getData('text/html')
      
      // Проверяем наличие изображений в буфере обмена
      if (event.clipboardData.files.length > 0) {
        const file = event.clipboardData.files[0]
        if (file.type.startsWith('image/')) {
          // Создаем временную ссылку для изображения
          const img = document.createElement('img')
          img.src = URL.createObjectURL(file)
          img.style.maxWidth = '100%'
          img.style.height = 'auto'
          
          const range = window.getSelection().getRangeAt(0)
          range.deleteContents()
          range.insertNode(img)
          return
        }
      }
      
      if (html) {
        const range = window.getSelection().getRangeAt(0)
        range.deleteContents()
        const div = document.createElement('div')
        div.innerHTML = html
        range.insertNode(div)
      } else {
        document.execCommand('insertText', false, text)
      }
    }

    const onSelectionChange = () => {
      if (!isFocused.value || !editor.value) return
      
      const selection = window.getSelection()
      if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0)
        
        // Check if selection is within our editor
        if (!editor.value.contains(range.commonAncestorContainer)) {
          return
        }
        
        // Fix empty selection with zero rect
        const rect = range.getBoundingClientRect()
        if (rect.top === 0 && rect.left === 0 && rect.width === 0 && rect.height === 0) {
          // Try to fix the range by moving it to a better position
          if (range.startContainer.nodeType === Node.TEXT_NODE) {
            // If we're in a text node, just reuse the same position
            range.setStart(range.startContainer, range.startOffset)
            range.setEnd(range.endContainer, range.endOffset)
          } else if (editor.value.firstChild) {
            // Otherwise try to position at the beginning of the editor
            range.setStart(editor.value.firstChild, 0)
            range.setEnd(editor.value.firstChild, 0)
          }
        }
      }
    }

    const onFocus = () => {
      isFocused.value = true
    }

    const onBlur = () => {
      isFocused.value = false
    }

    const formatText = (command, value = null) => {
      if (!editor.value) return
      document.execCommand(command, false, value)
      editor.value.focus()
    }

    const insertLink = (url) => {
      if (!editor.value) return
      const selection = window.getSelection()
      if (selection.toString()) {
        document.execCommand('createLink', false, url)
      } else {
        document.execCommand('insertText', false, url)
      }
      editor.value.focus()
    }

    watch(() => props.content, (newContent) => {
      localContent.value = {
        text: '',
        max_score: 1,
        ...newContent
      }
      
      if (editor.value && localContent.value.text) {
        // Only update the innerHTML if it's different to avoid cursor reset
        if (editor.value.innerHTML !== localContent.value.text) {
          // Save cursor position
          const selection = window.getSelection();
          let savedRange = null;
          let isEditorFocused = document.activeElement === editor.value;
          
          if (isEditorFocused && selection.rangeCount > 0) {
            savedRange = selection.getRangeAt(0).cloneRange();
          }
          
          // Update content
          editor.value.innerHTML = localContent.value.text;
          
          // Restore cursor position if editor was focused
          if (isEditorFocused && savedRange) {
            // Try to restore the cursor position
            try {
              selection.removeAllRanges();
              selection.addRange(savedRange);
            } catch (e) {
              console.error('Failed to restore cursor position:', e);
            }
          }
        }
      }
    }, { deep: true })

    onMounted(() => {
      if (editor.value) {
        editor.value.innerHTML = props.content.text || ''
      }
    })

    return {
      editor,
      localContent,
      onInput,
      onKeyDown,
      onPaste,
      onSelectionChange,
      onFocus,
      onBlur,
      formatText,
      insertLink
    }
  }
}
</script>

<style scoped>
.text-element {
  width: 100%;
  min-height: 100px;
  background: var(--form-background);
  border-radius: 8px;
  overflow: hidden;
  transition: background-color 0.3s ease;
  position: relative;
}

.formatting-toolbar {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  padding: 8px;
  background: var(--form-background);
  border-bottom: 1px solid var(--border-color);
  border-radius: 8px 8px 0 0;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.formatting-toolbar button {
  background: var(--form-background);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  transition: all 0.2s;
  color: var(--text-color);
}

.formatting-toolbar button:hover {
  background: var(--button-hover);
}

.formatting-toolbar button.active {
  background: var(--accent-color);
  color: #f5f9f8;
  border-color: var(--accent-color);
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--border-color);
  margin: 0 8px;
  transition: background-color 0.3s ease;
}

.icon-bold,
.icon-italic,
.icon-underline,
.icon-align-left,
.icon-align-center,
.icon-align-right,
.icon-ordered-list,
.icon-unordered-list {
  font-size: 14px;
  font-weight: 600;
}

.icon-bold { font-weight: 900; }
.icon-italic { font-style: italic; }
.icon-underline { text-decoration: underline; }

.text-editor {
  width: 100%;
  min-height: 100px;
  padding: 16px;
  font-family: 'Raleway', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-color);
  outline: none;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: var(--form-background);
  border-radius: 0 0 8px 8px;
  overflow-x: hidden;
  text-align: left;
  transition: color 0.3s ease, background-color 0.3s ease;
  max-width: 800px;
}

.text-editor:focus {
  outline: none;
  box-shadow: none;
}

.text-editor.read-only {
  background: var(--form-background);
  cursor: default;
}

.text-editor a {
  color: var(--accent-color);
  text-decoration: underline;
  transition: color 0.2s;
}

.text-editor a:hover {
  color: var(--text-color);
}

.text-editor p {
  margin: 0 0 1em;
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
}

.text-editor ul,
.text-editor ol {
  margin: 0 0 1em;
  padding-left: 2em;
  max-width: 100%;
}

.text-editor li {
  margin-bottom: 0.5em;
  overflow-wrap: break-word;
  word-wrap: break-word;
}

.text-editor li:last-child {
  margin-bottom: 0;
}

.text-editor blockquote {
  margin: 0 0 1em;
  padding-left: 1em;
  border-left: 4px solid var(--accent-color);
  color: var(--secondary-text);
  transition: color 0.3s ease, border-color 0.3s ease;
  max-width: 100%;
  overflow-wrap: break-word;
}

.text-editor code {
  font-family: monospace;
  background: var(--code-background);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
  white-space: pre-wrap;
  word-break: break-all;
}

.text-editor pre {
  background: var(--form-background);
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0 0 1em;
  border: 1px solid var(--border-color);
  transition: background-color 0.3s ease, border-color 0.3s ease;
  max-width: 100%;
  white-space: pre-wrap;
}

.text-editor pre code {
  background: none;
  padding: 0;
  border-radius: 0;
}

.text-editor img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 1em 0;
}

.text-editor table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.text-editor th,
.text-editor td {
  border: 1px solid var(--border-color);
  padding: 0.5em;
  text-align: left;
  transition: border-color 0.3s ease;
}

.text-editor th {
  background: var(--table-header);
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.text-editor hr {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 1em 0;
  transition: border-color 0.3s ease;
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

.score-success {
  color: #2e8b33;
  font-weight: 700;
}

.score-fail {
  color: var(--error-color, #da1f38);
  font-weight: 700;
}

:global(.dark-theme) .element-score-display {
  background: rgba(255, 255, 255, 0.08);
}

:global(.dark-theme) .score-success {
  color: #6bdb70;
}

:global(.dark-theme) .score-fail {
  color: #ff6b6b;
}
</style>