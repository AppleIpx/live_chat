import router from "@/router";

export async function handleError(error) {
    if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.message || error.response.data?.detail;

        switch (status) {
            case 403:
                if (message.status === "banned") {
                    await router.push({
                        path: "/banned",
                        query: { reason: message.reason || "Причина не указана" },
                    });
                } else if (message === "You are deleted.") {
                    await router.push("/deleted");
                } else {
                    await router.push("/403");
                }
                break;
            case 404:
                await router.push("/404");
                break;
            case 500:
                await router.push("/500");
                break;
            case 400:
                if (message === "This user has been deleted.") {
                    await router.push("/another-deleted");
                    break;
                } else  if (message === "This user has been banned.") {
                    await router.push("/another-banned");
                    break;
                }
                else if (message === "You can't perform this action, you are on the black list") {
                    await router.push("/blocked");
                } else break;
                break
            default:
                console.error("Неизвестная ошибка:", error);
        }
    } else {
        console.error("Ошибка:", error);
    }
    return "Произошла ошибка. Пожалуйста, попробуйте позже.";
}
