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
              <img :src="comment.author.avatar || defaultAvatarUrl" class="comment-avatar" alt="avatar" />
              <div class="comment-body">
                <div class="comment-header-row">
                  <span class="comment-author">{{ comment.author.username }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-text">{{ comment.text }}</div>
                <div class="comment-actions-row">
                  <button class="icon-btn" :class="{active: comment.current_user_reaction === 'LIKE'}" @click="likeComment(comment)">
                    <span class="heart-icon">❤</span> <span>{{ comment.likes_count }}</span>
                  </button>
                  <button class="reply-btn" @click="startReply(comment.id, comment.author.username, comment.id)">Ответить</button>
                  <button v-if="comment.replies && comment.replies.length > 0" class="toggle-replies-btn" @click="toggleReplies(comment.id)">
                    {{ comment.showReplies !== false ? 'Скрыть ответы' : `Показать ответы (${comment.replies.length})` }}
                    <span class="arrow">{{ comment.showReplies !== false ? '▲' : '▼' }}</span>
                  </button>
                  
                  <div class="menu-container">
                    <!-- Always visible debug button -->
                    <button class="more-btn" @click="toggleMenu(comment.id, $event)">
                      <span class="dots">...</span>
                    </button>
                    <div v-if="activeMenu === comment.id" class="actions-menu" @click.stop>
                      <button v-if="comment.is_author" class="action-btn edit-btn" @click="startEdit(comment); toggleMenu(null)">
                        <span class="action-icon">✎</span> Редактировать
                      </button>
                      <button v-if="comment.is_author" class="action-btn delete-btn" @click="deleteComment(comment); toggleMenu(null)">
                        <span class="action-icon">🗑</span> Удалить
                      </button>
                    </div>
                  </div>
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
                <!-- Редактирование комментария -->
                <div v-if="editingId === comment.id" class="edit-input-row">
                  <input
                    class="edit-input"
                    v-model="editText"
                    @keyup.enter="submitEdit(comment)"
                  />
                  <button class="send-edit-btn" @click="submitEdit(comment)" :disabled="!editText.trim()">Сохранить</button>
                  <button class="cancel-edit-btn" @click="cancelEdit()">Отмена</button>
                </div>
                <!-- Вложенные ответы -->
                <div v-if="comment.showReplies !== false && comment.replies && comment.replies.length > 0" class="replies-list">
                  <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                    <img :src="reply.author.avatar || defaultAvatarUrl" class="comment-avatar" alt="avatar" />
                    <div class="reply-body">
                      <div class="comment-header-row">
                        <span class="comment-author">{{ reply.author.username }}</span>
                        <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                      </div>
                      <div class="comment-text">{{ reply.text }}</div>
                      <div class="comment-actions-row">
                        <button class="icon-btn" :class="{active: reply.current_user_reaction === 'LIKE'}" @click="likeComment(reply)">
                          <span class="heart-icon">❤</span> <span>{{ reply.likes_count }}</span>
                        </button>
                        <button class="reply-btn" @click="startReply(comment.id, reply.author.username, reply.id)">Ответить</button>
                
                <div class="menu-container">
                  <!-- Always visible debug button for replies -->
                  <button class="more-btn" @click="toggleMenu(reply.id, $event)">
                    <span class="dots">...</span>
                  </button>
                  <div v-if="activeMenu === reply.id" class="actions-menu" @click.stop>
                    <button v-if="reply.is_author" class="action-btn edit-btn" @click="startEdit(reply); toggleMenu(null)">
                      <span class="action-icon">✎</span> Редактировать
                    </button>
                    <button v-if="reply.is_author" class="action-btn delete-btn" @click="deleteComment(reply); toggleMenu(null)">
                      <span class="action-icon">🗑</span> Удалить
                    </button>
                  </div>
                </div>
                      </div>
                      <!-- Редактирование ответа -->
                      <div v-if="editingId === reply.id" class="edit-input-row">
                        <input
                          class="edit-input"
                          v-model="editText"
                          @keyup.enter="submitEdit(reply)"
                        />
                        <button class="send-edit-btn" @click="submitEdit(reply)" :disabled="!editText.trim()">Сохранить</button>
                        <button class="cancel-edit-btn" @click="cancelEdit()">Отмена</button>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
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
    const editingId = ref(null)
    const editText = ref('')
    const activeMenu = ref(null)
    const replyToId = ref(null)

    const userAvatar = computed(() => {
      // First try to get avatar from user store
      if (userStore.avatarBase64) return userStore.avatarBase64;
      if (userStore.user?.avatar_base64) return userStore.user.avatar_base64;
      
      // If no avatar in store, use default avatar from assets
      return defaultAvatarUrl;
    })
    
    // Create a constant for the default avatar URL
    const defaultAvatarUrl = '/src/assets/images/default-avatar.png';

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

      return `/courses/${courseSlug.value}/modules/${moduleId.value}/lessons/${lessonId.value}/comments/`
    })

    // Initialize API with authentication
    const getAuthToken = () => {
      // Try to get token from auth store first, then from localStorage
      return authStore.accessToken || localStorage.getItem('access_token')
    }

    const api = axios.create({
      baseURL: 'http://localhost:8000/api',
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
        // First check if user is authenticated
        if (!userStore.user) {
          console.error('User not authenticated');
          alert('Необходима авторизация для оценки комментариев');
          return;
        }
        
        // Direct comments API endpoint
        const directUrl = `/comments/${comment.id}/reactions/`;
        
        console.log('Attempting to like comment with URL:', directUrl);
        console.log('Current user:', userStore.user);
        
        const wasLiked = comment.current_user_reaction === 'LIKE';
        
        // Optimistically update UI
        if (wasLiked) {
          comment.current_user_reaction = null;
          comment.likes_count = Math.max(0, comment.likes_count - 1);
        } else {
          comment.current_user_reaction = 'LIKE';
          comment.likes_count = (comment.likes_count || 0) + 1;
        }
        
        // Resort comments if needed
        if (sortType.value === 'popular') {
          sortComments();
        }
        
        try {
          if (wasLiked) {
            // Get all reactions for this comment
            const getResponse = await api.get(directUrl);
            console.log('Reactions:', getResponse.data);
            
            // Find the user's reaction by comparing email addresses
            // This is more reliable than comparing IDs which might be in different formats
            const userReaction = getResponse.data.find(r => 
              r.user && r.user.email === userStore.user.email
            );
            
            if (userReaction) {
              // Delete the specific reaction by ID
              console.log('Found reaction to delete:', userReaction.id);
              await api.delete(`/comments/${comment.id}/reactions/${userReaction.id}/`);
              console.log('Successfully deleted reaction');
            } else {
              // Alternative approach - try to delete by reaction type
              console.log('No reaction found to delete by email, trying direct delete');
              // Use a direct DELETE request to a custom endpoint
              await api.delete(`/comments/${comment.id}/user-reaction/`, {
                data: { user_id: userStore.user.id }
              });
              console.log('Successfully deleted reaction using direct method');
            }
          } else {
            // Create new reaction
            const response = await api.post(directUrl, { reaction_type: 'LIKE' });
            console.log('Successfully created reaction:', response.data);
          }
        } catch (apiError) {
          console.error('API error:', apiError);
          
          // Revert optimistic update on error
          if (wasLiked) {
            comment.current_user_reaction = 'LIKE';
            comment.likes_count = (comment.likes_count || 0) + 1;
          } else {
            comment.current_user_reaction = null;
            comment.likes_count = Math.max(0, comment.likes_count - 1);
          }
          
          if (sortType.value === 'popular') {
            sortComments();
          }
          
          // Refresh comments to ensure UI is in sync
          await loadComments();
        }
      } catch (err) {
        console.error('Error in like operation:', err);
        
        // Revert optimistic update on error
        if (comment.current_user_reaction === 'LIKE') {
          comment.current_user_reaction = null;
          comment.likes_count = Math.max(0, comment.likes_count - 1);
        } else {
          comment.current_user_reaction = 'LIKE';
          comment.likes_count = (comment.likes_count || 0) + 1;
        }
        
        // Resort comments if needed
        if (sortType.value === 'popular') {
          sortComments();
        }
      }
    }

    const toggleReplies = (id) => {
      const c = comments.value.find(c => c.id === id)
      if (c) c.showReplies = !c.showReplies
    }

    const startReply = (commentId, replyToUsername = null, replyToId = null) => {
      // Find which comment we're replying to (main comment or reply)
      let targetComment = comments.value.find(c => c.id === commentId);
      
      // If we're replying to a reply, we need to find its parent comment
      if (!targetComment) {
        // Look through all comments and their replies
        for (const comment of comments.value) {
          if (comment.replies) {
            const reply = comment.replies.find(r => r.id === commentId);
            if (reply) {
              // We found the reply, so we'll reply to the parent comment
              targetComment = comment;
              break;
            }
          }
        }
      }
      
      if (targetComment) {
        replyingId.value = targetComment.id;
        // Include the username in the reply text if provided
        replyText.value = replyToUsername ? `@${replyToUsername} ` : '';
        // Store the ID of the comment we're replying to (for UI reference only)
        replyToId.value = replyToId || null;
      }
    }

    const submitReply = async (commentId) => {
      if (!replyText.value.trim()) return;
      
      try {
        // Include any @username mentions in the text itself since we don't have a reply_to field
        const payload = {
          text: replyText.value,
          parent: commentId,
          comment_type: 'COMMENT',
          lesson: parseInt(lessonId.value)
        };
        
        const response = await api.post(apiUrl.value, payload);
        
        // Optimistically update UI
        const parentComment = comments.value.find(c => c.id === commentId);
        if (parentComment) {
          if (!parentComment.replies) parentComment.replies = [];
          parentComment.replies.unshift(response.data);
          parentComment.showReplies = true; // Ensure replies are visible
        }
        
        replyingId.value = null;
        replyText.value = '';
        replyToId.value = null;
      } catch (err) {
        console.error('Error submitting reply:', err);
        alert('Не удалось отправить ответ. Попробуйте позже.');
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
      // Force recomputation of sortedComments
      if (sortType.value === 'popular') {
        comments.value.sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0))
      } else if (sortType.value === 'new') {
        comments.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      } else if (sortType.value === 'old') {
        comments.value.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      }
    }

    const startEdit = (comment) => {
      editingId.value = comment.id
      editText.value = comment.text
    }

    const cancelEdit = () => {
      editingId.value = null
      editText.value = ''
    }

    const submitEdit = async (comment) => {
      if (!editText.value.trim()) return;
      
      // Store the original text before any changes
      const originalText = comment.text;
      
      try {
        // For both main comments and replies, use the direct API endpoint
        const url = `/comments/${comment.id}/`;
        
        console.log('Editing comment with URL:', url);
        
        // Optimistically update UI
        comment.text = editText.value;
        comment.is_edited = true;
        
        // Make API call with explicit token
        await api.patch(url, {
          text: editText.value
        });
        
        editingId.value = null;
        editText.value = '';
      } catch (err) {
        // Revert on error
        comment.text = originalText;
        
        console.error('Error editing comment:', err);
        alert('Не удалось отредактировать комментарий. Попробуйте позже.');
      }
    }

    const deleteComment = async (comment) => {
      if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) return;
      
      try {
        // For both main comments and replies, use the direct API endpoint
        const url = `/comments/${comment.id}/`;
        
        console.log('Deleting comment with URL:', url);
        
        // Optimistically update UI
        if (comment.parent) {
          // It's a reply - find parent and remove from replies
          const parentComment = comments.value.find(c => c.id === comment.parent);
          if (parentComment && parentComment.replies) {
            const index = parentComment.replies.findIndex(r => r.id === comment.id);
            if (index !== -1) {
              parentComment.replies.splice(index, 1);
            }
          }
        } else {
          // It's a main comment
          const index = comments.value.findIndex(c => c.id === comment.id);
          if (index !== -1) {
            comments.value.splice(index, 1);
          }
        }
        
        // Make API call
        await api.delete(url);
        
        console.log('Successfully deleted comment');
        
        activeMenu.value = null;
      } catch (err) {
        console.error('Error deleting comment:', err);
        // On error, reload comments
        await loadComments();
      }
    }

    // Function to check if user owns a comment
    const userOwnsComment = (comment) => {
      if (!comment) return false
      
      console.log('Checking ownership for comment:', comment.id, 'Author ID:', comment.author?.id, 'Current user ID:', userStore.user?.id)
      
      // First check if the API provided an is_author field
      if (comment.is_author !== undefined) {
        console.log('Using is_author field:', comment.is_author)
        return comment.is_author === true
      }
      
      // Fallback to comparing IDs
      if (!userStore.user || !comment.author) {
        console.log('Missing user or author data')
        return false
      }
      
      // Convert to strings for comparison to be safe
      const userId = String(userStore.user.id)
      const authorId = String(comment.author.id)
      
      const isOwner = userId === authorId
      console.log('ID comparison result:', isOwner, 'User ID:', userId, 'Author ID:', authorId)
      
      return isOwner
    }

    const toggleMenu = (id, event) => {
      if (event) {
        event.stopPropagation()
      }
      activeMenu.value = activeMenu.value === id ? null : id
    }

    // Close menu when clicking outside
    const handleOutsideClick = (event) => {
      if (activeMenu.value !== null && 
          !event.target.closest('.actions-dropdown') && 
          !event.target.classList.contains('more-btn')) {
        activeMenu.value = null
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleOutsideClick)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleOutsideClick)
    })

    watch([courseSlug, moduleId, lessonId], () => {
      loadComments()
    }, { immediate: true })

    return {
      userStore, authStore, userAvatar, comments, loading, error, newCommentText, activeTab,
      replyingId, replyText, sortType, sortedComments, editingId, editText, activeMenu,
      replyToId, addComment, likeComment, toggleReplies, startReply, submitReply, formatDate, sortComments,
      startEdit, cancelEdit, submitEdit, deleteComment, userOwnsComment, toggleMenu, defaultAvatarUrl
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
  transition: background 0.2s, transform 0.1s;
}
.add-comment-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.add-comment-btn:active {
  transform: translateY(0);
}
.add-comment-btn:disabled {
  background: #dab7e1;
  cursor: not-allowed;
  opacity: 0.7;
}
:root.dark-theme .add-comment-btn {
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
:root.dark-theme .add-comment-btn:disabled {
  background: #6d5a70;
  opacity: 0.5;
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
  position: relative;
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
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s, transform 0.15s;
}
.icon-btn:hover {
  color: var(--accent-color);
  background: var(--hover-background, #eafbe6);
}
.icon-btn:hover .heart-icon {
  transform: scale(1.1);
  color: #ff5c8d;
}
.icon-btn.active {
  transform: scale(1.05);
}
.heart-icon {
  transition: color 0.3s, transform 0.3s;
  font-size: 18px;
  position: relative;
  display: inline-block;
}
.icon-btn.active .heart-icon {
  color: transparent;
  background: linear-gradient(45deg, #ff3366, #ff5c8d, #ff85b3, #ff3366);
  background-size: 300% 300%;
  background-clip: text;
  -webkit-background-clip: text;
  animation: rgb-pulse 3s ease infinite;
  transform: scale(1.2);
  text-shadow: 0 0 5px rgba(255, 51, 102, 0.3);
}
.icon-btn.active .heart-icon::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  z-index: -1;
  background: radial-gradient(circle, rgba(255,51,102,0.2) 0%, rgba(255,51,102,0) 70%);
  animation: pulse-ring 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
}
@keyframes rgb-pulse {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
@keyframes pulse-ring {
  0% {
    transform: scale(0.8);
    opacity: 0.3;
  }
  80%, 100% {
    transform: scale(1.5);
    opacity: 0;
  }
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
  background: var(--button-bg, #f0f0f0);
  border: 1px solid var(--border-color, #ddd);
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  color: var(--secondary-text, #666);
  padding: 2px 10px;
  border-radius: 4px;
  transition: all 0.2s;
  letter-spacing: 2px;
  margin-left: 8px;
}
.more-btn:hover {
  background-color: var(--hover-background, #e0e0ff);
  color: var(--accent-color);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
.send-reply-btn, .send-edit-btn {
  background: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}
.send-reply-btn:hover, .send-edit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.send-reply-btn:disabled, .send-edit-btn:disabled {
  background: #dab7e1;
  cursor: not-allowed;
  opacity: 0.7;
}
.cancel-edit-btn {
  background: #f0f0f0;
  color: var(--text-color);
  border: none;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}
.cancel-edit-btn:hover {
  background: #e0e0e0;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
:root.dark-theme .cancel-edit-btn {
  background: #393552;
  color: var(--text-color);
}
:root.dark-theme .cancel-edit-btn:hover {
  background: #2a263d;
}
:root.dark-theme .send-reply-btn:disabled, 
:root.dark-theme .send-edit-btn:disabled {
  background: #6d5a70;
  opacity: 0.5;
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
:root.dark-theme .reply-input,
:root.dark-theme .edit-input {
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
.dots {
  display: inline-block;
  transform: translateY(-3px);
}
.actions-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 5px);
  background: var(--background-color, white);
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 1000;
  min-width: 180px;
  display: flex;
  flex-direction: column;
  padding: 5px 0;
  overflow: visible;
}
.action-btn {
  background: none;
  border: none;
  text-align: left;
  padding: 10px 15px;
  font-size: 14px;
  cursor: pointer;
  color: var(--text-color);
  transition: background 0.2s;
  display: flex;
  align-items: center;
}
.action-icon {
  margin-right: 10px;
  font-size: 16px;
}
.action-btn:hover {
  background-color: var(--hover-background, #f0f0ff);
}
.edit-btn {
  color: var(--accent-color);
}
.delete-btn {
  color: #ff3366;
}
.delete-btn:hover {
  background-color: rgba(255, 51, 102, 0.1);
}
.edit-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  margin-bottom: 8px;
}
.edit-input {
  flex: 1;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 7px 14px;
  font-size: 15px;
  outline: none;
  background: var(--background-color);
  color: var(--text-color);
}
.menu-container {
  position: relative;
  display: inline-block;
}

/* Dark theme overrides for heart icon */
:root.dark-theme .icon-btn.active .heart-icon {
  background: linear-gradient(45deg, #ff3366, #8c52ff, #5e9dff, #ff3366);
  background-size: 300% 300%;
  background-clip: text;
  -webkit-background-clip: text;
  animation: rgb-pulse 3s ease infinite;
  text-shadow: 0 0 8px rgba(255, 92, 141, 0.5);
}
:root.dark-theme .icon-btn:hover .heart-icon {
  color: #ff5c8d;
}
:root.dark-theme .icon-btn.active, 
:root.dark-theme .icon-btn:hover {
  background: rgba(255, 92, 141, 0.15);
}
:root.dark-theme .icon-btn.active .heart-icon::after {
  background: radial-gradient(circle, rgba(140,82,255,0.2) 0%, rgba(140,82,255,0) 70%);
}
:root.dark-theme .action-btn.edit-btn {
  color: var(--accent-color, #7cb342);
}
:root.dark-theme .action-btn.delete-btn {
  color: #ff5c8d;
}
:root.dark-theme .action-btn.delete-btn:hover {
  background-color: rgba(255, 92, 141, 0.15);
}
:root.dark-theme .more-btn {
  background: var(--button-bg, #2a263d);
  border-color: var(--border-color, #393552);
  color: var(--secondary-text, #b8b8b8);
}
:root.dark-theme .more-btn:hover {
  background-color: var(--hover-background, #393552);
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
</style>