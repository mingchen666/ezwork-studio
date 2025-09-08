import { ref, onMounted } from 'vue'
import { storageService } from '@/utils/storage'

export function useImageGallery() {
  const gallery = ref([])

  // 加载图库
  const loadGallery = () => {
    try {
      gallery.value = storageService.getGallery()
    } catch (error) {
      console.error('Gallery load error:', error)
      gallery.value = []
    }
  }

  // 从图库删除
  const deleteFromGallery = (imageId) => {
    try {
      const index = gallery.value.findIndex(item => item.id === imageId)
      if (index > -1) {
        gallery.value.splice(index, 1)
        storageService.saveGallery(gallery.value)
      }
    } catch (error) {
      console.error('Delete from gallery error:', error)
      throw error
    }
  }

  // 清空图库
  const clearGallery = () => {
    gallery.value = []
    storageService.saveGallery([])
  }

  // 初始化
  onMounted(() => {
    loadGallery()
  })

  return {
    gallery,
    loadGallery,
    deleteFromGallery,
    clearGallery
  }
}
