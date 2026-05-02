import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        colors: {
          background: '#1a1a2e',
          surface: '#222244',
          'surface-variant': '#2a2a4a',
          primary: '#a8b8d8',
          secondary: '#c4a8d8',
          accent: '#a8d8c4',
          error: '#d8a8a8',
          warning: '#d8cca8',
          info: '#a8c4d8',
          success: '#a8d8b4',
          'on-background': '#e0e0f0',
          'on-surface': '#e0e0f0',
        },
      },
    },
  },
  defaults: {
    global: {
      style: { fontFamily: "'Inter', sans-serif" },
    },
  },
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.mount('#app')
