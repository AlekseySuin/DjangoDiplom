document.addEventListener('DOMContentLoaded', function() {
    // Переключение между вкладками
    const menuItems = document.querySelectorAll('.menu li');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');

    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Удаляем активный класс у всех элементов
            menuItems.forEach(i => i.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Добавляем активный класс к выбранному элементу
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');

            // Обновляем заголовок страницы
            pageTitle.textContent = this.querySelector('span').textContent;
        });
    });

    // Drag and drop для загрузки файлов
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const filePreview = document.getElementById('file-preview');
    const processBtn = document.getElementById('process-btn');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('highlight');
    }

    function unhighlight() {
        dropZone.classList.remove('highlight');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFiles);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files } });
    }

    function handleFiles(e) {
        const files = e.target.files;
        if (files.length) {
            const file = files[0];
            displayFilePreview(file);
        }
    }

    function displayFilePreview(file) {
        filePreview.innerHTML = `
            <div class="file-preview-item">
                <i class="fas fa-file-alt"></i>
                <div>
                    <h4>${file.name}</h4>
                    <p>${formatFileSize(file.size)}</p>
                </div>
                <button class="btn-icon" id="remove-file"><i class="fas fa-times"></i></button>
            </div>
        `;
        filePreview.classList.add('active');

        document.getElementById('remove-file').addEventListener('click', () => {
            filePreview.innerHTML = '';
            filePreview.classList.remove('active');
            fileInput.value = '';
        });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    // Обработка файла
    processBtn.addEventListener('click', function() {
        if (!fileInput.files.length) {
            alert('Пожалуйста, выберите файл');
            return;
        }

        // Здесь будет вызов API для обработки файла
        alert('Файл отправлен на обработку');

        // Имитация обработки (для демонстрации)
        setTimeout(() => {
            alert('Обработка завершена! Результат доступен во вкладке "Мои файлы"');
        }, 3000);
    });
});