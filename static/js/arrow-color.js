function getDominantColor(imgElement, callback) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = imgElement.naturalWidth;
    canvas.height = imgElement.naturalHeight;

    // Рисуем изображение на canvas
    context.drawImage(imgElement, 0, 0);

    // Получаем данные пикселей
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // Находим центр изображения
    const centerX = Math.floor(canvas.width / 2);
    const centerY = Math.floor(canvas.height / 2);
    const radius = 100;

    // Подсчитываем цвета
    const colorCount = {};
    let dominantColor = null;
    let maxCount = 0;

    // Считаем пиксели в радиусе 50px от центра
    for (let y = -radius; y <= radius; y++) {
        for (let x = -radius; x <= radius; x++) {
            const distance = Math.sqrt(x * x + y * y);
            if (distance <= radius) { // Проверяем, находится ли точка в радиусе
                const pixelX = centerX + x;
                const pixelY = centerY + y;

                // Проверяем, не выходит ли за пределы
                if (pixelX >= 0 && pixelX < canvas.width && pixelY >= 0 && pixelY < canvas.height) {
                    const index = (pixelY * canvas.width + pixelX) * 4;
                    const r = data[index];
                    const g = data[index + 1];
                    const b = data[index + 2];
                    const rgb = `${r},${g},${b}`;

                    // Считаем количество каждого цвета
                    colorCount[rgb] = (colorCount[rgb] || 0) + 1;

                    // Находим преобладающий цвет
                    if (colorCount[rgb] > maxCount) {
                        maxCount = colorCount[rgb];
                        dominantColor = rgb;
                    }
                }
            }
        }
    }

    callback(dominantColor);
}

document.addEventListener('DOMContentLoaded', () => {
    const imgCards = document.querySelectorAll('.imgBox img');

    imgCards.forEach((img) => {
        img.addEventListener('load', () => {
            getDominantColor(img, (dominantColor) => {
                const iconBox = img.closest('.box').querySelector('.iconBox');
                iconBox.style.background = `rgb(${dominantColor})`;

                // Разбиваем цвет на компоненты
                const [r, g, b] = dominantColor.split(',').map(Number);

                // Вычисляем более светлый цвет для тени
                const shadowColor = `rgba(${Math.max(r - 50, 0)}, ${Math.max(g - 50, 0)}, ${Math.max(b - 50, 0)}, 0.3)`;
                iconBox.style.boxShadow = `0 0em 0.2em 0.1em ${shadowColor}`;
            });
        });

        // Предварительная загрузка изображения
        if (img.complete) {
            img.dispatchEvent(new Event('load'));
        }
    });
});