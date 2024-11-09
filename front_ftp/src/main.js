import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 确保路径正确

createApp(App)
    .use(router) // 确保正确使用 router
    .mount('#app');


