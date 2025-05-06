/**
 * Service for handling article content operations
 */
import api from '@/api';

// Content types mapping
const CONTENT_TYPES = {
  text: 'TEXT',
  image: 'IMAGE',
  video: 'VIDEO',
  code: 'CODE',
  quiz: 'QUIZ',
  table: 'TABLE',
  file: 'FILE',
  form: 'FORM',
};

// Default content templates
const DEFAULT_CONTENT = {
  text: { text: '', readOnly: false },
  image: { image: null, readOnly: false },
  video: { video_url: '', readOnly: false },
  code: { code: '', language: 'javascript', readOnly: false },
  quiz: { question: '', answers: ['', ''], correct_answer: null, readOnly: false },
  table: { headers: ['Заголовок 1', 'Заголовок 2'], data: [['', ''], ['', '']], readOnly: false },
  file: { file: null, filename: null, readOnly: false },
  form: { fields: [], readOnly: false },
};

// Generate unique ID for content items
const generateUniqueId = () => {
  return 'temp_' + Date.now() + '_' + Math.floor(Math.random() * 1000000);
};

export default {
  CONTENT_TYPES,
  DEFAULT_CONTENT,
  
  /**
   * Creates new content of specified type
   * @param {string} type - Content type
   * @param {number} order - Order in contents list
   * @returns {Object} New content object
   */
  createContent(type, order = 0) {
    if (!DEFAULT_CONTENT[type]) {
      throw new Error(`Unknown content type: ${type}`);
    }
    
    return {
      id: null,
      type,
      order: order,
      ...JSON.parse(JSON.stringify(DEFAULT_CONTENT[type])),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  },
  
  /**
   * Gets content type display name
   * @param {string} type - Content type 
   * @returns {string} Display name
   */
  getContentTypeName(type) {
    const types = {
      text: 'Текст',
      image: 'Изображение',
      video: 'Видео',
      code: 'Код',
      quiz: 'Тест',
      table: 'Таблица',
      file: 'Файл',
      form: 'Форма',
    };
    return types[type] || type;
  },
  
  /**
   * Creates a new empty article with default content
   * @param {Object} params - Article parameters
   * @param {string} params.title - Article title
   * @param {string} params.type - Article type
   * @returns {Object} New article data
   */
  createEmptyArticle(params = {}) {
    const title = params.title || 'Новая работа';
    
    // Create default text content
    const defaultContent = this.createContent('text');
    defaultContent.text = 'Добавьте содержимое здесь...';
    defaultContent.order = 1;
    
    return {
      contents: [defaultContent],
      originalContents: [JSON.parse(JSON.stringify(defaultContent))],
      isNew: true,
      error: null
    };
  },
  
  /**
   * Load article content from the backend
   * @param {Object} params - Route parameters
   * @param {number} params.courseSlug - Course slug
   * @param {number} params.moduleId - Module ID
   * @param {number} params.lessonId - Lesson ID
   * @returns {Promise} Promise resolving to content data
   */
  async loadArticle(params) {
    if (!params.courseSlug || !params.moduleId || !params.lessonId) {
      console.warn('Отсутствуют необходимые параметры (курс, модуль или урок).');
      return this.createEmptyArticle();
    }
    
    try {
      // Generate unique request URL for caching
      const contentRequestUrl = `/courses/${params.courseSlug}/modules/${params.moduleId}/lessons/${params.lessonId}/contents/`;
      
      // Load article contents
      const contentsResponse = await api.get(contentRequestUrl);
      const contents = contentsResponse.data
        .sort((a, b) => a.order - b.order)
        .map(item => ({
          ...item,
          filename: item.type === 'file' ? item.title : item.filename
        }));
        
      return {
        contents,
        originalContents: JSON.parse(JSON.stringify(contents)),
        error: null
      };
    } catch (error) {
      console.error('Error loading article:', error);
      
      let errorMessage = 'Ошибка загрузки содержимого. Попробуйте позже.';
      let createNew = false;
      
      if (error.response?.status === 404) {
        errorMessage = 'Урок не найден. Создаю новый пустой урок.';
        createNew = true;
      } else if (error.response?.status === 401) {
        errorMessage = 'Не авторизован. Пожалуйста, войдите в систему.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Доступ к уроку запрещён. Проверьте ваши права доступа.';
      }
      
      if (createNew) {
        console.info('Creating empty article due to 404 error');
        const emptyArticle = this.createEmptyArticle({
          title: params.title || 'Новая работа',
          type: params.type || 'article'
        });
        emptyArticle.message = errorMessage;
        return emptyArticle;
      }
      
      return {
        contents: [],
        originalContents: [],
        error: errorMessage
      };
    }
  },
  
  /**
   * Save article content and forms to the backend
   * @param {Object} data - Article data
   * @param {Array} data.contents - Content items
   * @param {Array} data.forms - Form items
   * @param {Object} params - Route parameters
   * @returns {Promise} Promise resolving to save results
   */
  async saveArticle(data, params) {
    const { contents, forms, lessonId, isNew, title, type } = data;
    const { courseSlug, moduleId } = params;
    
    try {
      // First, check if the lesson exists or needs to be created
      let actualLessonId = lessonId;
      
      if (isNew) {
        try {
          // Create the lesson first
          const lessonData = {
            title: title || 'Новая работа',
            description: '',
            module: moduleId,
            type: type || 'article'
          };
          
          const response = await api.post(`/courses/${courseSlug}/modules/${moduleId}/lessons/`, lessonData);
          
          // Update the lesson ID with the newly created lesson
          actualLessonId = response.data.id;
          console.info('Created new lesson with ID:', actualLessonId);
        } catch (error) {
          console.error('Failed to create new lesson:', error);
          return {
            success: false, 
            forms: forms,
            errors: ['Не удалось создать новый урок. ' + (error.message || '')]
          };
        }
      }
      
      // Step 1: Save form structure
      const formsToSave = forms.map(form => ({
        id: form.id,
        title: form.title || 'Новая форма',
        order: forms.indexOf(form) + 1,
        lesson: actualLessonId
      }));
      
      const formsResponse = await api.post(
        `/courses/${courseSlug}/modules/${moduleId}/lessons/${actualLessonId}/forms/batch/`,
        { forms: formsToSave }
      );
      
      // Update the form IDs with server-generated IDs
      const updatedForms = [...forms];
      if (formsResponse.data && formsResponse.data.forms) {
        formsResponse.data.forms.forEach((savedForm, index) => {
          if (index < updatedForms.length) {
            updatedForms[index].id = savedForm.id;
          }
        });
      }
      
      // Step 2: Process and save all form contents
      const contentPromises = [];
      const contentResults = [];
      
      for (const form of updatedForms) {
        for (const [contentIndex, content] of form.contents.entries()) {
          const isNewContent = !content.id;
          
          // Special handling for file uploads
          if ((content.type === 'file' && content.file instanceof File) || 
              (content.type === 'image' && content.image instanceof File)) {
            
            const formData = new FormData();
            formData.append('lesson', actualLessonId);
            formData.append('content_type', CONTENT_TYPES[content.type]);
            formData.append('order', contentIndex + 1);
            formData.append('form_id', form.id);
            
            if (content.type === 'file') {
              formData.append('file', content.file);
              if (content.filename) formData.append('title', content.filename);
            } else if (content.type === 'image') {
              formData.append('image', content.image);
            }
            
            const url = isNewContent
              ? `/courses/${courseSlug}/modules/${moduleId}/lessons/${actualLessonId}/contents/`
              : `/courses/${courseSlug}/modules/${moduleId}/lessons/${actualLessonId}/contents/${content.id}/`;
            
            try {
              const response = await fetch(`${api.defaults.baseURL}${url}`, {
                method: isNewContent ? 'POST' : 'PUT',
                body: formData,
                headers: {
                  'Authorization': `Token ${localStorage.getItem('auth_token')}`
                }
              });
              
              if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
              }
              
              const data = await response.json();
              contentResults.push({ 
                success: true, 
                data, 
                formIndex: updatedForms.indexOf(form), 
                contentIndex 
              });
            } catch (error) {
              contentResults.push({ 
                success: false, 
                error, 
                formIndex: updatedForms.indexOf(form), 
                contentIndex 
              });
            }
          } else {
            // Handle regular content (non-file)
            const payload = {
              lesson: actualLessonId,
              content_type: CONTENT_TYPES[content.type],
              order: contentIndex + 1,
              form_id: form.id
            };
            
            if (content.type === 'text') {
              payload.text = content.text || '';
            } else if (content.type === 'image' && typeof content.image === 'string') {
              payload.image = content.image;
            } else if (content.type === 'video') {
              payload.video_url = content.video_url || '';
            } else if (content.type === 'code') {
              payload.text = content.code || '';
              payload.code_language = content.language || 'javascript';
            } else if (content.type === 'quiz') {
              payload.quiz_data = {
                question: content.question || '',
                answers: content.answers || ['', ''],
                correct_answer: content.correct_answer
              };
            } else if (content.type === 'table') {
              payload.table_data = {
                headers: content.headers || ['Заголовок 1', 'Заголовок 2'],
                data: content.data || [['', ''], ['', '']]
              };
            } else if (content.type === 'file' && typeof content.file === 'string') {
              payload.file = content.file;
            }
            
            const url = isNewContent
              ? `/courses/${courseSlug}/modules/${moduleId}/lessons/${actualLessonId}/contents/`
              : `/courses/${courseSlug}/modules/${moduleId}/lessons/${actualLessonId}/contents/${content.id}/`;
              
            const method = isNewContent ? 'post' : 'put';
            
            try {
              const response = await api[method](url, payload);
              contentResults.push({ 
                success: true, 
                data: response.data, 
                formIndex: updatedForms.indexOf(form), 
                contentIndex 
              });
            } catch (error) {
              contentResults.push({ 
                success: false, 
                error, 
                formIndex: updatedForms.indexOf(form), 
                contentIndex 
              });
            }
          }
        }
      }
      
      // Process results
      const errors = contentResults
        .filter(result => !result.success)
        .map(result => {
          const { formIndex, contentIndex, error } = result;
          const content = updatedForms[formIndex].contents[contentIndex];
          const errorMessage = error?.response?.data?.detail || error?.message || 'Неизвестная ошибка';
          return `Форма ${formIndex + 1}, элемент ${contentIndex + 1} (${this.getContentTypeName(content.type)}): ${errorMessage}`;
        });
      
      // Update content IDs with server-generated IDs
      contentResults
        .filter(result => result.success)
        .forEach(result => {
          const { formIndex, contentIndex, data } = result;
          if (data && data.id) {
            updatedForms[formIndex].contents[contentIndex].id = data.id;
          }
          if (data && data.image && updatedForms[formIndex].contents[contentIndex].type === 'image') {
            updatedForms[formIndex].contents[contentIndex].image = data.image;
          }
          if (data && data.file && updatedForms[formIndex].contents[contentIndex].type === 'file') {
            updatedForms[formIndex].contents[contentIndex].file = data.file;
            updatedForms[formIndex].contents[contentIndex].filename = data.title || data.filename;
          }
        });
      
      // Invalidate cache after saving
      api.invalidateContentCache();
      
      return {
        success: errors.length === 0,
        forms: updatedForms,
        errors: errors,
        lessonId: isNew ? actualLessonId : null // Return the newly created lesson ID if this was a new lesson
      };
    } catch (error) {
      console.error('Error saving article:', error);
      return {
        success: false,
        forms: forms,
        errors: [error.message || 'Неизвестная ошибка при сохранении']
      };
    }
  },
  
  /**
   * Save forms to local storage (for offline or testing)
   * @param {number} lessonId - Lesson ID
   * @param {Array} forms - Forms to save
   * @returns {Object} Save result
   */
  saveFormsToLocalStorage(lessonId, forms) {
    try {
      // Deep clone to avoid reference issues
      const formsToSave = JSON.parse(JSON.stringify(forms));
      
      // Process each form to handle file uploads
      formsToSave.forEach(form => {
        // Ensure form has ID and title
        form.id = form.id || generateUniqueId();
        form.title = form.title || 'Новая форма';
        
        // Process each content item
        form.contents.forEach(content => {
          // Handle files
          if (content.type === 'file' && content.file instanceof File) {
            content.id = content.id || generateUniqueId();
            content.filename = content.file.name;
            content.file = URL.createObjectURL(content.file);
          } 
          // Handle images
          else if (content.type === 'image' && content.image instanceof File) {
            content.id = content.id || generateUniqueId();
            content.image = URL.createObjectURL(content.image);
          }
          // Generate ID for any content that doesn't have one
          else if (!content.id) {
            content.id = generateUniqueId();
          }
        });
      });
      
      // Save to localStorage
      localStorage.setItem(`article_forms_${lessonId}`, JSON.stringify(formsToSave));
      
      return {
        success: true,
        forms: formsToSave,
        errors: []
      };
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      return {
        success: false,
        forms: forms,
        errors: [error.message || 'Ошибка при сохранении в локальное хранилище']
      };
    }
  },
  
  /**
   * Load forms from local storage
   * @param {number} lessonId - Lesson ID 
   * @returns {Array} Forms from local storage or empty array
   */
  loadFormsFromLocalStorage(lessonId) {
    try {
      const savedForms = localStorage.getItem(`article_forms_${lessonId}`);
      if (savedForms) {
        return {
          forms: JSON.parse(savedForms),
          error: null
        };
      }
      return { forms: [], error: null };
    } catch (error) {
      console.error('Error loading from localStorage:', error);
      return { 
        forms: [], 
        error: 'Ошибка при загрузке из локального хранилища' 
      };
    }
  }
}; 