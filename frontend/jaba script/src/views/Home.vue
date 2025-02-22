<!-- html -->
<template>
    <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
      <router-view></router-view>
          <div class="netlab-ai-landing-page">
            <div class="center-column-flex-box">
              <div class="header-section">
                <p class="main-title-text-style">NetLab AI</p>
                <div class="header-nav-container">
                  <div class="navigation-bar">
                    <div class="main-nav-container">
                      <p class="main-heading-text-style">
                        <router-link :to="header.home.link">{{ header.home.title }}</router-link>
                      </p>
                      <div class="main-section-border"></div>
                    </div>
                    <div class="vertical-divider"></div>
                    <p class="primary-text-content-style">
                      <router-link :to="header.course.link">{{ header.course.title }}</router-link>
                    </p>
                    <div class="vertical-divider"></div>
                    <p class="primary-text-content-style">
                      <router-link :to="header.login.link">{{ header.login.title }}</router-link>
                    </p>
                  </div>
                  <img src="@/assets/images/moon_5370735.png" class="main-logo" />
                </div>
              </div>
            </div>
            <div class="course-details-container">
              <div class="course-details-section">
                <div class="course-details-section1">
                  <div class="course-description-container">
                    <p class="heading-primary">Обучающий курс «Администрирование вычислительных сетей»&nbsp;</p>
                    <p class="ai-support-heading">с поддержкой AI</p>
                  </div>
                  <div class="action-buttons-container">
                    <!-- PLACEHOLDER - Button Component detected here. Go to "React Code" via right click menu to see code generated -->
                    <!-- PLACEHOLDER - Button Component detected here. Go to "React Code" via right click menu to see code generated -->
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
                      <p class="central-text-block">Lorem ipsum dolor, sit amet consectetur adipisicing elit. Pariatur saepe nihil, fugit nemo in, cumque magni obcaecati explicabo ipsa omnis assumenda, numquam ut repudiandae? Qui eligendi impedit dolorem. Quos, quisquam.</p>
                      <img src="@/assets/images/info_img.png" class="featured-image-container" />
                    </div>
                  </div>
                </div>
                <div class="content-recommendation-section">
                  <div class="recommendation-container">
                    <p class="title-heading">Рекомендации для Вас</p>
                    <div class="article-card-container">
                      <div class="article-container1">
                        <p class="article-title-style">Название статьи</p>
                        <p class="article-content">Lorem ipsum dolor, sit amet consectetur adipisicing elit. Pariatur saepe nihil, fugit nemo in, cumque magni obcaecati explicabo ipsa omnis assumenda, numquam ut repudiandae? Qui eligendi impedit dolorem. Quos, quisquam.</p>
                      </div>
                      <div class="article-container">
                        <p class="article-title-style">Название статьи</p>
                        <p class="article-content">Lorem ipsum dolor, sit amet consectetur adipisicing elit. Pariatur saepe nihil, fugit nemo in, cumque magni obcaecati explicabo ipsa omnis assumenda, numquam ut repudiandae? Qui eligendi impedit dolorem. Quos, quisquam.</p>
                      </div>
                      <div class="article-container2">
                        <p class="article-title-style">Название статьи</p>
                        <p class="article-content">Lorem ipsum dolor, sit amet consectetur adipisicing elit. Pariatur saepe nihil, fugit nemo in, cumque magni obcaecati explicabo ipsa omnis assumenda, numquam ut repudiandae? Qui eligendi impedit dolorem. Quos, quisquam.</p>
                      </div>
                    </div>
                  </div>
                  <div class="recommendation-section">
                    <div class="feature-intro-container">
                      <div class="info-panel">
                        <p class="standout-heading">Заинтересовались?</p>
                        <div class="border-divider"></div>
                        <p class="centered-text-block">Lorem ipsum dolor, sit amet consectetur adipisicing elit. Pariatur saepe nihil, fugit nemo in, cumque magni obcaecati explicabo ipsa omnis assumenda, numquam ut repudiandae? Qui eligendi impedit dolorem. Quos, quisquam.</p>
                      </div>
                      <div class="call-to-action-container">
                        <!-- PLACEHOLDER - Button Component detected here. Go to "React Code" via right click menu to see code generated -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="team-contacts-section1">
              <div class="team-contacts-section2">
                <div class="team-contacts-section">
                  <div class="team-contact-details-container">
                    <p class="team-contacts-heading-style">Контакты команды</p>
                    <p class="team-contact-info-style">
                      <span class="contact-info-style">Email: </span>
                      <a href="mailto:team@example.com" class="contact-info-link">jabascript@sfedu.com</a>
                      <span class="line-height-reset"><br /></span>

                      <span class="contact-info-style">Телефон: </span>
                      <a href="tel:+1234567890" class="contact-info-link">+7(938)-100-16-77</a>
                      <span class="line-height-reset"><br /></span>

                      <span class="contact-info-style">Адрес: </span>
                      <a href="https://yandex.ru/maps/?text=пер.%20Некрасовский,%2044,%20Таганрог" target="_blank" class="contact-info-link">
                          пер. Некрасовский, 44, г. Таганрог
                      </a>
                    </p>
                  </div>
                  <div class="partner-section">
                    <p class="team-contacts-heading-style">Партнёры</p>
                    <div class="partner-section1">
                      <a href="https://vk.com/ictis_sfedu" target="_blank"><img src="@/assets/images/ictis.png" class="image-container" /></a>
                    </div>
                  </div>
                </div>
              </div>
              <div class="copyright-notice-container">
                <div class="center-aligned-copyright-text">
                  <p class="purple-heading">© 2024 NetLab AI. Все права защищены.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
    </template>
    
    
    
    
    <!-- js -->
    <script setup>
    import { ref, reactive } from 'vue';
    import { useRouter } from 'vue-router';
    import { header } from '@/config/header.js';
    
    const router = useRouter();
    const goToSignin = () => {
      router.push('header.login.link');
    };
    
    </script>
    
    
    
    <!-- css -->
    <style scoped>
    
    .netlab-ai-landing-page {
        box-sizing: border-box;
        background: #f5f9f8;
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
        color: #24222f;
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
        color: #24222f;
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
        border-left: 1px solid #24222f;
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
        color: #24222f;
        text-align: center;
      }
      .flexible-accessible-text {
        flex: 0 0 auto;
        align-self: stretch;
        padding: 0;
        margin: 0;
        margin-top: 12px;
        font: 400 14px Raleway, sans-serif;
        color: #24222f;
        text-align: center;
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
        color: #24222f;
        text-align: center;
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
        color: #24222f;
        text-align: center;
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
        border-top: 2px solid #24222f;
      }
      .course-title-heading {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        margin-left: 12px;
        font: 700 40px Raleway, sans-serif;
        color: #24222f;
        text-transform: uppercase;
      }
      .course-description-box {
        box-sizing: border-box;
        flex: 0 0 auto;
        width: 40%;
        margin-left: 15px;
        border-top: 2px solid #24222f;
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
        color: #24222f;
        text-align: center;
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
        color: #24222f;
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
      .article-container1 {
        box-sizing: border-box;
        flex: 1 1 0;
        max-width: 398px;
        padding: 118px 31px 35px;
        background: url("@/assets/images/article1.jpg") 50% / cover no-repeat;
      }
      .article-title-style {
        padding: 0;
        margin: 0;
        font: 700 20px Raleway, sans-serif;
        color: #f5f9f8;
      }
      .article-content {
        box-sizing: border-box;
        width: 100%;
        padding: 0;
        margin: 0;
        margin-top: 23.5px;
        font: 400 14px Raleway, sans-serif;
        color: #f5f9f8;
        text-align: left;
      }
      .article-container {
        box-sizing: border-box;
        flex: 1 1 0;
        max-width: 398px;
        padding: 118px 31px 35px;
        background: url("@/assets/images/article2.jpg") 50% / cover no-repeat;
      }
      .article-container2 {
        box-sizing: border-box;
        flex: 1 1 0;
        max-width: 398px;
        padding: 118px 31px 35px;
        background: url("@/assets/images/article3.jpg") 50% / cover no-repeat;
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
        color: #24222f;
        text-transform: uppercase;
      }
      .border-divider {
        flex: 0 0 auto;
        border-top: 2px solid #24222f;
      }
      .centered-text-block {
        flex: 0 0 auto;
        align-self: center;
        padding: 0;
        margin: 0;
        font: 400 20px Raleway, sans-serif;
        color: #24222f;
        text-align: center;
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
      .team-contacts-section1 {
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        width: 100%;
        padding-right: 20.5px;
        padding-left: 19.5px;
        background: #575667;
      }
      .team-contacts-section2 {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        border-bottom: 1px solid #a094b8;
      }
      .team-contacts-section {
        box-sizing: border-box;
        display: flex;
        flex-direction: row;
        gap: 8px;
        align-items: flex-start;
        justify-content: space-between;
        min-width: 1282px;
        padding-top: 45px;
        padding-bottom: 61px;
      }
      .team-contact-details-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: stretch;
        justify-content: center;
        max-width: 357px;
      }
      .team-contacts-heading-style {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        font: 700 18px Raleway, sans-serif;
        color: #f5f9f8;
      }
      .team-contact-info-style {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        margin-top: 32px;
        color: #a094b8;
        text-align: left;
      }
      .contact-info-style {
        font: 400 18px Raleway, sans-serif;
        text-align: left;
      }
      .contact-info-link {
        font: 400 18px Raleway, sans-serif;
        color: #a094b8;
        text-align: left;
        text-decoration-line: underline;
        text-underline-offset: 5px;
      }
      .line-height-reset {
        display: block;
        line-height: 10px;
      }
      .partner-section {
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: flex-end;
        justify-content: center;
        padding-bottom: 13px;
      }
      .partner-section1 {
        flex: 0 0 auto;
        margin-top: 49px;
      }
      .image-container {
        box-sizing: border-box;
        display: block;
        width: 122px;
        max-width: initial;
        height: 53px;
        border: none;
        object-fit: cover;
      }
      .copyright-notice-container {
        box-sizing: border-box;
        display: flex;
        flex: 0 0 auto;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
      }
      .center-aligned-copyright-text {
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 68px;
      }
      .purple-heading {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        font: 700 12px Raleway, sans-serif;
        color: #a094b8;
      }
    </style>