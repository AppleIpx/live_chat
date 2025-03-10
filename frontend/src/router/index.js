import {createRouter, createWebHistory} from 'vue-router';
import home from '@/views/Home.vue';
import login from "@/views/Login.vue";
import register from "@/views/Register.vue";
import chat from "@/views/Chats.vue";
import chatRoom from "@/views/ChatRoom.vue";
import profile from "@/views/MyProfile.vue";
import anotherProfile from "@/views/AnotherProfile.vue";
import Users from "@/views/Users.vue";
import chatsDeleted from "@/views/ChatsDeleted.vue";
import chatsDeletedRoom from "@/views/ChatsDeletedRoom.vue";
import NotFound from "@/components/NotFound.vue";
import Forbidden from "@/components/Forbidden.vue";
import Deleted from "@/components/Deleted.vue";
import ServerError from "@/components/ServerError.vue";
import BlackList from "@/views/BlackList.vue";
import AnotherDeleted from "@/components/AnotherDeleted.vue";
import Blocked from "@/components/Blocked.vue";
import BannedAccount from "@/components/Banned.vue";
import AnotherBanned from "@/components/AnotherBanned.vue";
import Summarization from "@/views/SummarizationForm.vue";
import SummarizationsHistory from "@/views/SummarizationsHistory.vue";
import SummarizationDetail from "@/views/SummarizationDetail.vue";

const routes = [
    {path: '/', name: 'Home', component: home},
    {path: '/login', name: 'Login', component: login},
    {path: '/register', name: 'Register', component: register},
    {path: '/chats', name: 'Chats', component: chat},
    {path: '/chats/deleted', name: 'Deleted Chats', component: chatsDeleted},
    {
        path: '/chats/deleted/:chat_id',
        name: 'Deleted ChatRoom',
        component: chatsDeletedRoom,
        props: true
    },
    {path: '/profile/me', name: "Profile", component: profile},
    {path: '/profile/:user_id', name: "AnotherProfile", component: anotherProfile},
    {path: '/users/', name: 'Users', component: Users},
    {path: '/black-list', name: 'BlackList', component: BlackList},
    {path: '/chats/:chat_id', name: 'ChatRoom', component: chatRoom, props: true},
    {path: '/ai/new-summarization', name: 'Summarization', component: Summarization},
    {
        path: '/ai/summarization-history',
        name: 'SummarizationsHistory',
        component: SummarizationsHistory
    },
    {
        path: '/summarization-detail/:chatId',
        name: 'summarization-detail',
        component: SummarizationDetail,
    },
    {path: '/403', name: 'Forbidden', component: Forbidden},
    {path: '/blocked', name: 'Blocked', component: Blocked},
    {path: '/banned', name: 'Banned', component: BannedAccount},
    {path: '/another-banned', name: 'AnotherBanned', component: AnotherBanned},
    {path: '/deleted', name: 'Deleted', component: Deleted},
    {path: '/another-deleted', name: 'AnotherDeleted', component: AnotherDeleted},
    {path: '/500', name: 'ServerError', component: ServerError},
    {path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound},
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
