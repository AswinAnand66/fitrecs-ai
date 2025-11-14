/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4fd1c5',
          DEFAULT: '#38b2ac',
          dark: '#319795',
        },
        secondary: {
          light: '#7f9cf5',
          DEFAULT: '#667eea',
          dark: '#5a67d8',
        },
        background: '#f7fafc',
        surface: '#ffffff',
        error: '#e53e3e',
        success: '#48bb78',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      boxShadow: {
        card: '0 2px 4px rgba(0,0,0,0.1)',
        elevated: '0 4px 6px rgba(0,0,0,0.1)',
      },
    },
  },
  plugins: [],
  important: true, // This ensures Tailwind classes override MUI
};