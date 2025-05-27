<template>
  <div class="news-manager-container">
    <p class="news-heading">Управление новостями</p>
    
    <!-- Form to add/edit news -->
    <div class="news-form">
      <div class="form-field">
        <p class="form-field-label">Заголовок:</p>
        <input
          v-model="newsForm.title"
          type="text"
          class="form-input"
          placeholder="Введите заголовок новости"
        />
      </div>
      
      <div class="form-field">
        <p class="form-field-label">Содержание:</p>
        <textarea
          v-model="newsForm.content"
          class="form-textarea"
          placeholder="Введите содержание новости"
          rows="4"
        ></textarea>
      </div>
      
      <div class="form-field">
        <p class="form-field-label">Ссылка (URL):</p>
        <div class="url-input-container">
          <input
            v-model="newsForm.link"
            type="text"
            class="form-input"
            placeholder="Введите URL ссылки для статьи (необязательно)"
          />
        </div>
      </div>
      
      <div class="form-field">
        <p class="form-field-label">Изображение:</p>
        <div class="image-upload-options">
          <div class="image-option-section">
            <p class="image-option-label">Выберите изображение из шаблонов:</p>
            <div class="image-template-container">
              <div 
                v-for="image in defaultImages" 
                :key="image.id" 
                class="image-template-item"
                :class="{ 'selected': selectedTemplateId === image.id }"
                @click="selectDefaultImage(image.id)"
              >
                <img :src="image.url" :alt="image.name" class="image-template-thumbnail" />
                <p class="image-template-name">{{ image.name }}</p>
              </div>
            </div>
          </div>
          
          <div class="image-option-section">
            <p class="image-option-label">Или загрузите своё изображение:</p>
            <div class="image-upload-actions">
              <label for="image-upload" class="image-upload-label">
                <span>Выбрать файл с компьютера</span>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  class="image-upload-input"
                  @change="handleImageUpload"
                />
              </label>
              
              <div class="image-url-input">
                <p class="image-url-label">URL изображения:</p>
                <input
                  v-model="newsForm.imageUrl"
                  type="text"
                  class="form-input"
                  placeholder="Введите прямую ссылку на изображение"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="newsForm.imageUrl" class="image-preview-container">
          <div class="image-preview">
            <img :src="getImageUrl(newsForm.imageUrl)" alt="Предпросмотр" class="preview-image" />
          </div>
          <button class="remove-image-button" @click="removeImage">Удалить изображение</button>
        </div>
      </div>
      
      <div class="form-actions">
        <button 
          class="save-button" 
          @click="saveNews"
          :disabled="!isFormValid"
        >
          {{ editingNewsId ? 'Сохранить изменения' : 'Добавить новость' }}
        </button>
        
        <button 
          v-if="editingNewsId" 
          class="cancel-button" 
          @click="cancelEdit"
        >
          Отменить
        </button>
      </div>
    </div>
    
    <!-- List of existing news -->
    <div class="news-list">
      <h3 class="news-list-title">Существующие новости</h3>
      
      <div v-if="news.length === 0" class="empty-news">
        Нет добавленных новостей
      </div>
      
      <div v-for="item in sortedNews" :key="item.id" class="news-item">
        <div class="news-item-header">
          <h4 class="news-item-title">{{ item.title }}</h4>
          <div class="news-item-actions">
            <button class="edit-button" @click="editNews(item)">
              Редактировать
            </button>
            <button class="delete-button" @click="confirmDelete(item.id)">
              Удалить
            </button>
          </div>
        </div>
        <p class="news-item-date">{{ formatDate(item.date) }}</p>
        
        <div class="news-item-content-wrapper">
          <div v-if="item.image_url" class="news-item-image-container">
            <img :src="getImageUrl(item.image_url)" alt="Изображение новости" class="news-item-image" />
          </div>
          <div class="news-item-content">{{ item.content }}</div>
        </div>
        
        <div v-if="item.link" class="news-item-link">
          <a :href="item.link" target="_blank" rel="noopener noreferrer">{{ item.link }}</a>
        </div>
      </div>
    </div>

    <!-- Confirmation modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Подтверждение удаления</h3>
          <span class="close-btn" @click="showDeleteModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <p>Вы уверены, что хотите удалить эту новость?</p>
          <div class="modal-actions">
            <button class="delete-button" @click="deleteNews">Удалить</button>
            <button class="cancel-button" @click="showDeleteModal = false">Отмена</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useNewsStore } from '@/stores/newsStore';
import article1 from '@/assets/images/default_news/article1.jpg';
import article2 from '@/assets/images/default_news/article2.jpg';
import article3 from '@/assets/images/default_news/article3.jpg';

const newsStore = useNewsStore();
const news = computed(() => newsStore.news);
const sortedNews = computed(() => 
  [...news.value].sort((a, b) => new Date(b.date) - new Date(a.date))
);

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Form data
const newsForm = ref({
  title: '',
  content: '',
  imageUrl: '',
  link: ''
});

const editingNewsId = ref(null);
const showDeleteModal = ref(false);
const newsToDelete = ref(null);
const imageBase64 = ref('');
const selectedTemplateId = ref(null);
const isUploading = ref(false);

// Default news images
const defaultImages = [
  { 
    id: 1, 
    name: 'Статья 1', 
    url: article1 
  },
  { 
    id: 2, 
    name: 'Статья 2', 
    url: article2 
  },
  { 
    id: 3, 
    name: 'Статья 3', 
    url: article3 
  },
];

const isFormValid = computed(() => 
  newsForm.value.title.trim() !== '' && 
  newsForm.value.content.trim() !== ''
);

// Load news on component mount
onMounted(async () => {
  await newsStore.fetchNews();
});

// Format date for display
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Get full image URL
const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  
  // If it's already a full URL (starts with http or https), return as is
  if (imagePath.startsWith('http')) {
    return imagePath;
  }
  
  // If it's a Django media path (either starts with /media/ or is a relative path)
  if (imagePath.startsWith('/media/')) {
    return `${apiBaseUrl}${imagePath}`;
  } else {
    // Assume it's a relative media path
    return `${apiBaseUrl}/media/${imagePath}`;
  }
};

// Handle file upload for images
const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  try {
    const response = await newsStore.uploadImage(file);
    if (response.success && response.image_path) {
      newsForm.value.imageUrl = response.image_path;
      imageBase64.value = ''; // Clear base64 when using file upload
    } else {
      throw new Error('Failed to upload image');
    }
  } catch (error) {
    console.error('Error uploading image:', error);
    // You might want to show an error message to the user here
  }
};

// Select default image
const selectDefaultImage = async (id) => {
  try {
    selectedTemplateId.value = id;
    const selectedImage = defaultImages.find(image => image.id === id);
    if (selectedImage) {
      // Convert the imported image to a File object
      const response = await fetch(selectedImage.url);
      const blob = await response.blob();
      const file = new File([blob], `article${id}.jpg`, { type: 'image/jpeg' });
      
      // Upload the template image to the server
      const uploadResponse = await newsStore.uploadImage(file);
      if (uploadResponse.success && uploadResponse.image_path) {
        newsForm.value.imageUrl = uploadResponse.image_path;
        imageBase64.value = ''; // Clear base64 when using URL
      } else {
        throw new Error('Failed to upload template image');
      }
    }
  } catch (error) {
    console.error('Error handling template image:', error);
    selectedTemplateId.value = null;
    // You might want to show an error message to the user here
  }
};

// Remove selected image
const removeImage = () => {
  imageBase64.value = '';
  newsForm.value.imageUrl = '';
  selectedTemplateId.value = null;
};

// Save new news or update existing
const saveNews = async () => {
  if (!isFormValid.value) return;

  try {
    isUploading.value = true;
    let finalImageUrl = newsForm.value.imageUrl;

    // Если изображение не выбрано, используем случайное изображение по умолчанию
    if (!finalImageUrl) {
      const randomIndex = Math.floor(Math.random() * defaultImages.length);
      const defaultImage = defaultImages[randomIndex];
      
      // Конвертируем и загружаем изображение по умолчанию
      const response = await fetch(defaultImage.url);
      const blob = await response.blob();
      const file = new File([blob], `article${randomIndex + 1}.jpg`, { type: 'image/jpeg' });
      
      const uploadResponse = await newsStore.uploadImage(file);
      if (uploadResponse.success && uploadResponse.image_path) {
        finalImageUrl = uploadResponse.image_path;
      }
    }

    if (editingNewsId.value) {
      await newsStore.editNews(
        editingNewsId.value,
        newsForm.value.title,
        newsForm.value.content,
        finalImageUrl,
        newsForm.value.link
      );
    } else {
      await newsStore.addNews(
        newsForm.value.title,
        newsForm.value.content,
        finalImageUrl,
        newsForm.value.link
      );
    }
    
    // Reset form
    resetForm();
  } catch (error) {
    console.error('Error saving news:', error);
    // You might want to show an error message to the user here
  } finally {
    isUploading.value = false;
  }
};

// Edit news
const editNews = (newsItem) => {
  editingNewsId.value = newsItem.id;
  
  // Reset selected template
  selectedTemplateId.value = null;
  
  // Try to find if the current image URL matches one of our templates
  const matchingTemplate = defaultImages.find(image => image.url === newsItem.image_url);
  if (matchingTemplate) {
    selectedTemplateId.value = matchingTemplate.id;
  }
  
  newsForm.value = {
    title: newsItem.title,
    content: newsItem.content,
    imageUrl: newsItem.image_url || '',
    link: newsItem.link || ''
  };
};

// Cancel editing
const cancelEdit = () => {
  resetForm();
};

// Reset form
const resetForm = () => {
  newsForm.value = {
    title: '',
    content: '',
    imageUrl: '',
    link: ''
  };
  imageBase64.value = '';
  editingNewsId.value = null;
  selectedTemplateId.value = null;
};

// Show delete confirmation
const confirmDelete = (id) => {
  newsToDelete.value = id;
  showDeleteModal.value = true;
};

// Delete news
const deleteNews = async () => {
  if (newsToDelete.value) {
    try {
      await newsStore.deleteNews(newsToDelete.value);
      showDeleteModal.value = false;
      newsToDelete.value = null;
    } catch (error) {
      console.error('Error deleting news:', error);
      // You might want to show an error message to the user here
    }
  }
};

</script>

<style scoped>
.news-manager-container {
  box-sizing: border-box;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: var(--form-background);
  border-radius: 20px;
  transition: background-color 0.3s ease;
}

.news-heading {
  font: 600 24px Raleway, sans-serif;
  color: var(--text-color);
  text-align: center;
  margin-bottom: 30px;
  transition: color 0.3s ease;
}

.news-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: var(--background-color);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  margin-bottom: 30px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-field-label {
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.form-input, .form-textarea {
  padding: 10px;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  background: var(--form-background);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  outline: none;
  transition: all 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
  border-color: var(--accent-color);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.url-input-container {
  display: flex;
  gap: 10px;
}

.fetch-image-button {
  padding: 0 15px;
  background-color: var(--accent-color);
  color: var(--footer-text);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font: 500 14px Raleway, sans-serif;
  white-space: nowrap;
  transition: background-color 0.3s ease;
}

.fetch-image-button:hover:not(:disabled) {
  background-color: var(--hover-accent);
}

.fetch-image-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.image-upload-options {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-option-section {
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--background-color);
  transition: all 0.3s ease;
}

.image-option-label {
  font: 500 16px Raleway, sans-serif;
  color: var(--text-color);
  margin-top: 0;
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.image-upload-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.image-upload-label {
  display: inline-block;
  padding: 10px 15px;
  background-color: var(--accent-color);
  color: var(--footer-text);
  border-radius: 10px;
  cursor: pointer;
  text-align: center;
  font: 500 14px Raleway, sans-serif;
  transition: background-color 0.3s ease;
  width: 100%;
}

.image-upload-label:hover {
  background-color: var(--hover-accent);
}

.image-upload-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
}

.image-url-input {
  width: 100%;
}

.image-url-label {
  font: 400 14px Raleway, sans-serif;
  color: var(--secondary-text);
  margin-bottom: 5px;
  margin-top: 0;
  transition: color 0.3s ease;
}

.image-preview-container {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.image-preview {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
  max-width: 398px;
  height: 235px;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-button {
  background-color: var(--error-color);
  color: white;
  border: none;
  border-radius: 5px;
  padding: 8px 16px;
  cursor: pointer;
  font: 500 14px Raleway, sans-serif;
  align-self: flex-start;
  transition: background-color 0.3s ease;
}

.remove-image-button:hover {
  background-color: var(--hover-delete);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}

.save-button, .edit-button {
  padding: 8px 16px;
  font: 500 14px Raleway, sans-serif;
  color: var(--footer-text);
  background-color: var(--accent-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-button:hover, .edit-button:hover {
  background-color: var(--hover-accent);
}

.save-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.cancel-button {
  padding: 8px 16px;
  font: 500 14px Raleway, sans-serif;
  color: white;
  background-color: #757575;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background-color: #616161;
}

.delete-button {
  padding: 8px 16px;
  font: 500 14px Raleway, sans-serif;
  color: white;
  background-color: var(--error-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-button:hover {
  background-color: var(--hover-delete);
}

.news-list {
  padding: 20px;
  background: var(--background-color);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.news-list-title {
  font: 500 18px Raleway, sans-serif;
  color: var(--text-color);
  margin-top: 0;
  margin-bottom: 20px;
  transition: color 0.3s ease;
}

.empty-news {
  font: 400 16px Raleway, sans-serif;
  color: var(--secondary-text);
  text-align: center;
  padding: 20px;
  transition: color 0.3s ease;
}

.news-item {
  padding: 15px;
  background: var(--form-background);
  border-radius: 8px;
  margin-bottom: 15px;
  transition: background-color 0.3s ease;
}

.news-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.news-item-title {
  font: 500 18px Raleway, sans-serif;
  color: var(--text-color);
  margin: 0;
  transition: color 0.3s ease;
}

.news-item-actions {
  display: flex;
  gap: 8px;
}

.news-item-date {
  font: 400 14px Raleway, sans-serif;
  color: var(--secondary-text);
  margin: 0 0 10px 0;
  transition: color 0.3s ease;
}

.news-item-content-wrapper {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.news-item-image-container {
  width: 150px;
  height: 100px;
  flex-shrink: 0;
  border-radius: 5px;
  overflow: hidden;
}

.news-item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-item-content {
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  margin: 0;
  white-space: pre-line;
  transition: color 0.3s ease;
  flex: 1;
}

.news-item-link {
  margin-top: 10px;
  font-size: 14px;
}

.news-item-link a {
  color: var(--accent-color);
  text-decoration: none;
  word-break: break-all;
}

.news-item-link a:hover {
  text-decoration: underline;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--form-background);
  border-radius: 8px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.close-btn {
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: var(--text-color);
}

.modal-body {
  padding: 20px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.image-template-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.image-template-item {
  width: calc(33.333% - 7px);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-template-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.image-template-item.selected {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px var(--accent-color);
}

.image-template-thumbnail {
  width: 100%;
  height: 80px;
  object-fit: cover;
  display: block;
}

.image-template-name {
  padding: 5px;
  margin: 0;
  font: 400 12px Raleway, sans-serif;
  color: var(--text-color);
  text-align: center;
  background: var(--form-background);
  transition: color 0.3s ease, background-color 0.3s ease;
}
</style> 