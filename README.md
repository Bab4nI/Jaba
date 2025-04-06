# Django + Vue.js Проект 🚀

Добро пожаловать в проект Django + Vue.js! Этот шаблон поможет вам начать создание полнофункционального приложения с Django на бэкенде и Vue.js на фронтенде. Давайте создадим что-то потрясающее! 🎉

## Содержание 📚
- [Настройка проекта](#настройка-проекта-)
- [Рекомендуемая настройка IDE](#рекомендуемая-настройка-ide-)
- [Разработка](#разработка-)
- [Продакшн](#продакшн-)
- [Настройка конфигурации](#настройка-конфигурации-)
- [Участие в проекте](#участие-в-проекте-)
- [Лицензия](#лицензия-)

## Настройка проекта 🛠️

Чтобы начать работу с проектом, выполните следующие шаги:

1. **Клонируйте репозиторий:**
    ```sh
    git clone https://github.com/Bab4nI/Jaba.git
    ```

2. **Скачать node:**
    ```
    https://nodejs.org/en

    или по ссылке:
    https://nodejs.org/dist/v22.14.0/node-v22.14.0-x64.msi
    ```

3. **Скачать postgresql:**
    ```
    https://sbp.enterprisedb.com/getfile.jsp?fileid=1259408
    
    При установке надо указывать следующие параметры:
        имя базы данных = netlabai
        имя пользователя = postgres
        пароль пользователя = ananas002

        Эти параметры стоят по умолчанию (их можно не трогать):
        DB_HOST=localhost
        DB_PORT=5432
    ```

4. **Настройте бэкенд (Django) и фронтенда (Vue.js):**
    ```sh
    cd backend/main
    pip install -r requirements.txt
    python manage.py migrate
    cd ../..
    cd frontend/"jaba script"
    npm i
    ```

5. **Запуск серверов:**
    ```
    Находясь в домашнем каталоге проекта (/Jaba), прописать:
        ```sh
        py .\run_servers.py
        ```
    ```

6. **Готово!** 🎉 Бэкенд Django должен работать на `http://localhost:8000`, а фронтенд Vue.js на `http://localhost:5173`.

## Рекомендуемая настройка IDE 💻

Для лучшего опыта разработки рекомендуем использовать [VSCode](https://code.visualstudio.com/) с следующими расширениями:
- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (для поддержки Vue.js)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (для поддержки Django)

Не забудьте отключить Vetur, если оно у вас установлено, так как оно может конфликтовать с Volar.

## Продакшн 🏗️

### Компиляция и минимизация для продакшн

Чтобы собрать фронтенд Vue.js для продакшн, выполните:
```sh
cd frontend/"jaba script"
npm run build
```
Это создаст папку `dist` с оптимизированной сборкой для продакшн.

### Развертывание Django

Чтобы развернуть бэкенд Django, следуйте официальному [руководству по развертыванию Django](https://docs.djangoproject.com/en/4.0/howto/deployment/).

## Настройка конфигурации ⚙️

### Конфигурация Vite

Для настройки фронтенда Vue.js обратитесь к [документации по настройке Vite](https://vite.dev/config/).

### Настройки Django

Для настройки бэкенда Django отредактируйте файл `settings.py` в директории `backend`.

## Участие в проекте 🤝

Мы рады принимать участие! Пожалуйста, выполните следующие шаги:

1. Форкните репозиторий.
2. Создайте новую ветку (`git checkout -b feature/AmazingFeature`).
3. Зафиксируйте изменения (`git commit -m 'Добавить AmazingFeature'`).
4. Отправьте изменения в ветку (`git push origin feature/AmazingFeature`).
5. Откройте Pull Request.

## Лицензия 📄

Этот проект лицензирован по лицензии MIT

---

Счастливого кодинга! 🎉👨‍💻👩‍💻  
![Счастливый кодинг](https://gifs.obs.ru-moscow-1.hc.sbercloud.ru/49fde73c1c7716bc51af25ffe7a549e5a48087e125338952e4d0e1f404dfb302.gif)