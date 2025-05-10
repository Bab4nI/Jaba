<template>
  <div class="comments-root">
    <!-- Tabs and Sorting -->
    <div class="header-row">
      <div class="comments-tabs">
        <div :class="['tab', activeTab === 'comments' ? 'active' : '']" @click="activeTab = 'comments'">
          <span>{{ comments.length }}</span> Комментарии
        </div>
      </div>
      <!-- Сортировка -->
      <div class="comments-sort-row">
        <select id="sort-select" v-model="sortType" @change="sortComments">
          <option value="popular">Популярные</option>
          <option value="new">Новые</option>
          <option value="old">Старые</option>
          <option value="my">Мои</option>
        </select>
      </div>
    </div>

    <!-- Add comment -->
    <div v-if="activeTab === 'comments'" class="add-comment-block">
      <img :src="userAvatar" class="user-avatar" alt="avatar" />
      <input
        v-model="newCommentText"
        class="add-comment-input"
        placeholder="Оставить комментарий"
        @keyup.enter="addComment"
      />
      <button class="add-comment-btn" :disabled="!newCommentText.trim()" @click="addComment">Отправить</button>
    </div>

    <!-- Comments list -->
    <div v-if="activeTab === 'comments'" class="comments-list-block">
      <div v-if="loading" class="loading">Загрузка комментариев...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="sortedComments.length === 0" class="no-comments">Пока нет комментариев. Будьте первым!</div>
      <div v-else>
        <template v-for="comment in sortedComments" :key="comment.id">
          <div class="comment-item">
            <div class="comment-main-row">
              <img :src="comment.author.avatar || '/default-avatar.png'" class="comment-avatar" alt="avatar" />
              <div class="comment-body">
                <div class="comment-header-row">
                  <span class="comment-author">{{ comment.author.username }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-text">{{ comment.text }}</div>
                <div class="comment-actions-row">
                  <button class="icon-btn" :class="{active: comment.current_user_reaction === 'LIKE'}" @click="likeComment(comment)">
                    <span>👍</span> <span>{{ comment.likes_count }}</span>
                  </button>
                  <button class="icon-btn" :class="{active: comment.current_user_reaction === 'DISLIKE'}" @click="dislikeComment(comment)">
                    <span>👎</span> <span>{{ comment.dislikes_count }}</span>
                  </button>
                  <button class="reply-btn" @click="startReply(comment.id)">Ответить</button>
                  <button v-if="comment.replies && comment.replies.length > 0" class="toggle-replies-btn" @click="toggleReplies(comment.id)">
                    {{ comment.showReplies !== false ? 'Скрыть ответы' : `Показать ответы (${comment.replies.length})` }}
                    <span class="arrow">{{ comment.showReplies !== false ? '▲' : '▼' }}</span>
                  </button>
                  <span class="more-btn">...</span>
                </div>
                <!-- Ответить поле -->
                <div v-if="replyingId === comment.id" class="reply-input-row">
                  <input
                    class="reply-input"
                    v-model="replyText"
                    :placeholder="'@' + comment.author.username + ', напишите ответ...'"
                    @keyup.enter="submitReply(comment.id)"
                  />
                  <button class="send-reply-btn" @click="submitReply(comment.id)" :disabled="!replyText.trim()">Отправить</button>
                </div>
                <!-- Вложенные ответы -->
                <div v-if="comment.showReplies !== false && comment.replies && comment.replies.length > 0" class="replies-list">
                  <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                    <img :src="reply.author.avatar || '/default-avatar.png'" class="comment-avatar" alt="avatar" />
                    <div class="reply-body">
                      <div class="comment-header-row">
                        <span class="comment-author">{{ reply.author.username }}</span>
                        <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                      </div>
                      <div class="comment-text">{{ reply.text }}</div>
                      <div class="comment-actions-row">
                        <button class="icon-btn" :class="{active: reply.current_user_reaction === 'LIKE'}" @click="likeComment(reply)">
                          <span>👍</span> <span>{{ reply.likes_count }}</span>
                        </button>
                        <button class="icon-btn" :class="{active: reply.current_user_reaction === 'DISLIKE'}" @click="dislikeComment(reply)">
                          <span>👎</span> <span>{{ reply.dislikes_count }}</span>
                        </button>
                        <button class="reply-btn" @click="startReply(reply.id)">Ответить</button>
                        <span class="more-btn">...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
    <!-- Решения (заглушка) -->
    <div v-if="activeTab === 'solutions'" class="solutions-block">
      <div class="solutions-placeholder">Тут будут решения (заглушка)</div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useRefreshStore } from '@/stores/auth'
import axios from 'axios'

export default {
  name: 'Comments',
  setup() {
    const route = useRoute()
    const userStore = useUserStore()
    const authStore = useRefreshStore()
    const comments = ref([])
    const loading = ref(true)
    const error = ref(null)
    const newCommentText = ref('')
    const activeTab = ref('comments')
    const replyingId = ref(null)
    const replyText = ref('')
    const sortType = ref('popular')

    const userAvatar = computed(() => userStore.avatarBase64 || userStore.user?.avatar_base64 || '/default-avatar.png')
    const courseSlug = computed(() => route.params.courseSlug)
    const moduleId = computed(() => route.params.moduleId)
    const lessonId = computed(() => route.params.lessonId)

    const apiUrl = computed(() => {
      if (!courseSlug.value || !moduleId.value || !lessonId.value) {
        console.error('Missing route params:', { courseSlug: courseSlug.value, moduleId: moduleId.value, lessonId: lessonId.value })
        return null
      }

      // Validate parameters
      if (isNaN(parseInt(moduleId.value)) || isNaN(parseInt(lessonId.value))) {
        console.error('Invalid route params:', { moduleId: moduleId.value, lessonId: lessonId.value })
        return null
      }

      return `http://localhost:8000/api/courses/${courseSlug.value}/modules/${moduleId.value}/lessons/${lessonId.value}/comments/`
    })

    // Initialize API with authentication
    const getAuthToken = () => {
      // Try to get token from auth store first, then from localStorage
      return authStore.accessToken || localStorage.getItem('access_token')
    }

    const api = axios.create({
      headers: {
        'Content-Type': 'application/json'
      }
    })

    api.interceptors.request.use(
      (config) => {
        const token = getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        } else {
          console.error('No access token available for API request')
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    const loadComments = async () => {
      if (!apiUrl.value) {
        error.value = 'Missing required parameters'
        return
      }

      // Ensure we have a valid lesson ID
      if (!lessonId.value || isNaN(parseInt(lessonId.value))) {
        error.value = 'Invalid lesson ID'
        console.error('Invalid lesson ID:', lessonId.value)
        return
      }

      try {
        loading.value = true
        error.value = null
        console.log('Loading comments from:', apiUrl.value)
        const response = await api.get(apiUrl.value)
        comments.value = response.data
        comments.value.forEach(comment => {
          comment.showReplies = true
        })
      } catch (err) {
        if (err.response?.status === 401) {
          error.value = 'Необходима авторизация'
          // Try to refresh the token
          try {
            await authStore.refreshToken()
            // If successful, try loading comments again
            if (authStore.accessToken) {
              return loadComments()
            }
          } catch (refreshError) {
            console.error('Failed to refresh token:', refreshError)
          }
        } else {
          error.value = 'Не удалось загрузить комментарии. Попробуйте позже.'
        }
        console.error('Error loading comments:', err)
      } finally {
        loading.value = false
      }
    }

    const addComment = async () => {
      if (!newCommentText.value.trim() || !apiUrl.value) {
        return
      }

      // Ensure we have a valid lesson ID
      if (!lessonId.value || isNaN(parseInt(lessonId.value))) {
        alert('Invalid lesson ID')
        console.error('Invalid lesson ID:', lessonId.value)
        return
      }

      try {
        console.log('Adding comment to:', apiUrl.value)
        const response = await api.post(apiUrl.value, {
          text: newCommentText.value,
          comment_type: 'COMMENT',
          lesson: parseInt(lessonId.value)
        })
        comments.value.unshift(response.data)
        newCommentText.value = ''
      } catch (err) {
        if (err.response?.status === 401) {
          // Try to refresh the token
          try {
            await authStore.refreshToken()
            // If successful, try adding comment again
            if (authStore.accessToken) {
              return addComment()
            } else {
              alert('Необходима авторизация')
            }
          } catch (refreshError) {
            console.error('Failed to refresh token:', refreshError)
            alert('Необходима авторизация')
          }
        } else {
          alert('Не удалось добавить комментарий. Попробуйте позже.')
        }
        console.error('Error adding comment:', err)
      }
    }

    const likeComment = async (comment) => {
      try {
        const url = `${apiUrl.value}${comment.id}/reactions/`
        const reactionType = comment.current_user_reaction === 'LIKE' ? 'DISLIKE' : 'LIKE'
        await api.post(url, { reaction_type: reactionType })
        await loadComments()
      } catch (err) {
        if (err.response?.status === 401) {
          // Try to refresh the token
          try {
            await authStore.refreshToken()
            // If successful, try liking again
            if (authStore.accessToken) {
              return likeComment(comment)
            } else {
              alert('Необходима авторизация')
            }
          } catch (refreshError) {
            console.error('Failed to refresh token:', refreshError)
            alert('Необходима авторизация')
          }
        } else {
          alert('Не удалось поставить лайк. Попробуйте позже.')
        }
        console.error(err)
      }
    }

    const dislikeComment = async (comment) => {
      try {
        const url = `${apiUrl.value}${comment.id}/reactions/`
        const reactionType = comment.current_user_reaction === 'DISLIKE' ? 'LIKE' : 'DISLIKE'
        await api.post(url, { reaction_type: reactionType })
        await loadComments()
      } catch (err) {
        if (err.response?.status === 401) {
          // Try to refresh the token
          try {
            await authStore.refreshToken()
            // If successful, try disliking again
            if (authStore.accessToken) {
              return dislikeComment(comment)
            } else {
              alert('Необходима авторизация')
            }
          } catch (refreshError) {
            console.error('Failed to refresh token:', refreshError)
            alert('Необходима авторизация')
          }
        } else {
          alert('Не удалось поставить дизлайк. Попробуйте позже.')
        }
        console.error(err)
      }
    }

    const toggleReplies = (id) => {
      const c = comments.value.find(c => c.id === id)
      if (c) c.showReplies = !c.showReplies
    }

    const startReply = (id) => {
      replyingId.value = id
      replyText.value = ''
    }

    const submitReply = async (id) => {
      if (!replyText.value.trim()) return
      try {
        const response = await api.post(apiUrl.value, {
          text: replyText.value,
          parent: id,
          comment_type: 'COMMENT',
          lesson: parseInt(lessonId.value)
        })
        const parentComment = comments.value.find(c => c.id === id)
        if (parentComment) {
          if (!parentComment.replies) parentComment.replies = []
          parentComment.replies.push(response.data)
          parentComment.replies.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        }
        replyingId.value = null
        replyText.value = ''
      } catch (err) {
        if (err.response?.status === 401) {
          // Try to refresh the token
          try {
            await authStore.refreshToken()
            // If successful, try submitting reply again
            if (authStore.accessToken) {
              return submitReply(id)
            } else {
              alert('Необходима авторизация')
            }
          } catch (refreshError) {
            console.error('Failed to refresh token:', refreshError)
            alert('Необходима авторизация')
          }
        } else {
          alert('Не удалось отправить ответ. Попробуйте позже.')
        }
        console.error(err)
      }
    }

    const formatDate = (date) => {
      const d = new Date(date)
      const now = new Date()
      const diff = (now - d) / 1000
      if (diff < 60 * 60) return 'только что'
      if (diff < 60 * 60 * 24) return 'сегодня'
      const months = Math.floor(diff / (60 * 60 * 24 * 30))
      if (months < 1) return 'в этом месяце'
      if (months === 1) return 'месяц назад'
      if (months < 12) return `${months} месяцев назад`
      return 'в прошлом году'
    }

    const sortedComments = computed(() => {
      let arr = [...comments.value]
      if (sortType.value === 'popular') {
        arr.sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0))
      } else if (sortType.value === 'new') {
        arr.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      } else if (sortType.value === 'old') {
        arr.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      } else if (sortType.value === 'my') {
        arr = arr.filter(c => c.author.id === userStore.user?.id)
      }
      return arr
    })

    const sortComments = () => {
      // Trigger for recomputing sortedComments
    }

    watch([courseSlug, moduleId, lessonId], () => {
      loadComments()
    }, { immediate: true })

    return {
      userStore, authStore, userAvatar, comments, loading, error, newCommentText, activeTab,
      replyingId, replyText, sortType, sortedComments,
      addComment, likeComment, dislikeComment, toggleReplies, startReply, submitReply, formatDate, sortComments
    }
  }
}
</script>

<style scoped>
.comments-root {
  margin-top: 30px;
  padding: 24px 32px 32px 32px;
  background: var(--form-background);
  border-radius: 8px;
  border: 2px solid var(--border-color);
  box-sizing: border-box;
  transition: background-color 0.4s, border-color 0.4s, box-shadow 0.4s;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}
.comments-root:hover {
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.comments-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  gap: 2rem;
  font-size: 16px;
  font-weight: 500;
}
.tab {
  padding: 18px 0 10px 0;
  cursor: pointer;
  color: var(--secondary-text);
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.tab.active {
  color: var(--accent-color);
  border-bottom: 2px solid var(--accent-color);
  font-weight: 700;
}
.tab span {
  font-weight: 700;
  font-size: 18px;
}
.comments-sort-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: var(--secondary-text);
}
.comments-sort-row select {
  border-radius: 20px;
  border: 1px solid var(--border-color);
  background: var(--background-color);
  color: var(--text-color);
  padding: 8px 16px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}
.comments-sort-row select:hover {
  background-color: var(--hover-background, #f0f0ff);
  border-color: var(--accent-color);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.comments-sort-row select:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(24, 119, 242, 0.2);
}
.comments-warning {
  background: var(--background-color);
  color: var(--secondary-text);
  font-size: 15px;
  border-radius: 4px;
  margin: 0 0 18px 0;
  padding: 12px 18px;
  border-left: 3px solid var(--accent-color);
}
.add-comment-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 0 0 0;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}
.add-comment-input {
  flex: 1;
  border: none;
  background: var(--background-color);
  border-radius: 18px;
  padding: 10px 16px;
  font-size: 15px;
  color: var(--text-color);
  outline: none;
  margin-right: 8px;
  transition: box-shadow 0.2s;
}
.add-comment-input:focus {
  box-shadow: 0 0 0 2px var(--accent-color);
}
.add-comment-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 18px;
  padding: 8px 18px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.add-comment-btn:disabled {
  background: #b7e1b7;
  cursor: not-allowed;
}
.comments-list-block {
  margin: 0;
}
.loading, .error, .no-comments {
  color: var(--secondary-text);
  text-align: center;
  padding: 32px 0;
}
.comment-item {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}
.comment-main-row {
  display: flex;
  align-items: flex-start;
}
.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 12px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
}
.comment-body {
  flex: 1;
}
.comment-header-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  margin-bottom: 2px;
}
.comment-author {
  font-weight: 700;
  color: var(--text-color);
}
.comment-date {
  color: var(--secondary-text);
  font-size: 13px;
}
.comment-text {
  font-size: 15px;
  color: var(--text-color);
  margin-bottom: 6px;
  word-break: break-word;
}
.comment-actions-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--secondary-text);
}
.icon-btn {
  background: none;
  border: none;
  color: var(--secondary-text);
  cursor: pointer;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 0 4px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}
.icon-btn.active, .icon-btn:hover {
  color: var(--accent-color);
  background: var(--hover-background, #eafbe6);
}
.reply-btn {
  color: var(--accent-color);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  padding: 0 4px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}
.reply-btn:hover {
  background: var(--hover-background, #f0f0ff);
  color: var(--accent-color);
}
.toggle-replies-btn {
  color: var(--accent-color);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0 4px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}
.toggle-replies-btn:hover {
  background: var(--hover-background, #f0f0ff);
  color: var(--accent-color);
}
.arrow {
  font-size: 12px;
  margin-left: 2px;
}
.more-btn {
  color: #bbb;
  font-size: 20px;
  margin-left: 8px;
  cursor: pointer;
}
.reply-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.reply-input {
  flex: 1;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 7px 14px;
  font-size: 15px;
  outline: none;
  background: var(--background-color);
  color: var(--text-color);
}
.send-reply-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.send-reply-btn:disabled {
  background: #b7e1b7;
  cursor: not-allowed;
}
.replies-list {
  margin-top: 10px;
  margin-left: 48px;
  border-left: 2px solid var(--border-color);
  padding-left: 16px;
}
.reply-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}
.reply-body {
  flex: 1;
}
.solutions-block {
  padding: 32px;
  color: var(--secondary-text);
  text-align: center;
}

/* Темная тема */
:root.dark-theme .comments-root {
  background: var(--form-background, #232136);
  border-color: var(--border-color, #393552);
}
:root.dark-theme .comments-warning {
  background: var(--background-color, #232136);
  color: var(--secondary-text, #b8b8b8);
}
:root.dark-theme .add-comment-input,
:root.dark-theme .reply-input {
  background: var(--background-color, #232136);
  color: var(--text-color, #fff);
}
:root.dark-theme .comment-avatar {
  background: var(--background-color, #232136);
  border-color: var(--border-color, #393552);
}
:root.dark-theme .comment-item {
  border-bottom: 1px solid var(--border-color, #393552);
}
:root.dark-theme .replies-list {
  border-left: 2px solid var(--border-color, #393552);
}
:root.dark-theme .comments-sort-row select {
  background-color: var(--background-color, #232136);
  color: var(--text-color, #fff);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23b8b8b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
}
:root.dark-theme .comments-sort-row select:hover {
  background-color: var(--hover-background, #2a263d);
}
</style>