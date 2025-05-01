<template>
  <div class="p-6 photo-page-container min-h-screen bg-gray-100">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-gray-100">照片相册</h1>

    <div class="max-w-screen-xl mx-auto flex flex-col bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">

       <div class="mb-6">
           <NuxtLink to="/video" class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 transition">
              <svg xmlns="http://www.w3.org/2000/svg" class="-ml-1 mr-2 h-5 w-5 text-gray-500 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h14" />
              </svg>
              返回视频页面
           </NuxtLink>
       </div>

      <div class="controls mb-6 flex flex-col sm:flex-row items-center gap-4 flex-shrink-0">
        <button
          @click="store.toggleSelectAll"
          :disabled="store.allPhotos.length === 0"
          class="bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 ease-in-out"
        >
          {{ store.allSelected ? '取消全选所有' : `全选所有 (${store.selectedPhotosCount}/${store.allPhotos.length})` }}
        </button>
        <button
          @click="store.deleteSelectedPhotos"
          :disabled="store.selectedPhotosCount === 0 || store.isDeleting"
          class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 ease-in-out"
          >
          {{ store.isDeleting ? '删除中...' : `删除选中 (${store.selectedPhotosCount})` }}
        </button>
         <span v-if="store.deleteStatus" class="text-sm ml-2 text-gray-700 dark:text-gray-300">{{ store.deleteStatus }}</span>
      </div>

      <div v-if="store.isLoadingPhotos" class="text-center py-10 flex-grow flex items-center justify-center text-gray-600 dark:text-gray-400">加载中...</div>

      <div v-else-if="store.allPhotos.length === 0" class="text-gray-500 dark:text-gray-400 text-center py-10 text-gray-600">
        暂无照片，请前往<NuxtLink to="/video" class="text-blue-500 dark:text-blue-400 hover:underline">视频页面</NuxtLink>拍照。
      </div>

      <div v-else class="flex flex-col gap-6 overflow-y-auto pr-2 max-h-[calc(100vh-250px)]">
        <div v-for="toothGroup in store.groupedPhotos" :key="toothGroup.tooth" class="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
          <div class="flex items-center justify-between mb-3">
             <h3 class="text-base font-semibold text-gray-800 dark:text-gray-100">{{ toothGroup.tooth }} 号牙 ({{ toothGroup.photoObjects.length }})</h3>
             <button
               @click="store.toggleSelectAllTooth(toothGroup)"
               :disabled="toothGroup.photoObjects.length === 0"
               class="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-2 py-1 rounded text-xs disabled:opacity-50 disabled:cursor-not-allowed transition duration-200"
             >
               {{ store.isToothGroupAllSelected(toothGroup) ? '取消全选本组' : '全选本组' }}
             </button>
          </div>

          <div class="photo-grid-row flex flex-wrap gap-3">
            <div
                v-for="photo in toothGroup.photoObjects"
                :key="photo.filename"
                class="photo-item relative border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden cursor-pointer hover:shadow-lg bg-white dark:bg-gray-700 flex flex-col flex-shrink-0"
                :class="{'ring-2 ring-blue-500 ring-offset-2 ring-offset-white dark:ring-offset-gray-800': photo.selected}"
                @click="viewPhotoEnlarged(photo)"
                style="width: 110px; height: 110px;"
            >
              <input
                type="checkbox"
                :checked="photo.selected"
                class="absolute top-1.5 left-1.5 z-10 h-4 w-4 cursor-pointer text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 rounded"
                @click.stop="store.toggleSelection(photo)"
              />
              <div class="flex-grow overflow-hidden">
                 <img :src="photo.url" :alt="`牙位 ${photo.tooth} 照片 ${photo.filename}`" class="w-full h-full object-cover block" @error="store.handleImageError(photo)" />
              </div>
              <p class="text-xs text-center bg-gray-100 dark:bg-gray-600 py-1 px-1 truncate text-gray-700 dark:text-gray-200 border-t border-gray-200 dark:border-gray-600">{{ photo.filename.split('.')[0].substring(0, 8) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { usePhotoStore } from '@/stores/photos';
import { useRouter } from 'vue-router';
// import type { Photo } from '@/stores/photos';

const store = usePhotoStore();
const router = useRouter();

const viewPhotoEnlarged = (photo: any) => {
    console.log('Navigating to video page to view photo:', photo);
    router.push({ path: '/video', query: { tooth: photo.tooth, filename: photo.filename } });
};

onMounted(() => {
  console.log('Photo page mounted. Loading photos if not loaded...');
  if (store.allPhotos.length === 0 && !store.isLoadingPhotos) {
     store.loadPhotos();
  }
});
</script>

<style scoped>
/* Note: Most styling is handled by Tailwind CSS classes in the template */

.photo-page-container {
  /* background handled by app.vue */
}
/* Custom scrollbar styles (optional) */
.overflow-y-auto::-webkit-scrollbar {
    width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}
.dark .overflow-y-auto::-webkit-scrollbar-track {
     background: #4a5568;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
    background: #a0aec0;
    border-radius: 3px;
}
.dark .overflow-y-auto::-webkit-scrollbar-thumb {
    background: #718096;
}
.overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: #718096;
}
.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}
</style>