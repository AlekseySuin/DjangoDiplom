document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    const submitButton = document.getElementById('submit-button');
    const buttonText = document.getElementById('button-text');
    const spinner = document.getElementById('spinner');
    const successAlert = document.getElementById('success-alert');
    const errorAlert = document.getElementById('error-alert');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // Показываем спиннер и меняем текст кнопки
        buttonText.textContent = 'Обработка...';
        spinner.style.display = 'inline-block';
        submitButton.disabled = true;

        // Создаем FormData для отправки файла
        const formData = new FormData(form);

        // Отправляем данные на сервер
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Ошибка при обработке файла');
            }
        })
        .then(data => {
            // Успешная обработка
            successAlert.style.display = 'block';
            errorAlert.style.display = 'none';
        })
        .catch(error => {
            // Ошибка
            console.error(error);
            errorAlert.style.display = 'block';
            successAlert.style.display = 'none';
        })
        .finally(() => {
            // Восстанавливаем кнопку
            buttonText.textContent = 'Загрузить и обработать';
            spinner.style.display = 'none';
            submitButton.disabled = false;
        });
    });
});