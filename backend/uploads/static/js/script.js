document.addEventListener('DOMContentLoaded', function() {
    // CSRF Token для AJAX
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Переключение между вкладками
    const menuItems = document.querySelectorAll('.menu li');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');

    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuItems.forEach(i => i.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            pageTitle.textContent = this.querySelector('span').textContent;
        });
    });

    // Drag and drop для загрузки файлов
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const filePreview = document.getElementById('file-preview');
    const selectFileBtn = document.getElementById('select-file-btn');
    const uploadForm = document.getElementById('upload-form');

    // Обработчики drag and drop
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
    selectFileBtn.addEventListener('click', () => fileInput.click());
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
                <i class="fas fa-file-${file.type.includes('audio') ? 'audio' : 'alt'}"></i>
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

    // Отправка формы
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const processBtn = document.getElementById('process-btn');

        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Файл успешно обработан!');
                window.location.reload();
            } else {
                throw new Error(data.message || 'Ошибка обработки файла');
            }
        })
        .catch(error => {
            alert(error.message);
        })
        .finally(() => {
            processBtn.disabled = false;
            processBtn.textContent = 'Обработать';
        });
    });

    // Удаление файлов
    document.querySelectorAll('.delete-file').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите удалить этот файл?')) {
                const fileId = this.getAttribute('data-file-id');

                fetch(`/delete-file/${fileId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.closest('.file-card').remove();
                    }
                });
            }
        });
    });

    // Поиск по файлам
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        document.querySelectorAll('.file-card').forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });

    // Вспомогательная функция
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
});