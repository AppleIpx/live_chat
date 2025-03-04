import axios from "axios";
import router from "@/router";


const apiClient = axios.create({
    baseURL: process.env.VUE_APP_BACKEND_URL,
    withCredentials: true

});

const apiClientWithoutAuth = axios.create({
    baseURL: process.env.VUE_APP_BACKEND_URL,
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
        return Promise.reject(new Error("Нет токена доступа"));
    }
    config.headers.Authorization = `Bearer ${token}`;
    return config;
});

export const chatService = {
    async fetchChatDetails(chatId) {
        try {
            return await apiClient.get(`/api/chats/${chatId}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async fetchChats(queryParams) {
        try {
            return await apiClient.get(`/api/chats?${queryParams.toString()}`)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async fetchDeletedChats(pageCursor) {
        try {
            if (!pageCursor) {
                return await apiClient.get(`/api/chats/deleted?size=3`)
            }
            return await apiClient.get(`/api/chats/deleted?size=3&cursor=${pageCursor}`)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async createChat(recipientData) {
        try {
            return await apiClient.post('/api/chats/create/direct', recipientData)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async createGroupChat(groupData) {
        try {
            return await apiClient.post('/api/chats/create/group', groupData)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async sendTypingStatus(chatId, isTyping) {
        try {
            return await apiClient.post(`/api/chats/${chatId}/typing-status?is_typing=${isTyping}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async updateChat(chatId, chatName) {
        try {
            return await apiClient.patch(`/api/chats/${chatId}`, {"name_group": chatName});
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async updateGroupImage(chatId, formData) {
        try {
            return await apiClient.patch(
                `/api/chats/${chatId}/upload-image`,
                formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    }
                }
            );
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async uploadAttachments(chatId, formData) {
        try {
            return await apiClient.post(
                `/api/chats/${chatId}/upload-attachments`,
                formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    }
                }
            );
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    }
};

export const messageService = {
    async fetchMessages(chatId, {cursor, size}) {
        try {
            const params = new URLSearchParams();
            if (cursor) params.append("cursor", cursor);
            if (size) params.append("size", size);
            return await apiClient.get(`/api/chats/${chatId}/messages?${params.toString()}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async fetchMessagesRange(chatId, fromId, toId) {
        try {
            const params = new URLSearchParams();
            params.append("from_id", fromId);
            params.append("to_id", toId);
            return await apiClient.get(`/api/chats/${chatId}/messages/range?${params.toString()}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async fetchDeletedMessages(chatId, {cursor, size}) {
        try {
            const params = new URLSearchParams();
            if (cursor) params.append("cursor", cursor);
            if (size) params.append("size", size);
            return await apiClient.get(`/api/chats/${chatId}/deleted-messages?${params.toString()}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async sendMessage(chatId, messageData) {
        try {
            return await apiClient.post(`/api/chats/${chatId}/messages`, messageData);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async updateMessage(chatId, messageId, messageData) {
        try {
            return apiClient.patch(`/api/chats/${chatId}/messages/${messageId}`, messageData);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async deleteMessage(chatId, messageId, deleteForever) {
        try {
            if (deleteForever) {
                return await apiClient.delete(`/api/chats/${chatId}/messages/${messageId}?is_forever=${deleteForever}`);
            }
            return await apiClient.delete(`/api/chats/${chatId}/messages/${messageId}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async sendLastMessage(chatId, messageContent) {
        try {
            return await apiClient.post(`/api/chats/${chatId}/draft-message`, {"content": messageContent});
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async updateLastMessage(chatId, messageContent) {
        try {
            return await apiClient.put(`/api/chats/${chatId}/draft-message`, {"content": messageContent});
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async deleteLastMessage(chatId) {
        try {
            return await apiClient.delete(`/api/chats/${chatId}/draft-message`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async postReaction(chatId, messageId, reactionType) {
        try {
            return apiClient.post(
                `/api/chats/${chatId}/messages/${messageId}/reaction`,
                {"reaction_type": reactionType}
            );
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async deleteReaction(chatId, messageId) {
        try {
            return apiClient.delete(
                `/api/chats/${chatId}/messages/${messageId}/reaction`,
            );
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async recoverMessage(chatId, messageId) {
        try {
            return await apiClient.post(`/api/chats/${chatId}/messages/${messageId}/recover`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async forwardMessage(fromChatId, toChatId, messages) {
        try {
            return apiClient.post(
                `/api/chats/${fromChatId}/messages/forward`,
                {
                    "to_chat_id": toChatId,
                    "messages": messages
                }
            );
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
}

export const userService = {
    async fetchUserDetails(userId) {
        try {
            return await apiClient.get(`/api/users/read/${userId}`);

        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async fetchUsers(size, pageCursor) {
        try {
            if (!pageCursor) {
                return await apiClient.get(`/api/users?size=${size}`)
            }
            return await apiClient.get(`/api/users?size=${size}&cursor=${pageCursor}`)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async fetchUserMe() {
        try {
            return await apiClient.get('/api/users/me')
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async deleteUserMe() {
        try {
            return await apiClient.delete('/api/users/me/delete')
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async recoverUserMe() {
        try {
            return await apiClient.post('/api/users/me/recover')
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async updateUserImage(userImageForm) {
        try {
            return await apiClient.patch(
                '/api/users/me/upload-image',
                userImageForm,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                })
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                this.$router.push("/");
            }
            throw error;
        }
    },
    async updateUserInfo(userForm) {
        try {
            return await apiClient.patch('/api/users/me', userForm)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                this.$router.push("/");
            }
            throw error;
        }
    },
};

export const readStatusService = {
    async updateReadStatus(chatId, readStatusData) {
        try {
            return await apiClient.patch(`/api/read_status/${chatId}/update`, readStatusData);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
};

export const aiService = {
    async postSummarization(chatId, duration) {
        const params = new URLSearchParams();
        params.append("chat_id", chatId);
        params.append("duration", duration);
        try {
            return await apiClient.post(`/api/ai/summarizations?${params.toString()}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async fetchSummarizations(status) {
        try {
            return await apiClient.get(`/api/ai/summarizations?summarization_status=${status}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async fetchSummarizationDetail(chatId) {
        try {
            return await apiClient.get(`/api/ai/summarizations/${chatId}`);
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    }
};

export const blackListService = {
    async fetchBlockedUsers(size, pageCursor) {
        try {
            if (!pageCursor) {
                return await apiClient.get(`/api/black-list?size=${size}`)
            }
            return await apiClient.get(`/api/black-list?size=${size}&cursor=${pageCursor}`)
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },

    async addToBlackList(userId) {
        try {
            return await apiClient.post('/api/black-list', {"user_id": userId});
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    },
    async removeFromBlackList(userId) {
        try {
            return await apiClient.delete('/api/black-list', {
                data: {user_id: userId},
            });
        } catch (error) {
            if (error.message === "Нет токена доступа") {
                await router.push("/");
            }
            throw error;
        }
    }
}

export const authService = {
    async loginUser(loginData) {
        return await apiClientWithoutAuth.post('/api/auth/jwt/login', loginData)
    },
    async registerUser(registerData) {
        return await apiClientWithoutAuth.post('/api/auth/register', registerData)
    }
}
