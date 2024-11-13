import {createRouter, createWebHistory} from 'vue-router';
import home from '@/views/Home.vue';
import login from "@/views/Login.vue";
import register from "@/views/Register.vue";
import chat from "@/views/Chats.vue";
import profile from "@/views/Profile.vue";

const routes = [
    {path: '/', name: 'Home', component: home},
    {path: '/login', name: 'Login', component: login},
    {path: '/register', name: 'Register', component: register},
    {path: '/chats', name: 'Chats', component: chat},
    {path: '/profile', name: "Profile", component: profile}
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
