// tailwind.config.ts
import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  // IMPORTANT: Configure dark mode to be based on the presence of the 'dark' class
  // on the html element (which our app.vue logic adds/removes).
  darkMode: 'class',

  // Configure the paths to all of your template files,
  // so Tailwind can scan them for classes.
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
    "./nuxt.config.ts" // Include nuxt.config if you use classes there
  ],
  theme: {
    extend: {
      // You can extend Tailwind's default theme here (e.g., custom colors, spacing)
    },
  },
  plugins: [
    // Add any Tailwind plugins here if needed
    // require('@tailwindcss/forms'), // Example plugin for better form styling
  ],
}