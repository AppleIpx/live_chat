import store from "@/store";
import {userService} from "@/services/apiService";

const SSEManager = {
    connections: {},

    async connect(chatId, isChatOpenCallback, messageCallback) {
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
        const user = await userService.fetchUserMe();
        const baseURL = process.env.VUE_APP_BACKEND_URL;
        const eventSource = new EventSource(
            `${baseURL}/api/chats/${chatId}/events?token=${encodeURIComponent(token)}`
        );

        eventSource.addEventListener("new_message", async (event) => {
            const message = JSON.parse(event.data);
            if (message.user_id !== user.data.id) {
                await store.dispatch("receiveMessage", {
                    message: message,
                    isChatOpenCallback: isChatOpenCallback
                });
                if (isChatOpenCallback) {
                    messageCallback(message, "new");
                }
            }
        });

        eventSource.addEventListener("delete_message", async (event) => {
            const message = JSON.parse(event.data);
            if (isChatOpenCallback) {
                messageCallback(message, "delete");
            }
        });

        eventSource.addEventListener("update_message", async (event) => {
            const message = JSON.parse(event.data);
            if (message.user_id !== user.data.id && isChatOpenCallback) {
                messageCallback(message, "update");
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
