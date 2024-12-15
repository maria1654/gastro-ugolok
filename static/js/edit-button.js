function updateAccountLink() {
    if (isUserLoggedIn === "True" && currentPage === "/account") {
        document.getElementById('account-link').textContent = 'Выйти';
        document.getElementById('account-link').href = '/logout';
    }
}

function addEditButton() {
    if (userRole === "admin" && window.location.pathname.startsWith('/recipe')) {
        const urlParams = new URLSearchParams(window.location.search);
        const rid = urlParams.get('rid');
        if (rid) {
            const editButton = document.createElement('a');
            editButton.textContent = '📝';
            editButton.href = `/admin/recipe/edit/${rid}`;
            editButton.classList.add('edit-button');
            
            const tooltip = document.createElement('div');
            tooltip.textContent = 'Редактировать рецепт';
            tooltip.classList.add('custom-tooltip');
            editButton.appendChild(tooltip);
            
            document.body.appendChild(editButton);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateAccountLink();
    addEditButton();
});