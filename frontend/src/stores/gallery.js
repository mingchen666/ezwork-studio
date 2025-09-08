import { ref, computed, onMounted } from 'vue'
import { defineStore } from 'pinia'
import {
  getImagesListService,
  deleteImageService,
  saveImageService
} from '@/apis/images'

export const useGalleryStore = defineStore('gallery', () => {
  // 状态
  const images = ref([])
  const selectedImage = ref(null)
  const loading = ref(false)
  const isExpanded = ref(true)  // 展开/折叠状态
  const maxCount = ref(20)

  // 计算属性
  const imageCount = computed(() => images.value.length)
  const isFull = computed(() => images.value.length >= maxCount.value)
  const isCollapsed = computed(() => !isExpanded.value)  // 兼容原来的命名

  const latestImage = computed(() => {
    if (images.value.length === 0) return null
    return images.value[0] // 服务器返回的已经是按时间倒序
  })

  // 显示的图片列表 - 转换数据格式以适配组件
  const displayImages = computed(() => {
    return images.value.map(item => ({
      id: item.image_id,
      image_id: item.image_id,
      imageUrl: item.image_url,
      image_url: item.image_url,       // 兼容字段
      prompt: item.prompt,
      promptPreview: item.prompt.length > 25 ? item.prompt.substring(0, 25) + '...' : item.prompt,
      model: item.model,
      elapsedTime: item.elapsed_time,
      timestamp: item.created_at,
      sortTimestamp: item.sortTimestamp || new Date(item.created_at).getTime(),
      modelResponse: item.model_response || ''  // 添加模型回复
    }))
  })


  // 从服务器加载图片列表
  const loadImages = async (simple = true) => {
    loading.value = true
    try {
      const response = await getImagesListService({ simple })

      if (response.code === 200) {
        images.value = response.data.images || []
        console.log('图片列表加载成功:', images.value.length, '张图片')
        return { success: true, data: response.data }
      } else {
        throw new Error(response.message || '获取图片列表失败')
      }
    } catch (error) {
      console.error('加载图片列表失败:', error)
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 保存图片到服务器
  const saveImage = async (imageData) => {
    try {
      const response = await saveImageService(imageData)

      if (response.code === 200) {
        // 保存成功后，将新图片添加到列表开头
        const newImage = response.data.image
        images.value.unshift(newImage)

        // 如果超过最大数量，移除最后一个
        if (images.value.length > maxCount.value) {
          images.value.pop()
        }

        console.log('图片保存成功:', newImage.image_id)
        return { success: true, data: response.data }
      } else {
        throw new Error(response.message || '保存图片失败')
      }
    } catch (error) {
      console.error('保存图片失败:', error)
      return { success: false, message: error.message }
    }
  }

  // 删除图片
  const removeImage = async (imageId) => {
    try {
      const response = await deleteImageService(imageId)

      if (response.code === 200) {
        // 从本地列表中移除
        const index = images.value.findIndex(img => img.image_id === imageId)
        if (index > -1) {
          images.value.splice(index, 1)
          console.log('图片删除成功:', imageId)
        }

        // 如果删除的是当前选中的图片，清除选中状态
        if (selectedImage.value && selectedImage.value.image_id === imageId) {
          selectedImage.value = null
        }

        return { success: true, message: response.message }
      } else {
        throw new Error(response.message || '删除图片失败')
      }
    } catch (error) {
      console.error('删除图片失败:', error)
      return { success: false, message: error.message }
    }
  }

  // 选择图片
  const selectImage = (imageId) => {
    // 支持传入对象或字符串ID
    const id = typeof imageId === 'object' ? imageId.image_id || imageId.id : imageId

    const image = images.value.find(img => img.image_id === id)
    if (image) {
      selectedImage.value = image
      console.log('选中图片:', id)
      return image
    }
    return null
  }

  // 清除选中
  const clearSelection = () => {
    selectedImage.value = null
  }

  // 清空图库
  const clearAll = () => {
    images.value = []
    selectedImage.value = null
    console.log('图库已清空')
  }

  // 切换展开/折叠状态
  const toggleExpanded = () => {
    isExpanded.value = !isExpanded.value
  }

  // 兼容原来的方法名
  const toggleCollapse = () => {
    toggleExpanded()
  }

  // 设置展开状态
  const setExpanded = (expanded) => {
    isExpanded.value = expanded
  }

  // 兼容原来的方法名
  const setCollapsed = (collapsed) => {
    isExpanded.value = !collapsed
  }

  // 刷新图片列表
  const refreshImages = async () => {
    return await loadImages(true)
  }

  // 初始化 - 自动加载图片列表
  const initialize = async () => {
    console.log('初始化图库Store...')
    await loadImages(true)
  }

  return {
    // 状态
    images,
    selectedImage,
    loading,
    isExpanded,
    maxCount,

    // 计算属性
    imageCount,
    isFull,
    isCollapsed,  // 兼容原来的命名
    latestImage,
    displayImages, // 新增：格式化后的显示数据

    // 方法
    loadImages,
    saveImage,
    removeImage,
    selectImage,
    clearSelection,
    clearAll,
    toggleExpanded,
    toggleCollapse,  // 兼容原来的方法名
    setExpanded,
    setCollapsed,    // 兼容原来的方法名
    refreshImages,
    initialize       // 新增：初始化方法
  }
}, {
  persist: {
    key: 'ai-image-generator-gallery',
    storage: localStorage,
    pick: ['isExpanded'] // 只持久化展开状态
  }
})
