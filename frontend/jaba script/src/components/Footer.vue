<template>
  <div class="footer-container">
    <div class="footer-contacts-section">
      <div class="team-contacts-section">
        <div class="team-contact-info-container">
          <p class="team-contacts-heading">Контакты команды</p>
          <p class="team-contact-info-style">
            <span class="contact-info-style">Email: </span>
            <a href="mailto:netlabai@gmail.com" class="contact-info-link">netlabai@gmail.com</a>
            <span class="line-break-separator"><br /></span>

            <span class="contact-info-style">Телефон: </span>
            <a href="tel:+79381001677" class="contact-info-link">+7-(938)-100-16-77</a>
            <span class="line-break-separator"><br /></span>

            <span class="contact-info-style">Адрес: </span>
            <a href="https://yandex.ru/maps/?text=пер.%20Некрасовский,%2044,%20Таганрог" target="_blank" class="contact-info-link">
              пер. Некрасовский, 44, г. Таганрог
            </a>
          </p>
        </div>
        <div class="partner-section">
          <p class="team-contacts-heading">Партнёры</p>
          <div class="partner-logo-container">
            <a href="https://vk.com/ictis_sfedu" target="_blank"><img src="@/assets/images/ictis.png" class="image-container" /></a>
          </div>
        </div>
      </div>
    </div>
    <div class="copyright-container">
      <div class="center-aligned-copyright-text">
        <p class="purple-heading">© 2024 NetLab AI. Все права защищены.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// No additional script needed for this component
</script>

<style scoped>
.footer-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  width: 100%;
  padding-right: 20.5px;
  padding-left: 19.5px;
  background: var(--footer-background);
  transition: background-color 0.3s ease;
}

.footer-contacts-section {
  box-sizing: border-box;
  display: flex;
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
  min-width: 1200px;
  padding-top: 45px;
  padding-bottom: 61px;
}

.team-contact-info-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  max-width: 357px;
}

.team-contacts-heading {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 700 18px Raleway, sans-serif;
  color: var(--footer-text);
  transition: color 0.3s ease;
}

.team-contact-info-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  margin-top: 32px;
  color: var(--footer-secondary);
  text-align: left;
  transition: color 0.3s ease;
}

.contact-info-style {
  font: 400 18px Raleway, sans-serif;
  text-align: left;
  transition: color 0.3s ease;
}

.contact-info-link {
  font: 400 18px Raleway, sans-serif;
  color: var(--footer-secondary);
  text-align: left;
  text-decoration-line: underline;
  text-underline-offset: 5px;
  transition: color 0.3s ease;
}

.line-break-separator {
  display: block;
  line-height: 10px;
}

.partner-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 13px;
}

.partner-logo-container {
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

.copyright-container {
  box-sizing: border-box;
  display: flex;
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
  color: var(--footer-secondary);
  transition: color 0.3s ease;
}

@media (max-width: 1280px) {
  .team-contacts-section {
    min-width: auto;
    width: 100%;
    flex-direction: column;
    align-items: center;
    gap: 40px;
  }
  
  .partner-section {
    align-items: center;
  }
}

@media (max-width: 768px) {
  .team-contact-info-container {
    max-width: 100%;
    width: 100%;
  }
  
  .team-contacts-heading {
    text-align: center;
  }
  
  .team-contact-info-style {
    text-align: center;
  }
}
</style> 