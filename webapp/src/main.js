import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import VueCodeHighlight from 'vue-code-highlight';

let app = createApp(App)
app.config.globalProperties.$hostname = 'http://localhost:3000'
app.mount('#app')


