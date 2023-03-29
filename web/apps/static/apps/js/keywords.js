
const buttons = document.querySelectorAll("[data-ask-to-delete]");
const closeModalButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

document.addEventListener("DOMContentLoaded", () => {
    buttons.forEach(button => {
        button.addEventListener('click', delete_button_clicked);
    })

    overlay.addEventListener('click', closeAllModals);

    closeModalButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal')
            closeModal(modal)
        })
    })
});

function closeAllModals() {
    const modals = document.querySelectorAll('.modal.active')
    modals.forEach(modal => {
        closeModal(modal)
    })
}

function closeModal(modal) {
    if (modal == null) return
    modal.classList.remove('active')
    overlay.classList.remove('active')
}

function openModal(modal) {
    if (modal == null) return
    modal.classList.add('active')
    overlay.classList.add('active')
}

function delete_button_clicked(e) {
    let modal = document.querySelector("#modal");
    let modalBody = modal.querySelector(".modal-body");

    let currentTarget = e.currentTarget;
    let keyword_id = currentTarget.getAttribute("data-id");
    let row = currentTarget.closest(".row");

    let tds = row.querySelectorAll('td');
    let keyword_name = tds[0].innerText;
    let keyword_region = tds[1].innerText;

    let s = `<div>Вы действительно хотите отвязать ключ <strong>${keyword_name}</strong> региона <strong>${keyword_region}</strong> от текущего приложения?</div>`;
    s += `<div style="margin-top: 5px; width: 100%;"><button class="delete_button" data-confirm-delete data-id="${keyword_id}" style="margin-left: auto; display: block;">Удалить</button></div>`

    modalBody.innerHTML = s;
    modalBody.querySelector("[data-confirm-delete]").addEventListener("click", confirm_delete_clicked);

    openModal(modal);
}

function confirm_delete_clicked(e) {
    let currentTarget = e.currentTarget;
    let keyword_id = currentTarget.getAttribute("data-id");
    
    let link = `${keyword_id}/remove/`;
    closeAllModals();
    window.location.href = window.location.href + link;
}