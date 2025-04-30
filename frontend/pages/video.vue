<template>
  <!-- Main container with padding, min-height, and background -->
   <!-- Removed bg-gray-100/dark:bg-gray-900 as it's handled by app.vue -->
  <div class="p-6 video-page-container min-h-screen">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-gray-100">实时视频与照片查看</h1>

    <!-- Main layout: Two columns on large screens (lg breakpoint and up) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-10 max-w-screen-2xl mx-auto">

      <!-- 左侧大区域：视频流 或 放大照片 -->
      <div class="large-view-section lg:col-span-2 flex flex-col bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
        <!-- Title depends on what is displayed -->
        <h2 class="text-lg font-semibold mb-3 text-gray-700 dark:text-gray-200">{{ displayedPhoto ? '放大查看照片' : '实时视频' }}</h2>

        <!-- Display Area -->
        <div class="display-wrapper bg-gray-200 dark:bg-gray-700 border dark:border-gray-600 rounded overflow-hidden w-full aspect-video mb-4 self-center relative">
          <!-- Image for video stream or static photo -->
           <img
             v-if="currentDisplaySrc"
             ref="displayArea"
             :src="currentDisplaySrc"
             :alt="displayedPhoto ? `牙位 ${displayedPhoto.tooth} 照片 ${displayedPhoto.filename}` : 'Live video stream'"
             :class="{'object-contain': displayedPhoto, 'object-cover': !displayedPhoto}"
             class="w-full h-full block"
             @error="handleDisplayError"
           />
            <div v-else-if="!currentDisplaySrc && !store.isLoadingPhotos && !displayedPhoto" class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400">
               加载中... 或 无视频流源
            </div>

          <!-- Error overlay for display area -->
          <div v-if="displayError" class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center text-white text-center p-4 text-sm">
             {{ displayError }}
           </div>
        </div>

        <!-- Controls (e.g., Tooth Select, Capture Photo - primarily for video mode) -->
        <div v-if="!displayedPhoto" class="controls mt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
           <div class="flex items-center">
            <label for="tooth-select" class="mr-2 text-sm text-gray-700 dark:text-gray-300">选择牙位:</label>
            <select id="tooth-select" v-model="selectedTooth" class="border dark:border-gray-600 p-1.5 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100">
              <option v-for="n in 32" :key="n" :value="n">{{ n }} 号牙</option>
            </select>
          </div>
          <button
            @click="capturePhoto"
            :disabled="store.isCapturing"
            class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-5 rounded-lg text-base disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 ease-in-out"
            >
            {{ store.isCapturing ? '拍照中...' : '拍照' }}
          </button>
        </div>

         <!-- Close enlarged view button when a photo is displayed -->
         <div v-if="displayedPhoto" class="controls mt-4 flex justify-center">
             <button @click="closeEnlargedView" class="bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-lg text-sm transition duration-200 ease-in-out">
                 返回视频或最新照片
             </button>
         </div>

      </div>

      <!-- 右侧小区域：最新照片预览 -->
      <div class="sidebar-section lg:col-span-1 flex flex-col bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <h2 class="text-lg font-semibold mb-3 text-gray-700 dark:text-gray-200">最新照片</h2>

          <div v-if="store.isLoadingPhotos" class="text-center text-gray-600 dark:text-gray-400">加载中...</div>
          <div v-else class="flex flex-col">
              <div v-if="store.latestPhoto" class="latest-photo-preview border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden cursor-pointer hover:shadow-lg bg-white dark:bg-gray-700"
                   @click="goToAlbum"
              >
                  <img :src="store.latestPhoto.url" :alt="`最新照片 牙位 ${store.latestPhoto.tooth}`" class="w-full object-cover block" style="height: 180px;" />
                  <p class="text-sm text-center bg-gray-100 dark:bg-gray-600 py-1 px-2 truncate text-gray-700 dark:text-gray-200 border-t border-gray-200 dark:border-gray-600">{{ store.latestPhoto.tooth }}号牙 - {{ store.latestPhoto.filename.split('.')[0].substring(0, 8) }}</p>
              </div>
              <div v-else class="text-gray-500 dark:text-gray-400 text-center py-4">暂无最新照片</div>

               <p class="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center">点击最新照片查看相册</p>
               <NuxtLink to="/photo" class="text-blue-500 dark:text-blue-400 hover:underline text-center mt-2 text-sm">或直接前往相册</NuxtLink>

          </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { usePhotoStore } from '@/stores/photos';
import { useRuntimeConfig } from '#app';
// import type { Photo } from '@/stores/photos'; // Uncomment if you export Photo type from store

const route = useRoute();
const router = useRouter();
const store = usePhotoStore();

// --- Reactive State ---
const selectedTooth = ref(1);
const displayArea = ref<HTMLImageElement | null>(null);
const displayedPhoto = ref<any | null>(null); // Use 'any' or import Photo type if defined/exported

const displayError = ref('');


// --- Computed Properties ---
const currentDisplaySrc = computed(() => {
  // If a specific photo object is set in displayedPhoto, use its URL
  if (displayedPhoto.value) {
    return displayedPhoto.value.url;
  } else if (store.videoError) {
     // If there's a video error in the store and no specific photo is requested,
     // don't load any source to prevent broken image icon
     return null; // Or a path to a placeholder image indicating error
  }
   else {
    // If no specific photo is set, load the video stream URL
    // Add timestamp to prevent potential caching issues with the stream URL itself
     return `${useRuntimeConfig().public.apiBaseUrl || 'http://localhost:5000'}/video_feed?t=${Date.now()}`;
  }
});


// --- Methods ---

const handleDisplayError = (event: Event) => {
    console.error("Large display load error:", event);
    if (displayedPhoto.value) {
         displayError.value = `无法加载照片 ${displayedPhoto.value.filename}。请检查后端服务或文件是否存在。`;
         // Potentially trigger a retry from the store if this was a static image URL
         // store.handleImageError(displayedPhoto.value); // This action expects a Photo object
         // For enlarged view, simple error message might be enough
    } else {
        store.setVideoError('无法加载视频流。请检查后端服务或摄像头是否开启。'); // Update store state
        displayError.value = '无法加载视频流。请检查后端服务或摄像头是否开启。'; // Update local state
    }
};


const capturePhoto = () => {
  store.capturePhoto(selectedTooth.value);
};

const goToAlbum = () => {
  router.push('/photo'); // Use router.push for navigation
};

const closeEnlargedView = () => {
    displayedPhoto.value = null; // Clear the enlarged photo
    // Clear the route parameters when closing the enlarged view
     router.replace({ query: {} }); // Use replace to avoid adding to history
};


// Handle initial load and route parameter check
const initializeDisplay = async () => {
    displayError.value = '';

    // 1. Ensure photos are loaded in the store if needed
    // We need photos loaded to potentially find a photo specified by route params
    if (store.allPhotos.length === 0 && !store.isLoadingPhotos) {
        console.log('Photos not loaded, calling store.loadPhotos...');
        await store.loadPhotos(); // Wait for photos to load
    } else if (store.isLoadingPhotos) {
        console.log('Photos are currently loading...');
         await new Promise<void>(resolve => { // Specify Promise type
             const unwatch = watch(() => store.isLoadingPhotos, (newValue) => {
                 if (!newValue) {
                     unwatch();
                     resolve();
                 }
             });
              const timeout = setTimeout(() => {
                 if(unwatch) unwatch();
                 console.warn('Timeout waiting for photos to load.');
                 resolve();
              }, 15000);
        });
    } else {
        console.log('Photos already loaded.');
    }

    // 2. Check for route parameters to display a specific photo
    const tooth = route.query.tooth as string | undefined; // Allow undefined
    const filename = route.query.filename as string | undefined; // Allow undefined

    if (tooth && filename) {
        console.log(`Route params found: tooth=${tooth}, filename=${filename}. Attempting to display specific photo.`);
        // Use getter to find the photo in the store
        const photoToShow = store.getPhotoByToothAndFilename(tooth, filename);

        if (photoToShow) {
            console.log('Specific photo found in store, displaying it.');
            displayedPhoto.value = photoToShow; // Set the photo to be displayed
            // Clear any residual video error when displaying a static photo
            store.clearVideoError();
            displayError.value = '';

        } else {
            console.warn('Specific photo not found in store. Falling back to video stream.');
            displayedPhoto.value = null; // Fallback to video stream
             displayError.value = `未能找到指定的照片 (牙位${tooth}, 文件名${filename})。`; // Display error about photo not found
        }
    } else {
        console.log('No route params found. Displaying video stream.');
        displayedPhoto.value = null; // Display video stream by default
        displayError.value = '';
    }
};


// --- Lifecycle Hooks ---
onMounted(() => {
  console.log('Video page mounted. Initializing display based on route...');
  initializeDisplay();
});


watch(() => route.query, (newQuery, oldQuery) => {
    const toothChanged = newQuery.tooth !== oldQuery?.tooth;
    const filenameChanged = newQuery.filename !== oldQuery?.filename;

    if (toothChanged || filenameChanged) {
         console.log('Detected relevant route query change, re-initializing display.');
         initializeDisplay();
    } else {
         console.log('Route query changed, but tooth/filename params are the same or irrelevant.');
    }
}, { deep: true });


onUnmounted(() => {
  console.log('Video page unmounted.');
   store.clearVideoError();
   // Optional: Clear specific displayed photo state if desired, but not strictly necessary
   // Keeping it in store allows state preservation if user navigates back quickly.
   // displayedPhoto.value = null; // Uncomment if you want to reset on leaving
});

</script>

<style scoped>
/* Scoped styles for the video page */
/* Note: Most styling is handled by Tailwind CSS classes in the template */

.video-page-container {
  /* Tailwind classes handle padding, min-height */
   /* background handled by app.vue */
  /* max-width and centering handled by max-w-screen-2xl and mx-auto on the grid div */
}

.large-view-section .display-wrapper {
   /* Tailwind classes handle aspect ratio, background, border, rounded, overflow, width, centering, position: relative */
}

.large-view-section img {
   /* Tailwind classes handle display, width, height, object-fit */
    /* object-contain vs object-cover is now dynamic based on displayedPhoto */
}

.sidebar-section .latest-photo-preview img {
    /* Tailwind classes handle width, object-cover, display */
    /* height is set via inline style */
}

</style>