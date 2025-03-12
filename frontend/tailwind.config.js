/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        hartwell: ['Hartwell Alt', 'sans-serif'],
      },
    },
  },
    content: [
        './src/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                background: 'rgb(var(--background-start-rgb))',
                foreground: 'rgb(var(--foreground-rgb))',
            },
        },
    },
    plugins: [],
}