import { useSettingsStore } from '@/stores/settings'

class ApiService {
  async generateImage({ model, prompt, images }) {
    const settingsStore = useSettingsStore()
    const { baseUrl, apiKey } = settingsStore.apiConfig

    if (!baseUrl || !apiKey) {
      throw new Error('请先配置API设置')
    }

    const url = `${baseUrl}/v1beta/models/${model}:generateContent`

    const requestBody = {
      contents: [{
        parts: [{
          text: '请帮我画图：' + prompt
        }]
      }],
      generationConfig: {
        responseModalities: ["TEXT", "IMAGE"]
      }
    }

    // 添加图片数据
    if (images && images.length > 0) {
      images.forEach(imageData => {
        requestBody.contents[0].parts.push({
          inline_data: {
            mime_type: imageData.mimeType,
            data: imageData.base64
          }
        })
      })
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'x-goog-api-key': apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `API请求失败 (${response.status})`

      try {
        const errorData = JSON.parse(errorText)
        if (errorData.error && errorData.error.message) {
          errorMessage = errorData.error.message
        }
      } catch (e) {
        // 使用默认错误消息
      }

      throw new Error(errorMessage)
    }

    return await response.json()
  }
}

export const apiService = new ApiService()
