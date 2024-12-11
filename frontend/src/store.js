import {createStore} from 'vuex';
import {chatService} from "@/services/apiService";

const store = createStore({
        state: {
            chats: [],
            user: {},
            latestMessage: null,
            isChatOpenCallback: true,
        },
        mutations: {
            setChats(state, chats) {
                state.chats = chats;
            },

            setMessagesForChat(state, {chatId, messages}) {
                state.chatMessages = {
                    ...state.chatMessages, [chatId]: messages,
                };
            },

            updateChat(state, updatedChat) {
                const index = state.chats.findIndex((c) => c.id === updatedChat.id);
                if (index !== -1) {
                    state.chats[index] = {...updatedChat};
                }
            },

            addMessageToChat(state, {chatId, message}) {
                const chat = state.chats.find((chat) => chat.id === chatId);
                if (chat) {
                    chat.messages = chat.messages || [];
                    chat.messages.push(message);
                    chat.last_message = message.content;
                    chat.last_message_content = message.content;
                    chat.updated_at = message.created_at;
                    state.chats = state.chats.map(c => c.id === chatId ? {...chat} : c);
                }
            },

            setLatestMessage(state, {message, isChatOpenCallback}) {
                state.isChatOpenCallback = isChatOpenCallback
                if (!state.isChatOpenCallback) {
                    state.latestMessage = message;
                }
            },
        },

        actions: {
            async handleIncomingMessage({state, commit}, {chatId, message}) {
                try {
                    let chat = state.chats.find((chat) => chat.id === chatId);
                    if (chat) {
                        commit("addMessageToChat", {chatId, message});
                    } else {
                        console.error(`Chat with id ${chatId} not found.`);
                    }
                } catch (error) {
                    console.error(`Ошибка при обработке сообщения для чата ${chatId}:`, error);
                }
            },

            async StoreFetchChats({commit}, queryParams) {
                try {
                    const response = await chatService.fetchChats(queryParams);
                    const chats = response.data.items;
                    commit("setChats", chats);
                    return response;
                } catch (error) {
                    console.error("Ошибка при загрузке чатов:", error);
                    throw error;
                }
            },

            async StoreFetchChatDetail({commit}, chatId) {
                try {
                    const response = await chatService.fetchChatDetails(chatId);
                    const chat = [response.data];
                    commit("setChats", chat);
                    return response;
                } catch (error) {
                    console.error("Ошибка при загрузке чатов:", error);
                    throw error;
                }
            },

            receiveMessage({commit}, {message, isChatOpenCallback}) {
                commit("addMessageToChat", {
                    chatId: message.chat_id, message: message
                },)
                commit("setLatestMessage", {
                    message: message,
                    isChatOpenCallback: isChatOpenCallback
                })
            },
        },
        getters: {
            getChatById: (state) => (id) => state.chats.find((chat) => chat.id === id),
            latestMessage: (state) => {
                if (state.chats.length === 0) return null;
                if (state.isChatOpenCallback) return null;
                return state.chats
                    .flatMap(chat => chat.messages || [])
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
            },
        },
    }
);

export default store;
