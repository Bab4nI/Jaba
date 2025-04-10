<template>
  <div style="display: inline-block; width: 1480px; background: #f5f9f8">
    <div class="main-content-container">
      <div class="main-content-section">
        <div class="module-card-container">
          <div class="module-title-container">
            <div class="svg-container">
              <svg viewBox="0 0 24 24" x="0" y="0" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g id="Group 65" xmlns="http://www.w3.org/2000/svg">
                  <circle id="Ellipse 7" cx="11" cy="9.5" r="8" stroke="#575667" />
                  <line id="Line 12" x1="15.879999999999995" y1="15.675000000000011" x2="21.879999999999995" y2="22.67500000000001" stroke="#575667" />
                </g>
              </svg>
            </div>
            <input 
              v-model="searchQuery"
              class="article-title-text-style search-input" 
              placeholder="Поиск по модулям и работам"
              @input="searchModules"
            />
          </div>
          <button class="search-button" @click="searchModules">Поиск</button>
        </div>

        <div class="main-content-container1">
          <!-- Список модулей -->
          <div 
            v-for="(module, moduleIndex) in filteredModules" 
            :key="module.id" 
            class="module-container4"
          >
            <div class="save-button-container">
              <button class="save-button" @click="saveModule(moduleIndex)">Сохранить</button>
              <button class="delete-button" @click="deleteModule(moduleIndex)">Удалить</button>
            </div>
            <div class="module-container3">
              <div class="module-container2">
                <input 
                  v-model="module.title" 
                  class="module-title-style module-title-input"
                  placeholder="Название модуля"
                  @change="updateModuleTitle(moduleIndex, $event)"
                />
              </div>
              
              <!-- Список работ в модуле с flex-wrap (3 в ряд) -->
              <div class="articles-wrapper">
                <div 
                  v-for="(article, articleIndex) in module.articles" 
                  :key="article.id" 
                  class="article-card"
                >
                  <img 
                    class="article-thumbnail" 
                    :src="getImageUrl(article.image)" 
                  />
                  <div class="article-content">
                    <h3>{{ article.title }}</h3>
                    <p>{{ article.description }}</p>
                    <div class="article-meta">
                      <span>{{ formatDate(article.date) }}</span>
                      <span>{{ getTypeName(article.type) }}</span>
                      <div class="article-actions">
                        <button @click="editArticle(moduleIndex, articleIndex)"><img src="@/assets/images/pencil_4211918_1.png" /></button>
                        <button @click="deleteArticle(moduleIndex, articleIndex)"><img src="@/assets/images/delete_16596354_1.png" /></button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Кнопка добавления работы с изображением -->
                <div 
                  class="add-article-card" 
                  @click="addArticle(moduleIndex)"
                >
                  <img 
                    src="@/assets/images/image_5f285c02.png" 
                    class="add-article-image" 
                    alt="Добавить работу"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Кнопка добавления нового модуля -->
          <p 
            class="module-title-text-style add-module-btn" 
            @click="addModule"
          >
            + Добавить модуль
          </p>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для редактирования работы -->
    <div v-if="editingArticle" class="modal-overlay">
      <div class="modal-content">
        <h3>Редактирование работы</h3>
        <input v-model="editingArticle.title" placeholder="Название" />
        <textarea 
          v-model="editingArticle.description" 
          placeholder="Описание"
          class="fixed-textarea"
        ></textarea>
        <input type="date" v-model="editingArticle.date" />
        <select v-model="editingArticle.type">
          <option value="article">Статья</option>
          <option value="lab">Лабораторная</option>
          <option value="practice">Практика</option>
        </select>
        
        <!-- Поле для загрузки изображения -->
        <div class="image-upload-container">
          <label for="image-upload" class="image-upload-label">
            <span v-if="!editingArticle.image">Выберите изображение</span>
            <span v-else>Изменить изображение</span>
            <input 
              id="image-upload" 
              type="file" 
              accept="image/*" 
              @change="handleImageUpload"
              class="image-upload-input"
            />
          </label>
          <div v-if="editingArticle.image" class="image-preview">
            <img :src="getImageUrl(editingArticle.image)" class="preview-image" />
            <button @click="removeImage" class="remove-image-btn">×</button>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="saveEditedArticle">Сохранить</button>
          <button @click="cancelEdit">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import defaultImage from '@/assets/images/image_37e6f0fb.png';

export default {
  data() {
    return {
      searchQuery: '',
      modules: [],
      editingArticle: null,
      currentEditIndexes: { moduleIndex: null, articleIndex: null },
      nextId: 1
    }
  },
  computed: {
    filteredModules() {
      if (!this.searchQuery.trim()) return this.modules;
      
      const query = this.searchQuery.toLowerCase().trim();
      return this.modules.filter(module => {
        // Поиск по названию модуля
        if (module.title.toLowerCase().includes(query)) return true;
        
        // Поиск по работам в модуле
        return module.articles.some(article => 
          article.title.toLowerCase().includes(query) || 
          article.description.toLowerCase().includes(query) ||
          this.getTypeName(article.type).toLowerCase().includes(query)
        );
      }).map(module => {
        // Если есть поисковый запрос, показываем все работы в найденных модулях
        if (module.title.toLowerCase().includes(query)) {
          return module;
        }
        
        // Иначе фильтруем только работы, соответствующие запросу
        return {
          ...module,
          articles: module.articles.filter(article => 
            article.title.toLowerCase().includes(query) || 
            article.description.toLowerCase().includes(query) ||
            this.getTypeName(article.type).toLowerCase().includes(query))
        };
      });
    }
  },
  methods: {
    getImageUrl(imagePath) {
      if (!imagePath) return defaultImage;
      if (typeof imagePath === 'object' && imagePath instanceof File) {
        return URL.createObjectURL(imagePath);
      }
      try {
        // Попробуем загрузить изображение по переданному пути
        return require(`@/assets/${imagePath.replace('@\\', '')}`);
      } catch (e) {
        // Если не получилось, вернем изображение по умолчанию
        return defaultImage;
      }
    },
    generateId() {
      return this.nextId++;
    },
    getTypeName(type) {
      switch(type) {
        case 'article': return 'Статья';
        case 'lab': return 'Лабораторная';
        case 'practice': return 'Практика';
        default: return type;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    },
    addModule() {
      this.modules.push({
        id: this.generateId(),
        title: `Модуль ${this.modules.length + 1}`,
        articles: []
      });
    },
    updateModuleTitle(moduleIndex, event) {
      this.modules[moduleIndex].title = event.target.value;
    },
    deleteModule(index) {
      if (confirm('Удалить модуль и все его работы?')) {
        this.modules.splice(index, 1);
      }
    },
    saveModule(index) {
      alert(`Модуль "${this.modules[index].title}" сохранен`);
    },
    addArticle(moduleIndex) {
      this.modules[moduleIndex].articles.push({
        id: this.generateId(),
        title: 'Новая работа',
        description: 'Описание работы',
        date: new Date().toISOString().split('T')[0],
        type: 'article',
        image: null
      });
    },
    editArticle(moduleIndex, articleIndex) {
      this.currentEditIndexes = { moduleIndex, articleIndex };
      this.editingArticle = { ...this.modules[moduleIndex].articles[articleIndex] };
    },
    saveEditedArticle() {
      const { moduleIndex, articleIndex } = this.currentEditIndexes;
      this.modules[moduleIndex].articles[articleIndex] = { ...this.editingArticle };
      this.editingArticle = null;
    },
    cancelEdit() {
      this.editingArticle = null;
    },
    deleteArticle(moduleIndex, articleIndex) {
      if (confirm('Удалить эту работу?')) {
        this.modules[moduleIndex].articles.splice(articleIndex, 1);
      }
    },
    searchModules() {
      // Фильтрация выполняется автоматически через computed свойство filteredModules
      console.log('Выполнен поиск:', this.searchQuery);
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Сохраняем сам файл изображения
      this.editingArticle.image = file;
    },
    removeImage() {
      this.editingArticle.image = null;
    }
  },
  mounted() {
    // Инициализация тестовыми данными
    this.addModule();
    this.addModule();
    this.modules[0].articles = [
      {
        id: this.generateId(),
        title: 'Пример статьи',
        description: 'Это пример статьи в модуле',
        date: '2023-05-15',
        type: 'article',
        image: 'images/image_33f63252.jpeg'
      },
      {
        id: this.generateId(),
        title: 'Лабораторная работа 1',
        description: 'Основы программирования',
        date: '2023-05-20',
        type: 'lab',
        image: 'images/image_33f63252.jpeg'
      },
      {
        id: this.generateId(),
        title: 'Практическое задание 1',
        description: 'Введение в HTML',
        date: '2023-05-25',
        type: 'practice',
        image: 'images/image_33f63252.jpeg'
      }
    ];
    this.modules[1].articles = [
      {
        id: this.generateId(),
        title: 'Практическое задание 2',
        description: 'Работа с API',
        date: '2023-06-01',
        type: 'practice',
        image: 'images/image_33f63252.jpeg'
      },
      {
        id: this.generateId(),
        title: 'Лабораторная работа 2',
        description: 'Работа с CSS',
        date: '2023-06-05',
        type: 'lab',
        image: 'images/image_33f63252.jpeg'
      }
    ];
  }
}
</script>

<style scoped>
.main-content-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 1480px;
  max-width: 1480px;
  margin: 0 auto;
  overflow-x: hidden;
}
.main-content-section {
  box-sizing: border-box;
  width: 100%;
  max-width: 1480px;
  padding: 50px 20px 101px;
}
.module-card-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 88px;
  padding: 0 28px 0 29px;
  background: #ebefef;
  border-radius: 20px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
}
.module-title-container {
  box-sizing: border-box;
  display: flex;
  flex: 1;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  height: 43px;
  padding: 0 8.5px;
  background: #f5f9f8;
  border: 1px solid #c5c8cc;
  border-radius: 20px;
}
.svg-container {
  display: flex;
  flex: 0 0 auto;
  width: 24px;
  height: 24px;
}
.article-title-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  margin-left: 13.5px;
  font: 400 14px Raleway, sans-serif;
  color: #575667;
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
  margin-left: 13.5px;
}
.search-button {
  box-sizing: border-box;
  display: block;
  flex: 0 0 auto;
  width: 111px;
  min-width: 111px;
  height: 40px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 20px;
}
.main-content-container1 {
  box-sizing: border-box;
  width: 100%;
  margin-top: 66px;
}
.module-container4 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  width: 100%;
  margin-bottom: 40px;
}
.save-button-container {
  flex: 0 0 auto;
  align-self: flex-end;
  padding-right: 3px;
  padding-left: 3px;
  display: flex;
  gap: 10px;
}
.save-button {
  box-sizing: border-box;
  display: block;
  width: 137px;
  min-width: 137px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  cursor: pointer;
  background: #cff6c3;
  border: none;
  border-radius: 10px;
}
.delete-button {
  box-sizing: border-box;
  display: block;
  width: 100px;
  height: 44px;
  font: 400 16px Raleway, sans-serif;
  color: #fff;
  cursor: pointer;
  background: #ff6b6b;
  border: none;
  border-radius: 10px;
}
.module-container3 {
  flex: 0 0 auto;
  margin-top: 1px;
}
.module-container2 {
  display: flex;
  margin-left: 100px;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-start;
}
.module-title-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 24px Raleway, sans-serif;
  color: #24222f;
}
.module-title-input {
  background: transparent;
  border: none;
  outline: none;
  width: 100%;
  font: 400 24px Raleway, sans-serif;
  color: #24222f;
}

.articles-wrapper {
  display: flex;
  flex-wrap: wrap;
  margin: 100px;
  gap: 20px;
  margin-top: 20px;
}

.article-card {
  width: calc(33.333% - 14px); /* 3 карточки в ряд с учетом отступов */
  background: #ebefef;
  border-radius: 20px;
  padding: 20px;
  position: relative;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  min-height: 350px;
  box-sizing: border-box;
}

.article-thumbnail {
  width: 100%;
  height: 150px;
  object-fit: contain; /* Изображение масштабируется, чтобы полностью поместиться */
  border-radius: 10px;
  object-position: center; /* Центрируем изображение */
}

.article-content {
  margin-top: 15px;
}

.article-content h3 {
  margin: 0;
  padding: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}

.article-content p {
  margin: 7px 0 0 0;
  padding: 0;
  font: 300 14px Raleway, sans-serif;
  color: #575667;
  height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 7px;
  font: 400 12px Raleway, sans-serif;
  color: #a094b8;
}

.article-actions {
  display: flex;
  gap: 5px;
}

.article-actions button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin: 0;
}

.article-actions button img {
  width: 20px;
  height: 20px;
}

.add-article-card {
  width: calc(33.333% - 14px);
  background: #ebefef;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 350px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  padding: 20px;
  transition: background 0.3s;
  box-sizing: border-box;
}

.add-article-card:hover {
  background: #dde3e2;
}

.add-article-image {
  width: 55px;
  height: 55px;
  object-fit: contain;
}

.add-module-btn {
  cursor: pointer;
  color: #a094b8;
  text-align: center;
  padding: 10px;
  border: 2px dashed #a094b8;
  border-radius: 10px;
  margin-top: 40px;
  transition: background 0.3s;
  font: 400 16px Raleway, sans-serif;
}

.add-module-btn:hover {
  background: #ebefef;
}

.fixed-textarea {
  resize: none;
  width: 100%;
  height: 100px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}

.modal-content input,
.modal-content textarea,
.modal-content select {
  width: 100%;
  margin-bottom: 15px;
  padding: 8px;
  border: 1px solid #c5c8cc;
  border-radius: 5px;
  font: 300 14px Raleway, sans-serif;
}

.modal-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font: 400 14px Raleway, sans-serif;
}

.modal-actions button:first-child {
  background: #a094b8;
  color: white;
}

.modal-actions button:last-child {
  background: #ff6b6b;
  color: white;
}

/* Стили для загрузки изображений */
.image-upload-container {
  margin-bottom: 15px;
}

.image-upload-label {
  display: inline-block;
  padding: 8px 16px;
  background: #a094b8;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font: 400 14px Raleway, sans-serif;
  margin-bottom: 10px;
}

.image-upload-input {
  display: none;
}

.image-preview {
  position: relative;
  margin-top: 10px;
}

.preview-image {
  max-width: 100%;
  max-height: 150px;
  border-radius: 5px;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}
</style>