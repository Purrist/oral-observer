// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  // Configuration for Local Network Access
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    port: 3000      // Nuxt development port (default is 3000)
  },

  // Runtime Configuration (for backend API URL)
  runtimeConfig: {
    public: {
      // This will prioritize the NUXT_PUBLIC_API_BASE env var.
      // If not set, it falls back to 'http://localhost:5000'.
      // For LAN access, the batch file MUST set this env var to the computer's LAN IP.
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000'
    }
  },

  // Modules: Add Pinia and Tailwind CSS
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  tailwindcss: {
    // Options for Tailwind CSS module
  },

  // Pinia configuration (optional, default works fine)
  pinia: {
    storeDirs: ['./stores/**'], // Where your Pinia stores are located
  },

  // Add any other necessary configurations
})