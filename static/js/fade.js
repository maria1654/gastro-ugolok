document.addEventListener('DOMContentLoaded', function () {
    const fadeElements = document.querySelectorAll('.fade');

    // Функция для добавления класса "show"
    function fadeIn() {
        fadeElements.forEach(element => {
            element.classList.add('show');
        });
    }

    // Функция для удаления класса "show"
    function fadeOut(callback) {
        fadeElements.forEach(element => {
            element.classList.remove('show');
        });

        // Задержка перед вызовом коллбека
        setTimeout(callback, 500); // 500ms соответствует времени анимации в CSS
    }

    // Запускаем плавное появление при загрузке страницы
    fadeIn();

    // Обработка перехода по ссылкам
    document.querySelectorAll('a.navbutton').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Отменить стандартное поведение ссылки
            const targetUrl = this.href; // Сохранить URL ссылки

            // Запускаем плавное исчезновение
            fadeOut(() => {
                window.location.href = targetUrl; // Переход на новую страницу
            });
        });
    });
});
