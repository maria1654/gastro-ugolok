function showCustomConfirm(message, onConfirm, onCancel) {
    const alertBox = document.getElementById('custom-alert');
    const alertContent = alertBox.querySelector('.alert-content');
    
    // Очищаем содержимое
    alertContent.innerHTML = '';
    
    // Добавляем сообщение
    const messageElement = document.createElement('p');
    messageElement.id = 'alert-message';
    messageElement.textContent = message;
    alertContent.appendChild(messageElement);
    
    // Создаем контейнер для кнопок
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'alert-buttons';
    
    // Создаем кнопку OK
    const okButton = document.createElement('button');
    okButton.textContent = 'OK';
    okButton.className = 'confirm-btn';
    okButton.addEventListener('click', () => {
        closeCustomAlert();
        if (onConfirm) onConfirm();
    });
    
    // Создаем кнопку Отмена
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Отмена';
    cancelButton.className = 'cancel-btn';
    cancelButton.addEventListener('click', () => {
        closeCustomAlert();
        if (onCancel) onCancel();
    });
    
    // Добавляем кнопки в контейнер
    buttonContainer.appendChild(okButton);
    buttonContainer.appendChild(cancelButton);
    
    // Добавляем контейнер с кнопками в алерт
    alertContent.appendChild(buttonContainer);
    
    // Показываем алерт
    alertBox.style.display = 'flex';
}

function closeCustomAlert() {
    const alertBox = document.getElementById('custom-alert');
    alertBox.style.display = 'none';
}