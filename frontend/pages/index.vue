<!-- D:\desktop\PYProject\nuxt-camer-try\pages\index.vue -->
<script setup lang="ts">
// This page immediately redirects to the video page
navigateTo('/video');
</script>

<!-- Optional: Add a fallback template in case script fails or for accessibility -->
<template>
  <div class="flex items-center justify-center h-screen bg-gray-100">
    <p class="text-lg text-gray-700">Redirecting to video page...</p>
    <!-- Fallback link -->
    <NuxtLink to="/video" class="text-blue-600 hover:underline ml-2">Click here</NuxtLink>
  </div>
</template>