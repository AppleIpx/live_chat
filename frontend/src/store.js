import {createStore} from 'vuex';
import {chatService} from "@/services/apiService";

const store = createStore({
        state: {
            chats: [],
            user: {},
            latestMessage: null,
        },
        mutations: {
            setChats(state, chats) {
                state.chats = chats;
            }, setMessagesForChat(state, {chatId, messages}) {
                state.chatMessages = {
                    ...state.chatMessages, [chatId]: messages,
                };
            }, updateChat(state, updatedChat) {
                const index = state.chats.findIndex((c) => c.id === updatedChat.id);
                if (index !== -1) {
                    state.chats.splice(index, 1, updatedChat);
                }
            }, addMessageToChat(state, {chatId, message}) {
                const chat = state.chats.find((chat) => chat.id === chatId);
                if (chat) {
                    console.log("messages in chat", chat.messages)
                    chat.messages = chat.messages || [];
                    chat.messages.push(message);
                    chat.last_message_content = message.content;
                    chat.updated_at = message.created_at;
                }
            }, setLatestMessage(state, message) {
                state.latestMessage = message;
            },
        },
        actions: {
            async handleIncomingMessage({state, commit}, {chatId, message}) {
                try {
                    let chat = state.chats.find((chat) => chat.id === chatId);
                    chat = await chatService.fetchChatDetails(chatId);
                    commit("setChats", [...state.chats, chat]);
                    commit("addMessageToChat", {chatId, message});
                } catch (error) {
                    console.error(`Ошибка при обработке сообщения для чата ${chatId}:`, error);
                }
            }, async StoreFetchChats({commit}) {
                try {
                    const response = await chatService.fetchChats();
                    commit("setChats", response.data.chats);
                    return response;
                } catch (error) {
                    console.error("Ошибка при загрузке чатов:", error);
                    throw error;
                }
            }, receiveMessage({commit}, message) {
                commit("addMessageToChat", {
                    chatId: message.chat_id, message: message
                },)
                commit("setLatestMessage", message)
            },
        },
        getters: {
            getChatById: (state) => (id) => state.chats.find((chat) => chat.id === id),
            latestMessage: (state) => {
                if (state.chats.length === 0) return null;
                return state.chats
                    .flatMap(chat => chat.messages || [])
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
            },
        },
    }
);

export default store;
