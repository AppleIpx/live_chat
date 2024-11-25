import store from "@/store";

const SSEManager = {
    connections: {},

    connect(chatId, isChatOpenCallback) {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            console.error("Token not found");
            return;
        }

        if (!chatId) {
            console.warn(`Не пришел chat_id = ${chatId}.`);
            return;
        }

        if (this.connections[chatId]) {
            console.warn(`SSE для чата ${chatId} уже установлено.`);
            return;
        }

        const baseURL = process.env.VUE_APP_BACKEND_URL;
        console.log("test", chatId)
        const eventSource = new EventSource(
            `${baseURL}/api/chats/${chatId}/events/?token=${encodeURIComponent(token)}`
        );

        eventSource.addEventListener("new_message", async (event) => {
            const message = JSON.parse(event.data);
            console.log("message", message)
            const user = localStorage.getItem("user");

            if (message.user_id !== user.id) {
                if (isChatOpenCallback && isChatOpenCallback(chatId)) {
                    console.log("Чат открыт, уведомление пропущено.");
                    return;
                }

                await store.dispatch("receiveMessage", message);
                const chat = store.getters.getChatById(chatId);
                if (chat) {
                    chat.last_message = message.content;
                    chat.updated_at = message.created_at;
                    store.commit("updateChat", chat);
                }
            }
        });

        eventSource.onerror = () => {
            console.log(`SSE для чата ${chatId} отключено. Переподключение...`);
            setTimeout(() => this.connect(chatId, isChatOpenCallback), 5000);
        };

        this.connections[chatId] = eventSource;
    },

    disconnect(chatId) {
        if (this.connections[chatId]) {
            this.connections[chatId].close();
            delete this.connections[chatId];
        }
    },

    disconnectAll() {
        Object.keys(this.connections).forEach((chatId) => {
            this.disconnect(chatId);
        });
    },
};

export default SSEManager;
