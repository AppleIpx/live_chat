import axios from "axios";

const apiClient = axios.create({
    baseURL: process.env.VUE_APP_BACKEND_URL,
});

const apiClientWithoutAuth = axios.create({
    baseURL: process.env.VUE_APP_BACKEND_URL,
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
        this.$router.push("/");
        return Promise.reject(new Error("Нет токена доступа"));
    }
    config.headers.Authorization = `Bearer ${token}`;
    return config;
});

export const chatService = {
    async fetchChatDetails(chatId) {
        return await apiClient.get(`/api/chats/${chatId}/`);
    },
    async sendMessage(chatId, messageData) {
        return await apiClient.post(`/api/chats/${chatId}/messages/`, messageData);
    },
    async fetchChats() {
        return await apiClient.get(`/api/chats/`);
    },
    async createChat(recipientData) {
        return await apiClient.post('/api/chats/create/direct', recipientData)
    }
};

export const userService = {
    async fetchUserDetails(userId) {
        return await apiClient.get(`/api/users/read/${userId}`);
    },
    async fetchUsers() {
        return await apiClient.get('/api/users')
    },
    async fetchUserMe() {
        return await apiClient.get('/api/users/me')
    },
    async updateUserImage(userImageForm) {
        return await apiClient.patch(
            '/api/users/me/upload-image',
            userImageForm,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            })
    },
    async updateUserInfo(userForm) {
        return await apiClient.patch('/api/users/me', userForm)
    },
};

export const authService = {
    async loginUser(loginData) {
        return await apiClientWithoutAuth.post('/api/auth/jwt/login', loginData)
    },
    async registerUser(registerData) {
        return await apiClientWithoutAuth.post('/api/auth/register', registerData)
    }
}
