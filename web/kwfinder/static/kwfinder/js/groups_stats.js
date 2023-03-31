import { datepicker } from '/static/kwfinder/js/datepicker.js';

let params = {
    data: {
        isLoading: false,
        data: [],
        keywords: [],
        rows: {}
    },
    group_selected: null,
    region_selected: null,
    date_selected: datepicker.date.from,
}

const table = document.getElementById("table");
const load_data_button = document.getElementById("load_data__button");
const group = document.getElementById("group");
const region = document.getElementById("region");
const closeModalButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

document.addEventListener("DOMContentLoaded", () => {
    datepicker.install("single");
    datepicker.render();

    group.addEventListener('change', groupChange);
    region.addEventListener('change', regionChange);
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

function groupChange(e) {
    params.group_selected = group.value;
    updateButtons();
}

function regionChange(e) {
    params.region_selected = region.value;
    updateButtons();
}

function updateTable() {
    if (isLoadingOrParamsNotSelected()) {
        removeAllTableRows();
        return
    }

    prepareData();

    params.data.keywords.forEach(keyword => {
        let info = params.data.rows[keyword.id];
        let row = document.createElement("tr");
        row.classList.add('row');

        let s = `<td>${keyword.name}</td><td>${keyword.installs}</td>`;

        for (let pos = 1; pos < 11; pos++) {
            let app_info = info.filter(app_info => app_info.position == pos);
            if (app_info.length == 0) {
                s += '<td style="width: 66px;">-</td>';
                continue;
            }

            app_info = app_info[0];
            if (app_info.app.icon) {
                let img = `<img src="${app_info.app.icon}" width="50" height="50">`;
                s += `<td style="width: 66px;">
                <div class="app_cell tooltip" data-id="${app_info.app.id}">
                    ${img}
                    <span class="tooltiptext">${app_info.app.num} </span>
                </div></td>`;
            } else {
                s += s += `<td style="width: 66px;">
                <div class="app_cell" data-id="${app_info.app.id}">
                    ${app_info.app.num} 
                </div></td>`;
            }
        }

        row.innerHTML = s;

        let app_cells = row.querySelectorAll(".app_cell");
        app_cells.forEach(app_cell => {
            app_cell.addEventListener('mouseover', appCellHovered);
            app_cell.addEventListener('mouseout', appCellUnHovered);
        })
        table.getElementsByTagName("tbody")[0].appendChild(row);
    })
}

function prepareData() {
    params.data.keywords = [];
    params.data.rows = {};

    params.data.data.forEach(info => {
        let keyword = info.keyword;
        let stored_keyword = params.data.keywords.filter(k => k.id == keyword.id);
        if (stored_keyword.length == 0) {
            stored_keyword = {
                id: keyword.id,
                name: keyword.name,
                installs: 0
            }
            params.data.keywords.push(stored_keyword);
        }

        stored_keyword.installs += info.installs ? info.installs : 0
        if (params.data.rows[stored_keyword.id] == undefined) {
            params.data.rows[stored_keyword.id] = [];
        }
        params.data.rows[stored_keyword.id].push(info);
    });

    params.data.keywords.sort((a, b) => b.installs - a.installs);
}

function appCellHovered(e) {
    let target = e.currentTarget;
    let app_id = target.getAttribute("data-id");
    
    let app_cells = table.querySelectorAll(`.app_cell[data-id="${app_id}"]`);
    app_cells.forEach(app_cell => {
        app_cell.classList.add("highlighted");
    });
}

function appCellUnHovered(e) {
    let target = e.currentTarget;
    let app_id = target.getAttribute("data-id");
    
    let app_cells = table.querySelectorAll(`.app_cell[data-id="${app_id}"]`);
    app_cells.forEach(app_cell => {
        app_cell.classList.remove("highlighted");
    });
}

function updateButtons() {
    if (isLoadingOrParamsNotSelected()) {
        load_data_button.disabled = true;
        return
    }

    load_data_button.disabled = false;
}

function isLoadingOrParamsNotSelected() {
    return params.data.isLoading || !params.region_selected || !params.group_selected
}

function removeAllTableRows() {
    let rows = table.getElementsByClassName("row");
    while (rows.length > 0) {
        rows[0].remove();
    }
}

function loadData() {
    params.date_selected = datepicker.date.from;

    removeAllTableRows();
    loadTableData();
}

async function loadTableData() {
    if (params.data.isLoading) {
        console.log("Data is already loading!");
        return
    }
    console.log("Console data is loading!");
    params.data.data = [];
    params.data.isLoading = true;

    let url = `/daily_data_joined/?date=${params.date_selected.format("yyyy-mm-dd")}&app__group=${params.group_selected}&keyword__region=${params.region_selected}&position__lte=10&position__gte=1`;

    let response = await fetch(url)
        .then((response) => {
            return response.json();
        });
    params.data.data = response;
    params.data.isLoading = false;
    console.log("Data is loaded!");
    console.log(params);
    if (params.data.data.length == 0) {
        alert("По выбранным параметрам нет данных!");
    }
    updateTable();
}