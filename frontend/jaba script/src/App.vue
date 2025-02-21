<!-- html -->
<template>
<div class="container">
    <!-- header -->
    <header>
        <div>NetLab AI</div>
        <nav>
            <a href="#">Главная</a>
            <a href="#">Курс</a>
            <a href="#">Вход</a>
        </nav>
    </header>
    <!-- main -->
    <div>

    </div>
    <div>

    </div>  
    <div>

    </div>
    <div>

    </div>
    <!-- footer -->
    <footer>
        <div class="left">
            <p>Контакты команды</p>
            <nav>
            <p>Email: <a href="mailto:jabascript@sfedu.com">jabascript@sfedu.com</a></p>
            <p>Телефон: <a href="tel:+7-(938)-100-16-77">+7-(938)-100-16-77</a></p>
            <p>Адрес: <a href="https://yandex.ru/maps/?text=пер.+Некрасовский,+44,+г.+Таганрог" target="_blank">пер. Некрасовский, 44, г.Таганрог</a></p>
        </nav>
        </div>
        <div class="right">
            <p id="partner">Партнеры</p>
            <img src="@/assets/images/ictis.png" alt="Фото ICTIS" id="ictis">
        </div>  
    </footer>

    <hr class="line">
    <div class="bottom">
        <p id="netlab">© 2024 NetLab AI. Все права защищены.</p>
    </div>
</div>
</template>




<!-- js -->
<script setup>
import { ref, reactive } from 'vue';

const header = 
{
    home: {title: 'Главная', link: '/'},
    course: {title: 'Курс', link: '/course'},
    login: {title: 'Вход', link: '/login'},
}
</script>




<!-- css -->
<style scoped>
.container {
    display: grid;
    grid-template: repeat(6, minmax(100px, auto)) / 1fr;
    grid-template-areas:
    "header"
    "administration"
    "advantage"
    "about"
    "recomendation"
    "footer";
}

header {
    display: flex;
    grid-area: header;
    background-color: #F5F9F8;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
}

header nav {
    display: flex;
    column-gap: 2vw;
    
}

header nav a {
    text-decoration: none;
    color: #000;
    font-weight: bold;
}

header nav a:hover {
    text-decoration: underline #24222F;
}

footer {
    display: flex;
    grid-area: footer;
    background-color: #575667;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
}

.left {
    width: 50%;
}

.right {
    width: 50%;
    display: flex;
    justify-content: flex-end;
    flex-direction: column;
    align-items: flex-end;
}

.bottom {
    margin: 0px;
    background-color: #575667;
}

.line {
    margin: 0px 0px;
    height: 2px;
    background-color:  #A094B8;
}

#ictis {
    max-width: 50%;
}

#partner {
    margin-right: 5vw;
}
</style>