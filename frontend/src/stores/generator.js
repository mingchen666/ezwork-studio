import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useGeneratorStore = defineStore('generator', () => {
  // 状态
  const loading = ref(false)
  const uploadedImages = ref([])

  // 当前绘图结果 - 只存储必要信息到本地
  const currentResult = ref({
    imageUrl: '',        // OSS的URL，用于显示
    prompt: '',
    model: '',
    elapsedTime: '',
    timestamp: null,
    modelResponse: '',   // 模型回复
    image_id: ''         // 后端返回的业务ID
  })

  // 生成统计
  const stats = ref({
    totalGenerations: 0,
    successCount: 0,
    failureCount: 0,
    totalTime: 0
  })

  // 计算属性
  const hasResult = computed(() => !!currentResult.value.imageUrl)

  const successRate = computed(() => {
    if (stats.value.totalGenerations === 0) return 0
    return ((stats.value.successCount / stats.value.totalGenerations) * 100).toFixed(1)
  })

  const averageTime = computed(() => {
    if (stats.value.successCount === 0) return 0
    return (stats.value.totalTime / stats.value.successCount).toFixed(1)
  })

  const canGenerate = computed(() => (prompt) => {
    return !loading.value && prompt && prompt.trim().length > 0
  })

  // 私有变量
  let _startTime = 0

  // 开始生成
  const startGeneration = (params) => {
    loading.value = true
    clearCurrentResult()

    // 记录开始时间
    _startTime = Date.now()

    // 保存生成参数
    currentResult.value.prompt = params.prompt
    currentResult.value.model = params.model

    // 增加总生成次数
    stats.value.totalGenerations++
  }

  // 获取计算后的elapsed_time
  const getElapsedTime = () => {
    return _startTime ? ((Date.now() - _startTime) / 1000).toFixed(1) : '0'
  }

  // 生成成功并保存后更新结果 - 直接用后端数据
  const setGenerationResult = (savedImageData) => {
    const elapsedTime = getElapsedTime()

    // 直接使用后端返回的数据
    currentResult.value = {
      ...currentResult.value,
      imageUrl: savedImageData.image_url,      // OSS URL
      image_id: savedImageData.image_id,       // 业务ID
      elapsedTime: savedImageData.elapsed_time || elapsedTime, // 优先使用后端返回的
      timestamp: savedImageData.created_at || new Date().toISOString(),
      modelResponse: savedImageData.model_response || '' // 模型回复
    }

    // 更新统计
    stats.value.successCount++
    stats.value.totalTime += parseFloat(elapsedTime)

    loading.value = false

    console.log('图片生成并保存成功，使用OSS URL:', savedImageData.image_url)
  }

  // 生成失败
  const setGenerationError = (error) => {
    loading.value = false
    stats.value.failureCount++
    console.error('Generation failed:', error)
  }

  // 清除当前结果
  const clearCurrentResult = () => {
    currentResult.value = {
      imageUrl: '',
      prompt: '',
      model: '',
      elapsedTime: '',
      timestamp: null,
      modelResponse: '',
      image_id: ''
    }
  }

  // 从图库选择图片时设置当前结果
  const setCurrentResultFromGallery = (imageData) => {
    currentResult.value = {
      imageUrl: imageData.image_url,
      prompt: imageData.prompt,
      model: imageData.model || '',
      elapsedTime: imageData.elapsed_time || '',
      timestamp: imageData.created_at,
      modelResponse: imageData.model_response || '', // 模型回复
      image_id: imageData.image_id
    }
  }

  // 上传图片管理
  const setUploadedImages = (images) => {
    uploadedImages.value = images
  }

  const addUploadedImage = (image) => {
    uploadedImages.value.push(image)
  }

  const removeUploadedImage = (index) => {
    if (index >= 0 && index < uploadedImages.value.length) {
      uploadedImages.value.splice(index, 1)
    }
  }

  const clearUploadedImages = () => {
    uploadedImages.value = []
  }

  // 重置统计
  const resetStats = () => {
    stats.value = {
      totalGenerations: 0,
      successCount: 0,
      failureCount: 0,
      totalTime: 0
    }
  }

  return {
    // 状态
    loading,
    currentResult,
    uploadedImages,
    stats,

    // 计算属性
    hasResult,
    successRate,
    averageTime,
    canGenerate,

    // 方法
    startGeneration,
    getElapsedTime,      // 新增：获取计算后的时间
    setGenerationResult,
    setGenerationError,
    clearCurrentResult,
    setCurrentResultFromGallery,
    setUploadedImages,
    addUploadedImage,
    removeUploadedImage,
    clearUploadedImages,
    resetStats
  }
}, {
  persist: {
    key: 'ai-image-generator-current',
    storage: localStorage,
    paths: ['currentResult', 'stats']
  }
})
