import { computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { useGalleryStore } from '@/stores/gallery'
import { useSettingsStore } from '@/stores/settings'
import { apiService } from '@/utils/api'

export function useImageGenerator() {
  const generatorStore = useGeneratorStore()
  const galleryStore = useGalleryStore()
  const settingsStore = useSettingsStore()

  // 计算属性 - 从store获取数据
  const loading = computed(() => generatorStore.loading)
  const resultImage = computed(() => generatorStore.currentResult.imageUrl)
  const modelResponse = computed(() => generatorStore.currentResult.modelResponse)
  const elapsedTime = computed(() => generatorStore.currentResult.elapsedTime)

  // 生成图片
  const generateImage = async (params) => {
    try {
      // 检查API配置
      if (!settingsStore.isApiConfigured) {
        throw new Error('请先配置API设置')
      }

      console.log('开始生成图片，参数:', params)

      // 开始生成
      generatorStore.startGeneration({
        ...params,
        base_url: settingsStore.baseUrl,
        api_key: settingsStore.apiKey
      })

      // 调用API
      const result = await apiService.generateImage({
        model: params.model,
        prompt: params.prompt,
        images: params.images
      })

      console.log('API响应:', result)

      // 处理结果
      if (result.candidates && result.candidates.length > 0) {
        const parts = result.candidates[0].content.parts
        let imageData = null
        let textResponse = ''

        for (const part of parts) {
          if (part.inlineData && part.inlineData.data) {
            imageData = part.inlineData.data
            console.log('找到图片数据，长度:', imageData.length)
          }
          if (part.text) {
            textResponse += part.text + ' '
          }
        }

        if (imageData) {
          const base64ImageUrl = `data:image/png;base64,${imageData}`
          const modelResponseText = textResponse.trim()

          console.log('图片生成成功，开始自动保存...')

          // 首先设置临时图片用于立即显示
          generatorStore.setTemporaryResult({
            imageUrl: base64ImageUrl,
            modelResponse: modelResponseText,
            elapsedTime: generatorStore.getElapsedTime(),
            prompt: params.prompt,
            model: params.model
          })
          
          console.log('临时图片已设置，现在保存到服务器...')

          // 直接保存到服务器 - 传递正确的数据
          const saveData = {
            image_data: base64ImageUrl,
            prompt: params.prompt,
            model: params.model,
            elapsed_time: generatorStore.getElapsedTime(),
            model_response: modelResponseText,
            base_url: settingsStore.baseUrl,
            api_key: settingsStore.apiKey
          }

          console.log('保存数据:', {
            prompt: saveData.prompt,
            model: saveData.model,
            elapsed_time: saveData.elapsed_time,
            model_response: saveData.model_response,
            has_image_data: !!saveData.image_data,
            image_data_length: saveData.image_data ? saveData.image_data.length : 0
          })

          try {
            const saveResult = await galleryStore.saveImage(saveData)
            console.log('saveResult:', saveResult)

            if (saveResult && saveResult.success) {
              // 用后端返回的数据更新结果（包含OSS URL）
              if (saveResult.data && saveResult.data.image) {
                generatorStore.setGenerationResult(saveResult.data.image)
                console.log('保存成功，后端返回数据:', saveResult.data.image)
                console.log('图片URL:', saveResult.data.image.image_url)
              }
            } else {
              console.error('保存失败，saveResult:', saveResult)
              // 保存失败但图片已经显示了，只是记录错误
              console.warn('图片保存到服务器失败:', saveResult ? saveResult.message : '未知错误')
            }
          } catch (saveError) {
            console.error('保存过程异常:', saveError)
            console.warn('图片保存到服务器异常，但图片已显示')
          }

        } else {
          throw new Error('API返回的数据中未找到图片')
        }
      } else {
        throw new Error('API返回数据格式错误')
      }

    } catch (error) {
      console.error('生成图片失败:', error)
      generatorStore.setGenerationError(error)
      throw error
    }
  }

  // 选择图库图片
  const selectGalleryImage = (imageData) => {
    galleryStore.selectImage(imageData.image_id || imageData.id)
    generatorStore.setCurrentResultFromGallery(imageData)
  }

  return {
    loading,
    resultImage,
    modelResponse,
    elapsedTime,
    generateImage,
    selectGalleryImage
  }
}
