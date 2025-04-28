document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".post-form form");
    const textarea = form.querySelector("textarea");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const content = textarea.value.trim();

        if (!content) {
            alert("Пост не может быть пустым!");
            return;
        }

        try {
            const response = await fetch("/profile/create_post", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ content }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText);
            }

            textarea.value = "";
            alert("Пост опубликован!");

        } catch (error) {
            console.error("Ошибка при создании поста:", error);
            alert("Ошибка при создании поста.");
        }
    });
});
