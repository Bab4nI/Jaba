<!-- html -->
<template>
    <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
      <router-view></router-view>
          <div class="netlab-ai-landing-page">
            <div class="course-details-container">
              <div class="course-details-section">
                <div class="course-details-section1">
                  <div class="course-description-container">
                    <p class="heading-primary">Обучающий курс «Администрирование вычислительных сетей»&nbsp;</p>
                    <p class="ai-support-heading">с поддержкой AI</p>
                  </div>
                  <div class="action-buttons-container">
                  </div>
                </div>
              </div>
              <div class="course-info-container1">
                <div class="course-info-container2">
                  <div class="course-features-container">
                    <div class="flex-column-container">
                      <img src="@/assets/images/flexible_8759203.png" class="interactive-assistant-card" />
                      <div class="flexible-accessible-container">
                        <p class="title-text-block">Гибкость и доступность</p>
                        <p class="flexible-accessible-text">Поддержка нескольких языков и переключение между светлым и темным режимами. Это делает платформу удобной для разных пользователей.</p>
                      </div>
                    </div>
                    <div class="interactive-assistant-section">
                      <div class="interactive-assistant-container">
                        <img src="@/assets/images/chatbot_10582024.png" class="interactive-assistant-card" />
                        <div class="flexible-accessible-container">
                          <p class="interactive-assistant-heading">Интерактивный ИИ-помощник</p>
                          <p class="flexible-accessible-text">Встроенный искусственный интеллект, который помогает с объяснением сложных понятий, решением задач и персонализированными рекомендациями по курсу.</p>
                        </div>
                      </div>
                      <div class="practical-focus-container">
                        <img src="@/assets/images/book_14142978.png" class="interactive-assistant-card" />
                        <div class="flexible-accessible-container">
                          <p class="practical-focus-heading">Практическая направленность</p>
                          <p class="flexible-accessible-text">Интеграция лабораторных заданий, тестов с мгновенной проверкой и удобной системой подачи файлов для проверки. Всё это помогает студентам не только изучать теорию, но и сразу применять знания.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="course-overview-container">
                    <div class="course-info-container">
                      <div class="course-topic-container"></div>
                      <p class="course-title-heading">О чём курс?</p>
                      <div class="course-description-box"></div>
                    </div>
                    <div class="content-wrapper">
                      <p class="central-text-block">Курс "Администрирование вычислительных сетей" — это путь от теории к практике в мире сетевых технологий. Вы научитесь не только понимать принципы работы сетей, но и уверенно управлять ими, диагностировать проблемы и обеспечивать безопасность.</p>
                      <img src="@/assets/images/info_img.png" class="featured-image-container" />
                    </div>
                  </div>
                </div>
                <div class="content-recommendation-section">
                  <div class="recommendation-container">
                    <p class="title-heading">Новости и объявления</p>
                    <div class="article-card-container">
                      <div v-if="news.length === 0" class="no-news-container">
                        <p class="no-news-text">Нет доступных новостей</p>
                      </div>
                      <div 
                        v-for="item in news" 
                        :key="item.id" 
                        class="article-container"
                        :style="getNewsItemStyle(item)"
                      >
                        <div class="article-content-container">
                          <p class="article-title-style">{{ item.title }}</p>
                          <p class="article-date">{{ formatDate(item.date) }}</p>
                          <p class="article-content">{{ item.content }}</p>
                          <div v-if="item.link" class="article-link-container">
                            <a :href="item.link" target="_blank" rel="noopener noreferrer" class="article-link-button">
                              Подробнее
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="recommendation-section">
                    <div class="feature-intro-container">
                      <div class="info-panel">
                        <p class="standout-heading">Заинтересовались?</p>
                        <div class="border-divider"></div>
                        <p class="centered-text-block">Присоединяйтесь к нашему обучающему курсу и откройте для себя мир сетевых технологий! Здесь вас ждут интерактивные лабораторные работы, поддержка ИИ-ассистента и возможность получить актуальные знания, востребованные на рынке труда.</p>
                      </div>
                      <div class="call-to-action-container">
                        <!-- PLACEHOLDER - Button Component detected here. Go to "React Code" via right click menu to see code generated -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <Footer />
          </div>
        </div>
    </template>
    
    
    <!-- js -->
    <script setup>
    import Footer from '@/components/Footer.vue';
    import { useNewsStore } from '@/stores/newsStore';
    import { computed } from 'vue';

    const newsStore = useNewsStore();
    const news = computed(() => newsStore.getRecentNews(3));

    // Format date for display
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    };

    const getNewsItemStyle = (item) => {
      if (item.imageUrl) {
        return { backgroundImage: `url(${item.imageUrl})`, backgroundSize: 'cover', backgroundPosition: 'center' };
      }
      return {};
    };
    </script>
    
    <!-- css -->
    <style scoped>
    
    .netlab-ai-landing-page {
        box-sizing: border-box;
        background: var(--background-color);
        transition: background-color 0.3s ease;
      }
      .center-column-flex-box {
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: center;
        width: 100%;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      }
      .header-section {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: row;
        gap: 8px;
        align-items: flex-end;
        justify-content: space-between;
        padding: 30px 29px 40px 99px;
        background: #f5f9f8;
      }
      .main-title-text-style {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        font: 400 36px Helvetica;
        color: var(--text-color);
        transition: color 0.3s ease;
      }
      .header-nav-container {
        display: flex;
        flex: 0 0 auto;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
      }
      .navigation-bar {
        display: flex;
        flex: 0 0 auto;
        flex-direction: row;
        gap: 29.5px;
        align-items: center;
        justify-content: flex-start;
      }
      .main-nav-container {
        flex: 0 0 auto;
        padding-top: 3.5px;
      }
      .main-heading-text-style {
        padding: 0;
        margin: 0;
        font: 400 20px Raleway, sans-serif;
        color: var(--text-color);
        transition: color 0.3s ease;
      }
      .main-heading-text-style:hover {
        text-decoration: underline;
        text-underline-offset: 5px;
      }
      .vertical-divider {
        box-sizing: border-box;
        flex: 0 0 auto;
        width: 1px;
        height: 29px;
        border-left: 1px solid var(--text-color);
        transition: border-color 0.3s ease;
      }
      .primary-text-content-style {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        font: 400 20px Raleway, sans-serif;
        color: #24222f;
      }
      .primary-text-content-style:hover {
        text-decoration: underline;
        text-underline-offset: 5px;
      }
    
      .main-logo {
        box-sizing: border-box;
        display: block;
        width: 42px;
        max-width: initial;
        height: 40px;
        margin-left: 58px;
        border: none;
        object-fit: cover;
      }
      .course-details-container {
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
      }
      .course-details-section {
        box-sizing: border-box;
        flex: 0 0 auto;
        max-width: initial;
        height: 627px;
        padding-right: 48px;
        padding-left: 99px;
        background: url("@/assets/images/main_page.png") 50% / cover no-repeat;
        border: none;
      }
      .course-details-section1 {
        box-sizing: border-box;
        max-width: 619px;
        padding-top: 216px;
        padding-bottom: 125px;
      }
      .course-description-container {
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: flex-start;
        width: 100%;
      }
      .heading-primary {
        flex: 0 0 auto;
        align-self: stretch;
        padding: 0;
        margin: 0;
        font: 700 40px Raleway, sans-serif;
        color: #f5f9f8;
        text-align: left;
        text-transform: uppercase;
      }
      .ai-support-heading {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        margin-top: 17px;
        font: 400 40px Raleway, sans-serif;
        color: #f5f9f8;
      }
      .action-buttons-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        padding-right: 123px;
        margin-top: 36px;
      }
      .detail-button {
        box-sizing: border-box;
        display: block;
        flex: 0 0 auto;
        width: 164px;
        min-width: 164px;
        height: 54px;
        font: italic 400 20px Raleway, sans-serif;
        color: #24222f;
        cursor: pointer;
        background: #c5c8cc;
        border: none;
        border-radius: 5px;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      }
      .primary-button-style {
        box-sizing: border-box;
        display: block;
        flex: 0 0 auto;
        width: 230px;
        min-width: 230px;
        height: 54px;
        margin-left: 20px;
        font: 700 20px Raleway, sans-serif;
        color: #f5f9f8;
        cursor: pointer;
        background: #3b3a4a;
        border: none;
        border-radius: 5px;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      }
      .course-info-container1 {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        padding-right: 31px;
        padding-left: 31px;
      }
      .course-info-container2 {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: flex-start;
        justify-content: flex-start;
        padding-top: 86px;
        padding-bottom: 70px;
        border-bottom: 2px solid #24222f;
      }
      .course-features-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: row;
        align-items: stretch;
        align-self: center;
        justify-content: flex-start;
        max-width: 1022px;
      }
      .flex-column-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 30.72%;
        padding-right: 15px;
        padding-bottom: 16px;
      }
      .interactive-assistant-card {
        box-sizing: border-box;
        display: block;
        flex: 0 0 auto;
        width: 137px;
        max-width: initial;
        height: 137px;
        border: none;
        object-fit: cover;
      }
      .flexible-accessible-container {
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: center;
        align-self: stretch;
        justify-content: flex-start;
        margin-top: 47px;
      }
      .title-text-block {
        box-sizing: border-box;
        flex: 0 0 auto;
        max-width: 185px;
        padding: 0;
        margin: 0;
        font: 900 24px Raleway, sans-serif;
        color: var(--text-color);
        text-align: center;
        transition: color 0.3s ease;
      }
      .flexible-accessible-text {
        flex: 0 0 auto;
        align-self: stretch;
        padding: 0;
        margin: 0;
        margin-top: 12px;
        font: 400 14px Raleway, sans-serif;
        color: var(--text-color);
        text-align: center;
        transition: color 0.3s ease;
      }
      .interactive-assistant-section {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: row;
        align-items: flex-start;
        justify-content: center;
        width: 69.28%;
        padding-left: 45px;
      }
      .interactive-assistant-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 1 293px;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
      }
      .interactive-assistant-heading {
        box-sizing: border-box;
        flex: 0 0 auto;
        max-width: 206px;
        padding: 0;
        margin: 0;
        font: 900 24px Raleway, sans-serif;
        color: var(--text-color);
        text-align: center;
        transition: color 0.3s ease;
      }
      .practical-focus-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 1 330px;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        margin-left: 40px;
      }
      .practical-focus-heading {
        box-sizing: border-box;
        flex: 0 0 auto;
        max-width: 212px;
        padding: 0;
        margin: 0;
        font: 900 24px Raleway, sans-serif;
        color: var(--text-color);
        text-align: center;
        transition: color 0.3s ease;
      }
      .course-overview-container {
        flex: 0 0 auto;
        margin-top: 92px;
      }
      .course-info-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
      }
      .course-topic-container {
        box-sizing: border-box;
        flex: 0 0 auto;
        width: 40%;
        border-top: 2px solid var(--text-color);
        transition: border-color 0.3s ease;
      }
      .course-title-heading {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        margin-left: 12px;
        font: 700 40px Raleway, sans-serif;
        color: var(--text-color);
        text-transform: uppercase;
        transition: color 0.3s ease;
      }
      .course-description-box {
        box-sizing: border-box;
        flex: 0 0 auto;
        width: 40%;
        margin-left: 15px;
        border-top: 2px solid var(--text-color);
        transition: border-color 0.3s ease;
      }
      .content-wrapper {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        padding-left: 90px;
        margin-top: 63px;
      }
      .central-text-block {
        box-sizing: border-box;
        flex: 0 1 auto;
        max-width: 400px;
        padding: 0;
        margin: 0;
        font: 400 20px Raleway, sans-serif;
        color: var(--text-color);
        text-align: center;
        transition: color 0.3s ease;
      }
      .featured-image-container {
        box-sizing: border-box;
        display: block;
        width: 667px;
        max-width: initial;
        height: 444px;
        margin-left: 123px;
        border: none;
        border-radius: 5px;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
        object-fit: cover;
      }
      .content-recommendation-section {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: stretch;
        justify-content: center;
        padding-top: 57px;
        padding-bottom: 95px;
      }
      .recommendation-container {
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        padding-right: 69px;
        padding-left: 69px;
      }
      .title-heading {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        font: 700 32px Raleway, sans-serif;
        color: var(--text-color);
        transition: color 0.3s ease;
      }
      .article-card-container {
        display: flex;
        flex: 0 0 auto;
        flex-direction: row;
        gap: 42px;
        align-items: flex-start;
        justify-content: space-between;
        margin-top: 44px;
      }
      .article-container {
        box-sizing: border-box;
        flex: 1 1 0;
        max-width: 398px;
        height: 235px;
        padding: 0;
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        background-color: var(--accent-color);
        transition: transform 0.3s ease;
        background-image: linear-gradient(to bottom right, var(--accent-color), var(--hover-accent));
      }
      .article-container:hover {
        transform: scale(1.02);
      }
      .article-container.news-item-1 {
        background: url("@/assets/images/article1.jpg") 50% / cover no-repeat;
      }
      .article-content-container {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 20px;
        background: rgba(0, 0, 0, 0.7);
        color: #f5f9f8;
      }
      .article-title-style {
        padding: 0;
        margin: 0;
        font: 700 20px Raleway, sans-serif;
        color: #f5f9f8;
      }
      .article-date {
        font: 400 14px Raleway, sans-serif;
        color: #cccccc;
        margin: 5px 0;
      }
      .article-content {
        box-sizing: border-box;
        width: 100%;
        padding: 0;
        margin: 8px 0;
        font: 400 14px Raleway, sans-serif;
        color: #f5f9f8;
        text-align: left;
        max-height: 60px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
      }
      .article-link-container {
        margin-top: 10px;
        text-align: right;
      }
      .article-link-button {
        display: inline-block;
        padding: 5px 15px;
        background: var(--accent-color);
        color: var(--footer-text);
        text-decoration: none;
        border-radius: 5px;
        font: 500 14px Raleway, sans-serif;
        transition: background-color 0.3s ease;
      }
      .article-link-button:hover {
        background: var(--hover-accent);
      }
      .recommendation-section {
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        margin-top: 96px;
      }
      .feature-intro-container {
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        max-width: 672px;
      }
      .info-panel {
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        gap: 19px;
        align-items: stretch;
        align-self: stretch;
        justify-content: flex-start;
      }
      .standout-heading {
        flex: 0 0 auto;
        align-self: center;
        padding: 0;
        margin: 0;
        font: 700 40px Raleway, sans-serif;
        color: var(--text-color);
        text-transform: uppercase;
        transition: color 0.3s ease;
      }
      .border-divider {
        flex: 0 0 auto;
        border-top: 2px solid var(--text-color);
        transition: border-color 0.3s ease;
      }
      .centered-text-block {
        flex: 0 0 auto;
        align-self: center;
        padding: 0;
        margin: 0;
        font: 400 20px Raleway, sans-serif;
        color: var(--text-color);
        text-align: center;
        transition: color 0.3s ease;
      }
      .call-to-action-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: stretch;
        justify-content: center;
        width: 205px;
        margin-top: 48px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.25);
      }
      .start-button {
        box-sizing: border-box;
        display: block;
        flex: 0 0 auto;
        min-width: 205px;
        height: 54px;
        font: 700 20px Raleway, sans-serif;
        color: #a094b8;
        cursor: pointer;
        background: transparent;
        border: 3px solid #a094b8;
        border-radius: 5px;
      }
      .team-contacts-section1,
      .team-contacts-section2,
      .team-contacts-section,
      .team-contact-details-container,
      .team-contacts-heading-style, 
      .team-contact-info-style,
      .contact-info-style,
      .contact-info-link,
      .line-height-reset,
      .partner-section,
      .partner-section1,
      .image-container,
      .copyright-notice-container,
      .center-aligned-copyright-text,
      .purple-heading {
        /* These styles are now in the Footer component */
        display: none;
      }
      .no-news-container {
        width: 100%;
        padding: 30px;
        text-align: center;
        background: var(--form-background);
        border-radius: 10px;
        transition: background-color 0.3s ease;
      }
      .no-news-text {
        font: 400 16px Raleway, sans-serif;
        color: var(--secondary-text);
        transition: color 0.3s ease;
      }
    </style>