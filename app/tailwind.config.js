/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'mapbench-blue': '#2563eb',
        'mapbench-green': '#10b981',
        'mapbench-purple': '#7c3aed',
      },
    },
  },
  plugins: [],
}