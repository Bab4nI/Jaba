<template>
  <div id="app">
    <Header />
    <router-view></router-view>
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'; // Импортируем компонент Header
</script>


<style>
*{
    margin: 0px;
}
    
a {
    all: unset;
    cursor: pointer;
}
</style>