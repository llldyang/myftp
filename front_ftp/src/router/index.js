import { createRouter, createWebHistory } from 'vue-router';

import Login from '../views/Login.vue';
import TwoFactorAuth from '../views/TwoFactorAuth.vue';
import FileManager from '../views/FileManager.vue';
import QRCode from '../views/QRCode.vue';


const routes = [
    {
        path: '/',
        name: 'Login',
        component: Login,
    },
    {
        path: '/2fa',
        name: 'TwoFactorAuth',
        component: TwoFactorAuth,
        
    },
    {
        path: '/auth/2fa',
        name: 'TwoFactorAuth',
        component: TwoFactorAuth,
        
    },
    {
        path: '/auth/qr-code',
        name:QRCode,
        component: QRCode,
    },  // 展示二维码的页面
    {
        path: '/auth/file-manager',
        name: 'FileManager',
        component: FileManager,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
