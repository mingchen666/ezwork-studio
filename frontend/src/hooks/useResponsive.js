import { ref, onMounted, onUnmounted } from 'vue'

export function useResponsive() {
  const isMobile = ref(false)
  const isTablet = ref(false)
  const isDesktop = ref(false)
  const screenWidth = ref(0)

  const updateResponsive = () => {
    screenWidth.value = window.innerWidth
    isMobile.value = screenWidth.value < 768
    isTablet.value = screenWidth.value >= 768 && screenWidth.value < 1024
    isDesktop.value = screenWidth.value >= 1024
  }

  onMounted(() => {
    updateResponsive()
    window.addEventListener('resize', updateResponsive)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateResponsive)
  })

  return {
    isMobile,
    isTablet,
    isDesktop,
    screenWidth
  }
}
