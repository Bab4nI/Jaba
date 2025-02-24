# Django + Vue.js Project 🚀

Welcome to the Django + Vue.js project! This template will help you get started with a full-stack application using Django as the backend and Vue.js as the frontend. Let's build something amazing! 🎉

## Table of Contents 📚

- [Project Setup](#project-setup-)
- [Recommended IDE Setup](#recommended-ide-setup-)
- [Development](#development-)
- [Production](#production-)
- [Customize Configuration](#customize-configuration-)
- [Contributing](#contributing-)
- [License](#license-)

## Project Setup 🛠️

To get started with this project, follow these steps:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/Bab4nI/Jaba.git -b kirill
   ```

2. **Set up the backend (Django):**

   ```sh
   cd backend/main
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Set up the frontend (Vue.js):**

   ```sh
   cd frontend/"jaba script"
   npm i
   npm run dev
   ```

4. **You're all set!** 🎉 The Django backend should be running on `http://localhost:8000` and the Vue.js frontend on `http://localhost:5173`.

## Recommended IDE Setup 💻

For the best development experience, we recommend using [VSCode](https://code.visualstudio.com/) with the following extensions:

- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (for Vue.js support)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (for Django support)

Make sure to disable Vetur if you have it installed, as it may conflict with Volar.

## Development 🚀

### Compile and Hot-Reload for Development

To start the development server with hot-reloading, run:

```sh
cd frontend/"jaba script"
npm run dev
```

This will start the Vue.js development server on `http://localhost:3000`.

### Backend Development

For Django backend development, run:

```sh
cd backend/main
python manage.py runserver
```

This will start the Django development server on `http://localhost:8000`.

## Production 🏗️

### Compile and Minify for Production

To build the Vue.js frontend for production, run:

```sh
cd frontend/"jaba script"
npm run build
```

This will create a `dist` folder with the optimized production build.

### Deploying Django

To deploy the Django backend, follow the official [Django deployment guide](https://docs.djangoproject.com/en/4.0/howto/deployment/).

## Customize Configuration ⚙️

### Vite Configuration

For customizing the Vue.js frontend, refer to the [Vite Configuration Reference](https://vite.dev/config/).

### Django Settings

For customizing the Django backend, modify the `settings.py` file in the `backend` directory.

## Contributing 🤝

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Happy coding! 🎉👨‍💻👩‍💻

![Happy Coding](https://media.giphy.com/media/3o7abAHdYvZdBNnGZq/giphy.gif)