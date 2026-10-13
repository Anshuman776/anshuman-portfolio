// Tailwind config for the portfolio.
// The compiled stylesheet (static/css/site.css) is committed, so the server never needs Node.
// After changing classes in templates/ or data.py, rebuild it with:
//   npx tailwindcss@3.4.17 -i ./static/css/input.css -o ./static/css/site.css --minify

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html', './data.py'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        // Cool "ink" neutrals replace Tailwind's default zinc across the whole site
        zinc: {
          50: '#f6f8fa',
          100: '#eef1f5',
          200: '#d9dfe7',
          300: '#b4bfcc',
          400: '#8d9aab',
          500: '#6f7d90',
          600: '#4f5c6d',
          700: '#364252',
          800: '#232e3c',
          900: '#151c27',
          950: '#0b1017',
        },
        cyber: {
          bg: '#0b1017',        // page background
          panel: '#151c27',     // raised surfaces
          border: '#232e3c',    // hairlines
          accent: '#2dd4bf',    // primary accent (teal)
          accentHover: '#5eead4',
          accentGlow: 'rgba(45, 212, 191, 0.12)',
          cyan: '#7dd3fc',      // secondary accent (sky) for technical labels
          cyanGlow: 'rgba(125, 211, 252, 0.12)',
          green: '#4ade80',     // status: online / live
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
