import { api } from '../services/api'

const titleRef = { value: 'Family Tree' }

export async function loadSiteTitle() {
  try {
    const data = await api.getSite()
    if (data?.title) {
      titleRef.value = data.title
      if (typeof document !== 'undefined') document.title = data.title
    }
  } catch {
    /* keep default */
  }
  return titleRef.value
}
