/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#3A2E5C',
        gold: '#C8A967',
      },
      fontFamily: {
        serif: ['"Songti SC"', '"STSong"', '"PingFang SC"', 'serif'],
      },
    },
  },
  plugins: [],
};
