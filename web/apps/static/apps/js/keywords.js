
const buttons = document.querySelectorAll("[data-ask-to-delete]");
const closeModalButtons = document.querySelectorAll('[data-close-button]');
const keyword_positions = document.querySelectorAll('.keyword_position');

const delete_modal = document.querySelector("#delete-modal");
const history_modal = document.querySelector("#history-modal");
const overlay = document.getElementById('overlay');
let chart = null;

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
    keyword_positions.forEach(position => {
        position.addEventListener('click', keywordPositionClicked);
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
    let modalBody = delete_modal.querySelector(".modal-body");

    let currentTarget = e.currentTarget;
    let row = currentTarget.closest(".row");
    let keyword_id = row.getAttribute("data-id");

    let tds = row.querySelectorAll('td');
    let keyword_name = tds[0].innerText;
    let keyword_region = tds[1].innerText;

    let s = `<div>Вы действительно хотите отвязать ключ <strong>${keyword_name}</strong> региона <strong>${keyword_region}</strong> от текущего приложения?</div>`;
    s += `<div style="margin-top: 5px; width: 100%;"><button class="delete_button" data-confirm-delete data-id="${keyword_id}" style="margin-left: auto; display: block;">Удалить</button></div>`

    modalBody.innerHTML = s;
    modalBody.querySelector("[data-confirm-delete]").addEventListener("click", confirm_delete_clicked);

    openModal(delete_modal);
}

function confirm_delete_clicked(e) {
    let currentTarget = e.currentTarget;
    let keyword_id = currentTarget.getAttribute("data-id");

    let link = `${keyword_id}/remove/`;
    closeAllModals();
    window.location.href = window.location.href + link;
}

function keywordPositionClicked(e) {
    let currentTarget = e.currentTarget;
    let row = currentTarget.closest(".row");
    let keyword_id = row.getAttribute("data-id");

    if (!keyword_id) {
        return;
    }

    if (chart !== null) {
        chart.destroy();
        chart = null;
    }

    let modalBody = history_modal.querySelector(".modal-body");
    modalBody.innerHTML = `<img class="spinner" src="/static/kwfinder/img/spinner.gif" style="margin: 0 auto;">`;
    openModal(history_modal);

    getKeywordPositionHistory(keyword_id);
}

async function getKeywordPositionHistory(keyword_id) {
    const url = `/position_data/?app__id=${app_id}&keyword__id=${keyword_id}&limit=20&ordering=-run__started_at`;

    let response = await fetch(url)
        .then((response) => {
            return response.json();
        });

    createHistortyChart(response.results);
}

function createHistortyChart(data) {
    data.reverse();

    let labels = [];
    let positions = [];

    data.forEach(d => {
        labels.push(d.datetime.slice(0, 10));
        if (d.position != 0) {
            positions.push(d.position);
        } else {
            positions.push(NaN);
        }
    });

    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'History',
                data: positions
            }]
        },
        options: {
            scales: {
                y: {
                    suggestedMin: 1,
                    reverse: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
        }
    };

    let modalBody = history_modal.querySelector(".modal-body");
    modalBody.innerHTML = "";

    let chart_holder = document.createElement("div");
    chart_holder.classList.add("chart_holder");
    chart_holder.classList.add("position_history--chart");
    let canvas = document.createElement('canvas');
    canvas.classList.add('chart');

    chart_holder.appendChild(canvas);
    modalBody.appendChild(chart_holder);

    chart = new Chart(
        canvas,
        config
    );
}