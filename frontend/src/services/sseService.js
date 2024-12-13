import store from "@/store";
import {userService} from "@/services/apiService";

const SSEManager = {
    connections: {},

    async connect(
        chatId,
        isChatOpenCallback,
        messageCallback,
        typingCallback,
        groupCallback,
        readStatusCallback,
    ) {
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

        eventSource.addEventListener("recover_message", async (event) => {
            const message = JSON.parse(event.data);
            if (isChatOpenCallback) {
                messageCallback(message, "recover");
            }
        });

        eventSource.addEventListener("update_message", async (event) => {
            const message = JSON.parse(event.data);
            if (message.user_id !== user.data.id && isChatOpenCallback) {
                messageCallback(message, "update");
            }
        });

        eventSource.addEventListener("user_typing", async (event) => {
            const typing_status = JSON.parse(event.data);
            if (typing_status.user_id !== user.data.id && isChatOpenCallback) {
                typingCallback(typing_status)
            }
        });

        eventSource.addEventListener("update_group_name", async (event) => {
            const group_data = JSON.parse(event.data);
            if (isChatOpenCallback) {
                groupCallback(group_data, "name");
            }
        });

        eventSource.addEventListener("update_image_group", async (event) => {
            const group_data = JSON.parse(event.data);
            if (isChatOpenCallback) {
                groupCallback(group_data, "image");
            }
        });

        eventSource.addEventListener("update_read_status", async (event) => {
            const readStatusData = JSON.parse(event.data);
            if (isChatOpenCallback) {
                readStatusCallback(readStatusData);
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
