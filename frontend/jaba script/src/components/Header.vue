<!-- components/Header.vue -->
<template>
    <div class="header-section">
      <router-link :to="header.home.link">
        <p class="main-title-text-style">NetLab AI</p>
      </router-link>
      <div class="header-nav-container">
        <div class="navigation-bar">
          <div class="main-nav-container">
            <p class="primary-text-content-style">
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
  </template>
  
  <script setup>
  import { header } from '@/config/header.js';
  </script>

  <style scoped>
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
      .primary-text-content-style {
        flex: 0 0 auto;
        padding: 0;
        margin: 0;
        font: 400 20px Raleway, sans-serif;
        color: #24222f;
      }
      .vertical-divider {
        box-sizing: border-box;
        flex: 0 0 auto;
        width: 1px;
        height: 29px;
        border-left: 1px solid #24222f;
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
  </style>