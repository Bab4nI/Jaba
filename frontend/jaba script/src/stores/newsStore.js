import { defineStore } from 'pinia';

export const useNewsStore = defineStore('news', {
  state: () => {
    // Try to load news from localStorage, handle any potential errors
    let savedNews;
    let lastId = 1;
    
    try {
      savedNews = JSON.parse(localStorage.getItem('news'));
      lastId = parseInt(localStorage.getItem('lastNewsId')) || 1;
    } catch (e) {
      savedNews = null;
      console.error('Error loading news from localStorage:', e);
    }
    
    return {
      news: savedNews || [
        {
          id: 1,
          title: 'Добро пожаловать на курс!',
          content: 'Поздравляем с началом обучения! Здесь будут публиковаться важные новости и объявления.',
          date: new Date('2023-09-01').toISOString(),
          imageUrl: '',
          link: ''
        }
      ],
      lastId: lastId
    };
  },

  actions: {
    addNews(title, content, imageUrl = '', link = '') {
      const id = this.lastId + 1;
      this.news.push({
        id,
        title,
        content,
        date: new Date().toISOString(),
        imageUrl,
        link
      });
      this.lastId = id;
      this.saveNews();
      return id;
    },

    editNews(id, title, content, imageUrl = '', link = '') {
      const newsItem = this.news.find(item => item.id === id);
      if (newsItem) {
        newsItem.title = title;
        newsItem.content = content;
        newsItem.imageUrl = imageUrl;
        newsItem.link = link;
        this.saveNews();
        return true;
      }
      return false;
    },

    deleteNews(id) {
      const index = this.news.findIndex(item => item.id === id);
      if (index !== -1) {
        this.news.splice(index, 1);
        this.saveNews();
        return true;
      }
      return false;
    },

    saveNews() {
      try {
        // For images that are too large for localStorage, we could implement a compression
        // mechanism or upload to external storage. For now, we'll just save as is.
        localStorage.setItem('news', JSON.stringify(this.news));
        localStorage.setItem('lastNewsId', this.lastId.toString());
      } catch (e) {
        console.error('Error saving news to localStorage:', e);
        // If the error is because of localStorage size limits, we could show a warning to the user
        if (e.name === 'QuotaExceededError' || e.name === 'NS_ERROR_DOM_QUOTA_REACHED') {
          console.warn('LocalStorage quota exceeded. Some images may be too large to store locally.');
        }
      }
    },

    getRecentNews(count = 3) {
      return [...this.news]
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, count);
    },
  },
}); 