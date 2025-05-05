# Dark Theme Implementation for Authentication Pages

This update adds dark theme support for all authentication-related pages of the application:

- Sign In
- Sign Up
- Password Reset
- New Password

## Changes Made

1. Updated all CSS in authentication views to use CSS variables (defined in `index.html`) instead of hardcoded colors
2. Added dynamic image switching based on the current theme (day/night versions)
3. Added computed property `isDarkTheme` to each component to detect current theme state
4. Replaced `require()` with direct imports for loading images (Vue 3 with Vite compatibility)

## Required Manual Steps

To complete the implementation, you need to:

1. **Add night-themed background images**:
   - Replace placeholder files `login_night1.jpg` and `login_night2.jpg` with actual dark-themed images 
   - The night images should have the same dimensions as their day counterparts

2. **Test theme switching**:
   - Try switching themes with the theme toggle in your app
   - Verify that all authentication pages correctly update colors and images

## How it Works

The theme detection is based on the presence of the `dark-theme` class on the `html` element, which is set by the theme switching code in `index.html`. Each authentication component now includes this code:

```javascript
// Determine current theme
const isDarkTheme = computed(() => {
  return document.documentElement.classList.contains('dark-theme');
});
```

Images are imported and then switched using v-bind based on the theme:

```javascript
// Import images
import loginDayImage from '@/assets/images/login_day2.jpg';
import loginNightImage from '@/assets/images/login_night2.jpg';

// Use in template
<img :src="isDarkTheme ? loginNightImage : loginDayImage" class="hero-image-container" />
```

All colors have been replaced with CSS variables that automatically change when switching themes:

```css
.welcome-message {
  color: var(--text-color);
}
```

## Troubleshooting

If you see the error `Uncaught (in promise) ReferenceError: require is not defined`, it is likely because:
- Vue 3 with Vite does not support using `require()` for loading assets
- Use direct imports instead as shown in the example above 