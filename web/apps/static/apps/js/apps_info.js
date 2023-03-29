
const button = document.querySelector(".toggle_banned_button");
const banned_apps = document.querySelectorAll('[data-attribute="banned"]');

document.addEventListener("DOMContentLoaded", () => {
    button.addEventListener('click', toggle_banned);
});

function toggle_banned() {
    button.classList.toggle("active");
    banned_apps.forEach(app => {
        app.classList.toggle("hidden");
    })
}