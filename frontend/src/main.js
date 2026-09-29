import { createApp } from 'vue'

import '@fontsource-variable/inter'
import '@fontsource-variable/fraunces'
import './index.css'

import App from './App.vue'
import router from './router'
import { reveal } from './composables/useReveal'

createApp(App).use(router).directive('reveal', reveal).mount('#app')
