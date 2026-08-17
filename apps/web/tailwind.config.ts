/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cork: {
          50: '#f9fafb',
          100: '#f3f4f6',
          500: '#ef6b3b',
          600: '#dc5a2c',
          700: '#b8441f',
          900: '#4a1a0f',
        }
      }
    },
  },
  plugins: [],
}
