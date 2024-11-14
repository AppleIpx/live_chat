import {createRouter, createWebHistory} from 'vue-router';
import home from '@/views/Home.vue';
import login from "@/views/Login.vue";
import register from "@/views/Register.vue";
import chat from "@/views/Chats.vue";
import chatRoom from "@/views/ChatRoom.vue";
import profile from "@/views/MyProfile.vue";
import anotherProfile from "@/views/AnotherProfile.vue";
import Users from "@/views/Users.vue";

const routes = [
    {path: '/', name: 'Home', component: home},
    {path: '/login', name: 'Login', component: login},
    {path: '/register', name: 'Register', component: register},
    {path: '/chats', name: 'Chats', component: chat},
    {path: '/profile/me/', name: "Profile", component: profile},
    {path: '/profile/:user_id/', name: "AnotherProfile", component: anotherProfile},
    {path: '/users/', name: 'Users', component: Users},
    {path: '/chats/:chat_id', name: 'ChatRoom', component: chatRoom, props: true}
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
