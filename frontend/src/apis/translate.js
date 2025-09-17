import request from '@/utils/request'
import { useSettingsStore } from '@/stores/settings'

/**
 * 翻译提示词为英文
 * @param {string} text 要翻译的文本
 * @returns {Promise} 翻译结果
 */
export const translateToEnglish = async (text) => {
  const settingsStore = useSettingsStore()
  const config = settingsStore.apiConfig
  
  if (!config.baseUrl || !config.apiKey) {
    throw new Error('请先配置API设置')
  }

  if (!text?.trim()) {
    throw new Error('请输入要翻译的内容')
  }

  const translationModel = config.translationModel || 'gpt-4.1'

  try {
    // 构建请求URL
    const url = `${config.baseUrl.replace(/\/$/, '')}/v1/chat/completions`
    
    // 构建请求体
    const requestBody = {
      model: translationModel,
      messages: [
        {
          role: "system",
          content: "你是一个英文绘图提示词翻译助手，擅长将用户的文字翻译为精准的英文，以便于绘制描述精准的图像"
        },
        {
          role: "user",
          content: text.trim()
        }
      ]
    }

    // 发送请求
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`
      },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error?.message || `HTTP错误: ${response.status}`)
    }

    const data = await response.json()
    
    // 检查响应格式
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      throw new Error('翻译API返回格式错误')
    }

    const translatedText = data.choices[0].message.content

    if (!translatedText?.trim()) {
      throw new Error('翻译结果为空')
    }

    return {
      success: true,
      data: {
        original: text,
        translated: translatedText.trim(),
        model: translationModel
      }
    }
    
  } catch (error) {
    console.error('Translation error:', error)
    
    // 网络错误处理
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('网络连接失败，请检查API地址和网络连接')
    }
    
    // API错误处理
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      throw new Error('API Key无效，请检查设置')
    }
    
    if (error.message.includes('429')) {
      throw new Error('请求过于频繁，请稍后再试')
    }
    
    if (error.message.includes('insufficient_quota')) {
      throw new Error('API配额不足，请检查账户余额')
    }
    
    // 抛出原始错误或包装后的错误
    throw error
  }
}

/**
 * 检查翻译配置是否完整
 * @returns {boolean} 配置是否完整
 */
export const checkTranslationConfig = () => {
  const settingsStore = useSettingsStore()
  const config = settingsStore.apiConfig
  
  return !!(config.baseUrl && config.apiKey && config.translationModel)
}
