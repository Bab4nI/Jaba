Вот перевод README на русский язык:

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
    git clone https://github.com/Bab4nI/Jaba.git -b kirill
    ```

2. **Настройте бэкенд (Django):**
    ```sh
    cd backend/main
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```

3. **Настройте фронтенд (Vue.js):**
    ```sh
    cd frontend/"jaba script"
    npm i
    npm run dev
    ```

4. **Готово!** 🎉 Бэкенд Django должен работать на `http://localhost:8000`, а фронтенд Vue.js на `http://localhost:5173`.

## Рекомендуемая настройка IDE 💻

Для лучшего опыта разработки рекомендуем использовать [VSCode](https://code.visualstudio.com/) с следующими расширениями:
- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (для поддержки Vue.js)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (для поддержки Django)

Не забудьте отключить Vetur, если оно у вас установлено, так как оно может конфликтовать с Volar.

## Разработка 🚀

### Компиляция и горячая перезагрузка для разработки

Чтобы запустить сервер разработки с горячей перезагрузкой, выполните:
```sh
cd frontend/"jaba script"
npm run dev
```
Это запустит сервер разработки Vue.js на `http://localhost:3000`.

### Разработка бэкенда

Для разработки бэкенда на Django выполните:
```sh
cd backend/main
python manage.py runserver
```
Это запустит сервер разработки Django на `http://localhost:8000`.

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

Этот проект лицензирован по лицензии MIT — смотрите файл [LICENSE](LICENSE) для подробностей.

---

Счастливого кодинга! 🎉👨‍💻👩‍💻  
![Счастливый кодинг](https://media.giphy.com/media/fCSxHT0lQJV1C/giphy.gif?cid=790b7611q6pqcnrh821gy937th717ugwmtz8y89nrjy2qi0y&ep=v1_gifs_search&rid=giphy.gif&ct=g)