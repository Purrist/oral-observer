import { defineStore } from 'pinia';
import axios from 'axios';
import { useRuntimeConfig } from '#app';

// Define the type for a single photo object
interface Photo {
    url: string;
    filename: string;
    tooth: string;
    selected: boolean;
    retryCount: number; // For image loading retry logic
}

// Define the type for grouped photos
interface ToothGroup {
    tooth: string;
    photoObjects: Photo[];
}

interface PhotosState {
    allPhotos: Photo[];
    groupedPhotos: ToothGroup[];
    latestPhoto: Photo | null;
    isLoadingPhotos: boolean;
    isCapturing: boolean;
    captureStatus: { message: string; isError: boolean } | null;
    isDeleting: boolean;
    deleteStatus: string;
    videoError: string; // Video stream error status
}

export const usePhotoStore = defineStore('photos', {
    state: (): PhotosState => ({
        allPhotos: [], // Flat list of all photos
        groupedPhotos: [], // Photos grouped by tooth
        latestPhoto: null, // The latest captured photo
        isLoadingPhotos: false, // Loading photos flag
        isCapturing: false, // Capture in progress flag
        captureStatus: null, // Capture status message
        isDeleting: false, // Deleting photos flag
        deleteStatus: '', // Delete status message
        videoError: '', // Video stream error status
    }),

    getters: {
        // Count of selected photos in the flat list
        selectedPhotosCount: (state) => state.allPhotos.filter(p => p.selected).length,
        // Check if all photos in the flat list are selected
        allSelected: (state) => state.allPhotos.length > 0 && state.selectedPhotosCount === state.allPhotos.length,
        // Check if all photos in a specific tooth group are selected (Getter function)
        isToothGroupAllSelected: (state) => (toothGroup: ToothGroup) => {
            return toothGroup.photoObjects.length > 0 && toothGroup.photoObjects.every(photo => photo.selected);
        },
         // Get a specific photo by tooth and filename (Getter function)
        getPhotoByToothAndFilename: (state) => (tooth: string, filename: string) => {
            return state.allPhotos.find(photo => photo.tooth === tooth && photo.filename === filename) || null;
        },
    },

    actions: {
        // Action to load photos from backend and update state
        async loadPhotos() {
            this.isLoadingPhotos = true;
            this.deleteStatus = ''; // Clear delete status on load

            const runtimeConfig = useRuntimeConfig();
            const API_BASE_URL = runtimeConfig.public.apiBaseUrl || 'http://localhost:5000';

            try {
                const response = await axios.get(`${API_BASE_URL}/list_photos`);
                const photosData = response.data || {}; // { '1': ['file1.jpg', ...], ... }
                const tempAllPhotos: Photo[] = [];
                const groupedByTooth: { [key: string]: Photo[] } = {}; // Temporary object to group photos

                // 1. Flatten and create photo objects for the flat list (allPhotos)
                for (const tooth in photosData) {
                    if (photosData.hasOwnProperty(tooth) && Array.isArray(photosData[tooth])) {
                        for (const filename of photosData[tooth]) {
                            if (typeof filename === 'string' && filename.match(/\.(jpg|jpeg|png|gif)$/i)) {
                                const photoObject: Photo = {
                                    url: `${API_BASE_URL}/photos/${tooth}/${filename}?t=${Date.now()}`, // Timestamp to prevent caching
                                    filename: filename,
                                    tooth: tooth,
                                    selected: false, // Default selection state
                                    retryCount: 0 // Initialize retry counter
                                };
                                tempAllPhotos.push(photoObject);

                                // Also add to temporary grouping object
                                if (!groupedByTooth[tooth]) {
                                    groupedByTooth[tooth] = [];
                                }
                                groupedByTooth[tooth].push(photoObject); // Store the SAME photo object reference
                            } else {
                                console.warn(`Skipping invalid filename for tooth ${tooth}:`, filename);
                            }
                        }
                    }
                }

                // Sort the flat list (useful for select all/delete logic and finding latest)
                tempAllPhotos.sort((a, b) => {
                    const toothA = parseInt(a.tooth, 10);
                    const toothB = parseInt(b.tooth, 10);
                    if (toothA !== toothB) {
                        return toothA - toothB; // Sort by tooth number
                    }
                    // Attempt to sort by timestamp part of the filename (assuming filename is timestamp.jpg)
                    const numA = parseInt(a.filename.split('.')[0], 10);
                    const numB = parseInt(b.filename.split('.')[0], 10);
                    if (!isNaN(numA) && !isNaN(numB)) {
                       return numA - numB; // Sort by numeric timestamp
                    }
                    return a.filename.localeCompare(b.filename); // Fallback to string comparison
                });
                this.allPhotos = tempAllPhotos; // Update state's flat list

                // Determine the latest photo (last one in the sorted list)
                this.latestPhoto = tempAllPhotos.length > 0 ? tempAllPhotos[tempAllPhotos.length - 1] : null;
                console.log('Latest photo:', this.latestPhoto);


                // 2. Populate groupedPhotos array from the temporary grouping object
                const tempGroupedPhotos: ToothGroup[] = [];
                const sortedToothNumbers = Object.keys(groupedByTooth).sort((a, b) => parseInt(a, 10) - parseInt(b, 10));

                for (const tooth of sortedToothNumbers) {
                    // Sort photos within each tooth group by filename (timestamp)
                    groupedByTooth[tooth].sort((a, b) => {
                         const numA = parseInt(a.filename.split('.')[0], 10);
                         const numB = parseInt(b.filename.split('.')[0], 10);
                         if (!isNaN(numA) && !isNaN(numB)) {
                            return numA - numB;
                         }
                         return a.filename.localeCompare(b.filename);
                    });
                    tempGroupedPhotos.push({
                        tooth: tooth,
                        photoObjects: groupedByTooth[tooth] // Use the array of photo objects
                    });
                }
                this.groupedPhotos = tempGroupedPhotos; // Update state's grouped list

                console.log(`Loaded ${this.allPhotos.length} photos, grouped into ${this.groupedPhotos.length} teeth.`);

            } catch (error) {
                console.error('Error loading photos:', error);
                this.allPhotos = []; // Clear lists on error
                this.groupedPhotos = [];
                this.latestPhoto = null;
                // Optionally set an error message in state for UI
            } finally {
                this.isLoadingPhotos = false;
            }
        },

        // Action to capture a photo via backend API
        async capturePhoto(tooth: number) {
            if (this.isCapturing) return;
            this.isCapturing = true;
            this.captureStatus = null; // Clear previous status

            const runtimeConfig = useRuntimeConfig();
            const API_BASE_URL = runtimeConfig.public.apiBaseUrl || 'http://localhost:5000';

            try {
                const response = await axios.post(`${API_BASE_URL}/capture_photo`, {
                    tooth: tooth // Send the selected tooth number
                });
                console.log('Photo capture response:', response.data);
                this.captureStatus = { message: `牙位 ${tooth} 照片已保存!`, isError: false };
                // After capture, refresh photos state
                await this.loadPhotos();
            } catch (error) {
                console.error('Error capturing photo:', error);
                const errorMsg = (error as any).response?.data?.error || (error as any).message || '未知错误';
                this.captureStatus = { message: `拍照失败: ${errorMsg}`, isError: true };
                if ((error as any).response) {
                    console.error('Backend Error Response Details:', (error as any).response.data);
                }
            } finally {
                this.isCapturing = false; // Reset capturing flag
                setTimeout(() => { this.captureStatus = null; }, 3000);
            }
        },

        // Action to delete selected photos via backend API
        async deleteSelectedPhotos() {
            const photosToDelete = this.allPhotos.filter(p => p.selected);
            if (photosToDelete.length === 0 || this.isDeleting) return;

            if (!confirm(`确定要删除选中的 ${photosToDelete.length} 张照片吗？此操作不可恢复！`)) {
                return;
            }

            this.isDeleting = true;
            this.deleteStatus = '正在删除...';

            const runtimeConfig = useRuntimeConfig();
            const API_BASE_URL = runtimeConfig.public.apiBaseUrl || 'http://localhost:5000';

            try {
                const payload = {
                    photos: photosToDelete.map(p => ({ tooth: p.tooth, filename: p.filename }))
                };
                const response = await axios.post(`${API_BASE_URL}/delete_photos`, payload);
                console.log('Delete response:', response.data);
                this.deleteStatus = response.data.message || `成功删除了 ${photosToDelete.length} 张照片`;
                await this.loadPhotos(); // Refresh photos after deletion
            } catch (error) {
                console.error('Error deleting photos:', error);
                const errorMsg = (error as any).response?.data?.message || (error as any).response?.data?.error || (error as any).message || '删除失败';
                this.deleteStatus = `删除失败: ${errorMsg}`;
                if ((error as any).response) {
                    console.error('Backend Error Response Details:', (error as any).response.data);
                }
            } finally {
                this.isDeleting = false;
                setTimeout(() => { this.deleteStatus = '' }, 5000);
            }
        },

        // Toggle selection state for a single photo (modifies state directly)
        toggleSelection(photo: Photo) {
            photo.selected = !photo.selected;
        },

        // Toggle selection state for all photos (modifies state directly)
        toggleSelectAll() {
            const targetState = !this.allSelected;
            this.allPhotos.forEach(p => p.selected = targetState);
        },

         // Toggle selection state for all photos within a specific tooth group (modifies state directly)
        toggleSelectAllTooth(toothGroup: ToothGroup) {
            const targetState = !this.isToothGroupAllSelected(toothGroup);
            toothGroup.photoObjects.forEach(photo => {
                photo.selected = targetState;
            });
        },

        // Handle image load errors in the album (modifies state directly)
         handleImageError(photo: Photo) {
             // Important: Find the mutable photo object in the state's array before modifying
             const photoInState = this.allPhotos.find(p => p.tooth === photo?.tooth && p.filename === photo?.filename);

             if (!photoInState || photoInState.retryCount >= 1) { // Max 1 retry for simplicity
                 console.error(`Max retries reached or photo not found in state for ${photo?.filename}`);
                 // Optional: Mark as errored or hide
                 // if(photoInState) photoInState.error = true;
                 return;
             }
             console.warn(`Album image failed to load (${photoInState.retryCount + 1}/${1 + 1}): ${photoInState.url}`);

             // Increment retry count and try reloading the image source with a new timestamp
             photoInState.retryCount = (photoInState.retryCount || 0) + 1;

              nextTick(() => { // Ensure reactivity system is ready
                 const originalUrl = `${useRuntimeConfig().public.apiBaseUrl || 'http://localhost:5000'}/photos/${photoInState.tooth}/${photoInState.filename}`;
                 // Create a new URL with a different timestamp/retry param
                 photoInState.url = `${originalUrl}?t=${Date.now()}&retry=${photoInState.retryCount}`;
                 console.log(`Retrying image load: ${photoInState.url}`);
             });
         },
         // Action to clear all photo data from the store
         clearPhotos() {
             this.allPhotos = [];
             this.groupedPhotos = [];
             this.latestPhoto = null;
         },

         // Action to set video stream error message
         setVideoError(message: string) {
             this.videoError = message;
         },

         // Action to clear video stream error message
         clearVideoError() {
             this.videoError = '';
         }
    }
});