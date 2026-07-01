/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#10B981',
        'primary-dark': '#059669',
        danger: '#EF4444',
        warning: '#F59E0B',
        safe: '#10B981',
        caution: '#F59E0B',
        risk: '#EF4444',
      }
    }
  },
  plugins: []
}
