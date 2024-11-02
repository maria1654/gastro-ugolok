// cookie.js

function acceptCookies() {
    fetch("/accept_cookies", {
        method: "POST"
    })
    .then(response => {
        if (response.ok) {
            document.getElementById("cookie-banner").style.display = "none";
        }
    })
    .catch(error => console.error("Error:", error));
}

// Функция для получения значения cookie по имени
function getCookie(name) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

// Проверяем наличие cookie 'cookiesAccepted'
window.onload = function() {
    if (!getCookie('cookiesAccepted')) {
        const banner = document.getElementById("cookie-banner");
        if (banner) {
            setTimeout(() => {
                banner.style.display = "block";
            }, 2000);
        }
    }
};