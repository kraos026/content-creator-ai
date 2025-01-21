import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'

// Configuration d'axios pour l'API
axios.defaults.baseURL = 'http://localhost:5000'

const app = createApp(App)
app.mount('#app')
