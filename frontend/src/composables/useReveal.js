let observer = null

function getObserver() {
  if (!observer && typeof window !== 'undefined' && 'IntersectionObserver' in window) {
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible')
            observer.unobserve(entry.target)
          }
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' },
    )
  }
  return observer
}

export const reveal = {
  mounted(el, binding) {
    el.classList.add('reveal')
    const delay = Number(binding.value) || 0
    if (delay) el.style.transitionDelay = `${Math.min(delay, 640)}ms`

    if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
      getObserver().observe(el)
    } else {
      el.classList.add('is-visible')
    }
  },
  unmounted(el) {
    if (observer) observer.unobserve(el)
  },
}
