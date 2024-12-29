import router from "@/router";

export async function handleError(error) {
    if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.message || error.response.data?.detail;

        switch (status) {
            case 403:
                if (message === "You are deleted.") {
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
                } else break;
            default:
                console.error("Неизвестная ошибка:", error);
        }
    } else {
        console.error("Ошибка:", error);
    }

    return "Произошла ошибка. Пожалуйста, попробуйте позже.";
}
