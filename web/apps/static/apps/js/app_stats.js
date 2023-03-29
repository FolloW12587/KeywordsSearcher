import { datepicker } from '/static/kwfinder/js/datepicker.js';

let params = {
    keitaro: {
        isLoading: false,
        data: []
    },
    our: {
        isLoading: false,
        data: []
    },
    console: {
        isLoading: false,
        data: []
    },
    asoworld: {
        isLoading: false,
        data: []
    },
    keyword_selected: null,
    date_range: []
}

const table = document.getElementById("table");
const load_data_button = document.getElementById("load_data__button");
const keyword = document.getElementById("keyword");
const closeModalButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

document.addEventListener("DOMContentLoaded", () => {
    datepicker.render();

    keyword.addEventListener('change', keywordChange);
    load_data_button.addEventListener('click', loadData);

    overlay.addEventListener('click', () => {
        const modals = document.querySelectorAll('.modal.active')
        modals.forEach(modal => {
            closeModal(modal)
        })
    })

    closeModalButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal')
            closeModal(modal)
        })
    })
});

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

async function loadPositionData(date) {
    let modal = document.getElementById("modal-keyword");
    let modalBody = modal.getElementsByClassName("modal-body")[0];
    modalBody.innerHTML = '<img class="spinner" src="/static/kwfinder/img/spinner.gif" style="margin: 0 auto;">';
    openModal(modal);
    modal.getElementsByClassName("title")[0].innerHTML = date;

    let url = `/position_data/?app__id=${app_id}&keyword__id=${params.keyword_selected}&date=${date}&ordering=run__started_at`;
    let response = await fetch(url)
        .then((response) => {
            return response.json();
        });

    let results = response.results;
    let s = "";
    for (var i = 0; i < results.length; i++) {
        s += `<div>${results[i].datetime}: ${results[i].position}</div>`;
    }

    modalBody.innerHTML = s;
}

function keywordChange(e) {
    params.keyword_selected = keyword.value;
    updateButtons();
}

function updateTable() {
    updateStates();
    if (isLoadingOrKeywordNotSelected()) {
        removeAllTableRows();
        return
    }

    params.date_range.forEach(day => {
        let row = document.createElement("tr");
        row.classList.add('row');
        let s = `<td>${day}</td>`;

        let keitaro_data = params.keitaro.data.filter(data => data.date == day);
        if (keitaro_data.length == 0) {
            s += `<td>-</td><td>-</td><td>-</td>`;
            if (can_see_keitaro_revenue) {
                s += "<td>-</td>"
            }
        } else {
            keitaro_data = keitaro_data[0];
            s += `<td>${keitaro_data.unique_users_count}</td><td>${keitaro_data.conversions_count}</td>
                <td>${keitaro_data.sales_count}</td>`;
            if (can_see_keitaro_revenue) {
                s += `<td>${keitaro_data.revenue}</td>`;
            }
        }

        let our_data = params.our.data.filter(data => data.date == day);
        if (our_data.length == 0) {
            s += `<td>-</td>`;
        } else {
            our_data = our_data[0];
            s += `<td>${our_data.position}</td>`;
        }
        
        let console_data = params.console.data.filter(data => data.date == day);
        if (console_data.length == 0) {
            s += `<td>-</td><td>-</td><td>-</td>`;
        } else {
            console_data = console_data[0];
            s += `<td>${console_data.views}</td><td>${console_data.installs}</td>
                <td>${console_data.conversion}%</td>`;
        }

        let asoworld_data = params.asoworld.data.filter(data => data.date == day);

        let asoworld_installs = asoworld_data.reduce((prev, current) => prev += current.installs, 0);
        s += `<td>${asoworld_installs}</td>`;

        row.innerHTML = s;
        row.addEventListener('click', e => {
            loadPositionData(day);
        })
        table.getElementsByTagName("tbody")[0].appendChild(row);
    })
}

function updateButtons() {
    if (isLoadingOrKeywordNotSelected()) {
        load_data_button.disabled = true;
        keyword.disabled = true;
        return
    }

    load_data_button.disabled = false;
    keyword.disabled = false;
}

function isLoadingOrKeywordNotSelected() {
    return isLoading() || !params.keyword_selected
}

function isLoading() {
    return params.keitaro.isLoading || params.our.isLoading || params.console.isLoading || params.asoworld.isLoading
}

function removeAllTableRows() {
    let rows = table.getElementsByClassName("row");
    while (rows.length > 0) {
        rows[0].remove();
    }
}

function loadData() {
    params.date_range = datepicker.getDaysArray().reverse()
    removeAllTableRows();
    resetStates();
    loadKeitaroData();
    loadConsoleData();
    loadOurData();
    loadASOWorldData();
}

function resetStates() {
    let states = document.getElementsByClassName("load_state");
    for (var i = 0; i < states.length; i++) {
        let state = states[0];
        state.innerHTML = "...";
    }

    let loading_info = document.getElementsByClassName("loading_info")[0];
    loading_info.classList.remove("hidden");
}

function updateStates() {
    if (!params.keitaro.isLoading) {
        let keitaro_data_load_state = document.getElementsByClassName("keitaro_data_load_state")[0];
        keitaro_data_load_state.innerHTML = "+";
    }

    if (!params.our.isLoading) {
        let our_data_load_state = document.getElementsByClassName("our_data_load_state")[0];
        our_data_load_state.innerHTML = "+";
    }

    if (!params.console.isLoading) {
        let console_data_load_state = document.getElementsByClassName("console_data_load_state")[0];
        console_data_load_state.innerHTML = "+";
    }

    if (!params.asoworld.isLoading) {
        let asoworld_data_load_state = document.getElementsByClassName("asoworld_data_load_state")[0];
        asoworld_data_load_state.innerHTML = "+";
    }

    if (!isLoading()) {
        updateButtons();
        let loading_info = document.getElementsByClassName("loading_info")[0];
        loading_info.classList.add("hidden");
    }
}

async function loadKeitaroData() {
    if (params.keitaro.isLoading) {
        console.log("Keitaro data is already loading!");
        return
    }
    console.log("Keitaro data is loading!");
    params.keitaro.data = [];
    params.keitaro.isLoading = true;

    let url = `/keitaro_data/?ordering=-date&date__gte=${datepicker.date.from.format("yyyy-mm-dd")}&date__lte=${datepicker.date.to.format("yyyy-mm-dd")}&app__id=${app_id}`;

    while (url) {
        let response = await fetch(url)
            .then((response) => {
                return response.json();
            });
        params.keitaro.data = params.keitaro.data.concat(response.results);
        url = response.next;
    }
    params.keitaro.isLoading = false;
    console.log("Keitaro data is loaded!");
    updateTable();
}

async function loadConsoleData() {
    if (params.console.isLoading) {
        console.log("Console data is already loading!");
        return
    }
    console.log("Console data is loading!");
    params.console.data = [];
    params.console.isLoading = true;

    let url = `/console_data/?ordering=-date&date__gte=${datepicker.date.from.format("yyyy-mm-dd")}&date__lte=${datepicker.date.to.format("yyyy-mm-dd")}&app__id=${app_id}&keyword__id=${params.keyword_selected}`;

    while (url) {
        let response = await fetch(url)
            .then((response) => {
                return response.json();
            });
        params.console.data = params.console.data.concat(response.results);
        url = response.next;
    }
    params.console.isLoading = false;
    console.log("Console data is loaded!");
    updateTable();
}

async function loadOurData() {
    if (params.our.isLoading) {
        console.log("Our data is already loading!");
        return
    }
    console.log("Our data is loading!");
    params.our.data = [];
    params.our.isLoading = true;

    let url = `/daily_data/?ordering=-date&date__gte=${datepicker.date.from.format("yyyy-mm-dd")}&date__lte=${datepicker.date.to.format("yyyy-mm-dd")}&app__id=${app_id}&keyword__id=${params.keyword_selected}`;

    while (url) {
        let response = await fetch(url)
            .then((response) => {
                return response.json();
            });
        params.our.data = params.our.data.concat(response.results);
        url = response.next;
    }
    params.our.isLoading = false;
    console.log("Our data is loaded!");
    updateTable();
}

async function loadASOWorldData() {
    if (params.asoworld.isLoading) {
        console.log("ASO World data is already loading!");
        return
    }
    console.log("ASO World data is loading!");
    params.asoworld.data = [];
    params.asoworld.isLoading = true;

    let url = `/asoworld_data/?ordering=-date&date__gte=${datepicker.date.from.format("yyyy-mm-dd")}&date__lte=${datepicker.date.to.format("yyyy-mm-dd")}&order__app__id=${app_id}&keyword__id=${params.keyword_selected}`;

    while (url) {
        let response = await fetch(url)
            .then((response) => {
                return response.json();
            });
        params.asoworld.data = params.asoworld.data.concat(response.results);
        url = response.next;
    }
    params.asoworld.isLoading = false;
    console.log("ASO World data is loaded!");
    updateTable();
}