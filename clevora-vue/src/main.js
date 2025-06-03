// main.js
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// 引入全局樣式
import './assets/main.css';

// 引入 Bootstrap 和 Font Awesome
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { useUserStore } from '@/stores/userStore';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia); // 先安裝 pinia

// 在掛載應用程式前，嘗試載入使用者狀態
const userStore = useUserStore();
// Pinia store 在定義時已經會從 localStorage 載入 token 了
// 但為了確保萬無一失，我們可以手動觸發 Pinia store 的初始化或確認 token 已載入
// 這裡不需要額外的 loadUser 函數，因為 Pinia 的 setup store 在第一次 use 時就會執行
// 我們只需要確保在 router 安裝前 Pinia 和 userStore 被使用了

app.use(router);

app.mount('#app');