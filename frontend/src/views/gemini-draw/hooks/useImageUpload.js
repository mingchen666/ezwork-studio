import { imageUtils } from '@/utils/imageUtils'

export function useImageUpload() {

  // 验证文件
  const validateFile = (file) => {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      throw new Error(`请上传有效的图片文件："${file.name}"！`)
    }

    // 验证文件大小（最大10MB）
    if (file.size > 10 * 1024 * 1024) {
      throw new Error(`图片"${file.name}"文件大小不能超过10MB！`)
    }

    return true
  }

  // 处理多张图片
  const processImages = async (files) => {
    const processedImages = []

    for (const file of files) {
      try {
        validateFile(file)
        const imageData = await processImage(file)
        processedImages.push(imageData)
      } catch (error) {
        throw error
      }
    }

    return processedImages
  }

  // 处理单张图片
  const processImage = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()

      reader.onload = (e) => {
        try {
          const base64Data = e.target.result.split(',')[1] // 移除data:image/...;base64,前缀
          const mimeType = imageUtils.getMimeType(file)

          const imageData = {
            id: Date.now() + Math.random(),
            name: file.name,
            base64: base64Data,
            mimeType: mimeType,
            dataUrl: e.target.result,
            size: file.size
          }

          resolve(imageData)
        } catch (error) {
          reject(new Error(`图片"${file.name}"处理失败`))
        }
      }

      reader.onerror = () => {
        reject(new Error(`图片"${file.name}"读取失败，请重试！`))
      }

      reader.readAsDataURL(file)
    })
  }

  return {
    validateFile,
    processImages,
    processImage
  }
}
