const SSESummarizerManager = {
    connections: {},

    async connect_summarize(chatId, updateCallback) {
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
            console.warn(`SSE для суммаризации чата ${chatId} уже установлено.`);
            return;
        }
        const user = JSON.parse(localStorage.getItem("user"));
        if (!user) {
            this.$router.push('/login');
            alert("Пожалуйста, перезайдите в аккаунт");
            return;
        }
        const baseURL = process.env.VUE_APP_BACKEND_URL;
        const eventSource = new EventSource(
            `${baseURL}/api/ai/summarizations/stream?chat_id=${chatId}&token=${encodeURIComponent(token)}`
        );
        eventSource.addEventListener("progress_summarization", async (event) => {
            const summarization_data = JSON.parse(event.data);
            if (summarization_data) {
                updateCallback(summarization_data, "progress_summarization");
            }
        });
        eventSource.addEventListener("failed_summarization", async (event) => {
            const summarization_data = JSON.parse(event.data);
            if (summarization_data) {
                updateCallback(summarization_data, "failed_summarization");
            }
        });
        this.connections[chatId] = eventSource;
    },
    disconnect(chatId) {
        if (this.connections[chatId]) {
            this.connections[chatId].close();
            delete this.connections[chatId];
        }
    },
}
export default SSESummarizerManager;
