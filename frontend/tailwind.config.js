/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#0c0c11",
        surface: "#13131c",
        elevated: "#1c1c2e",
        accent: "#7c6af5",
        "accent-dim": "rgba(124,106,245,0.15)",
        success: "#4ade80",
        warning: "#fbbf24",
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
