document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("register-form");

    registerForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const nameInput = registerForm.elements["name"];
        const emailInput = registerForm.elements["email"];
        const passwordInput = registerForm.elements["password"];
        const ageInput = registerForm.elements["age"];

        let isValid = true;

        const namePattern = /^[A-ZА-Я]?[a-zа-я]{5,30}$/;
        if (!namePattern.test(nameInput.value)) {
            showError(nameInput, "Имя должно содержать только буквы (от 5 до 30) и максимум одну заглавную.");
            isValid = false;
        } else {
            clearError(nameInput);
        }

        const emailPattern = /^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
        if (!emailPattern.test(emailInput.value)) {
            showError(emailInput, "Введите корректный email.");
            isValid = false;
        } else {
            clearError(emailInput);
        }

        const passwordPattern = /^[a-zA-Z0-9%&*#$!]{10,}$/;
        if (!passwordPattern.test(passwordInput.value)) {
            showError(passwordInput, "Пароль должен содержать только буквы, цифры и символы %&*#$! и иметь длину не менее 10 символов.");
            isValid = false;
        } else {
            clearError(passwordInput);
        }

        const age = parseInt(ageInput.value, 10);
        if (isNaN(age) || (age >= 14 && age <= 150)) {
            clearError(ageInput);
        } else {
            showError(ageInput, "Возраст должен быть от 14 до 150 лет.");
            isValid = false;
        }

        if (isValid) {
            const formData = {
                name: nameInput.value,
                email: emailInput.value,
                password: passwordInput.value,
                age: ageInput.value
            };

            fetch("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            })
            .catch(error => {
                console.error("Ошибка:", error);
            });
        }
    });

    function showError(input, message) {
        input.classList.add("error");
        let errorText = input.nextElementSibling;
        if (!errorText || !errorText.classList.contains("error-text")) {
            errorText = document.createElement("div");
            errorText.classList.add("error-text");
            input.parentNode.appendChild(errorText);
        }
        errorText.textContent = message;
    }

    function clearError(input) {
        input.classList.remove("error");
        const errorText = input.nextElementSibling;
        if (errorText && errorText.classList.contains("error-text")) {
            errorText.remove();
        }
    }
});
