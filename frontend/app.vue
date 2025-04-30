<template>
  <!-- The 'dark' class will be added to the html element by the script logic -->
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300 ease-in-out">
    <header class="bg-white dark:bg-gray-800 shadow-md">
      <nav class="container mx-auto px-6 py-3 flex items-center justify-between">
        <!-- Site Title or Logo -->
        <NuxtLink to="/video" class="text-xl font-bold text-gray-800 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition">
          口腔观察仪
        </NuxtLink>

        <!-- Navigation Links -->
        <div class="flex items-center gap-6">
          <NuxtLink to="/video" active-class="text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400" class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 pb-1 transition">
            视频与最新照片
          </NuxtLink>
          <NuxtLink to="/photo" active-class="text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400" class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 pb-1 transition">
            相册
          </NuxtLink>

          <!-- Dark Mode Toggle Button -->
          <button @click="toggleDarkMode" class="focus:outline-none text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition">
             <svg v-if="isDarkMode" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
          </button>
        </div>
      </nav>
    </header>

    <!-- NuxtPage component renders the current page content (video.vue or photo.vue) -->
    <!-- The min-h-screen on the main div ensures content pushes footer down if needed -->
    <main>
       <NuxtPage />
    </main>

    <!-- Optional Footer -->
    <!-- <footer class="bg-gray-200 dark:bg-gray-700 text-center p-4 mt-8">
      <p>© 2023 My App</p>
    </footer> -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// Reactive state for dark mode
const isDarkMode = ref(false);

// Function to toggle dark mode
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  // Update localStorage
  localStorage.setItem('darkMode', isDarkMode.value ? 'true' : 'false');
  // Update the 'dark' class on the html element
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

// On component mount, check localStorage for theme preference
onMounted(() => {
  // Check for saved preference, default to false if not found
  const savedTheme = localStorage.getItem('darkMode');
  isDarkMode.value = savedTheme === 'true';

  // Apply the theme class immediately
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  // Optional: Listen for system theme changes (prefers-color-scheme),
  // but Local Storage preference usually overrides this.
  // const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  // const handleSystemThemeChange = (e) => {
  //    if (!localStorage.getItem('darkMode')) { // Only apply system preference if user hasn't set a manual one
  //        isDarkMode.value = e.matches;
  //        if (isDarkMode.value) {
  //           document.documentElement.classList.add('dark');
  //        } else {
  //           document.documentElement.classList.remove('dark');
  //        }
  //    }
  // };
  // mediaQuery.addListener(handleSystemThemeChange);
  // // Clean up listener on unmount if necessary (using onUnmounted)
});

// No unmounted logic needed here for this simple example

</script>

<style>
/* Global styles */
/* The transition class on the main div handles smooth color changes */
/* You can add other global styles here if needed */
/* html.dark body { background-color: #1a202c; color: #e2e8f0; } */
</style>