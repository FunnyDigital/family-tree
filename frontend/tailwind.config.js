/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#fafaf9',
        surface: '#ffffff',
        line: '#e7e5e4',
        ink: {
          DEFAULT: '#1c1917',
          soft: '#44403c',
          muted: '#78716c',
          faint: '#a8a29e',
        },
        accent: {
          DEFAULT: '#10b981',
          700: '#047857',
          600: '#059669',
          500: '#10b981',
          100: '#d1fae5',
          50: '#ecfdf5',
        },
      },
      fontFamily: {
        sans: ['Inter Variable', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Fraunces Variable', 'Fraunces', 'Georgia', 'serif'],
      },
      boxShadow: {
        soft: '0 1px 2px rgba(28,25,23,0.04), 0 10px 30px -16px rgba(28,25,23,0.18)',
        lift: '0 2px 4px rgba(28,25,23,0.05), 0 18px 40px -20px rgba(28,25,23,0.28)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
    },
  },
  plugins: [],
}
