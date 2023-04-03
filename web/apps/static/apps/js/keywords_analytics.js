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
    date_range_selected: datepicker.getDaysArray(),
}

const table = document.getElementById("table");
const table_header = table.querySelector(".header_row");
const load_data_button = document.getElementById("load_data__button");
const closeModalButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

document.addEventListener("DOMContentLoaded", () => {
    datepicker.install();
    datepicker.render();

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


function updateTable() {
    updateButtons();
    if (params.data.isLoading) {
        removeHeader();
        removeAllTableRows();
        return
    }

    prepareData();

    let header_s = `<th class="sticky">Ключевое слово</th>`;
    params.date_range_selected.forEach(date => {
        header_s += `<th>${date}</th>`;
    });
    table_header.innerHTML = header_s;

    params.data.keywords.forEach(keyword => {
        let info = params.data.rows[keyword.id];
        let row = document.createElement("tr");
        row.classList.add('row');
        let s = `<td class="sticky">${keyword.name}</rd>`;
        
        params.date_range_selected.forEach(date => {
            let data = info.filter(d => d.date == date);
            if (data.length == 0){
                s += `<td>-</td>`;
            } else {
                s += `<td>
                    <p style="text-align: center; margin-bottom: 5px;"><strong>${data[0].position} место</strong></p>
                    <p>${(data[0].views ? data[0].views : 0) - (data[0].aso_installs ? data[0].aso_installs : 0)} посещений</p>
                    <p>${(data[0].installs ? data[0].installs : 0) - (data[0].aso_installs ? data[0].aso_installs : 0)} установок</p>
                </td>`;
            }
        });

        row.innerHTML = s;

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
            }
            params.data.keywords.push(stored_keyword);
        } else {
            stored_keyword = stored_keyword[0];
        }

        if (params.data.rows[stored_keyword.id] == undefined) {
            params.data.rows[stored_keyword.id] = [];
        }
        params.data.rows[stored_keyword.id].push(info);
    });

}

function updateButtons() {
    if (params.data.isLoading) {
        load_data_button.disabled = true;
        return
    }

    load_data_button.disabled = false;
}


function removeAllTableRows() {
    let rows = table.getElementsByClassName("row");
    while (rows.length > 0) {
        rows[0].remove();
    }
}

function removeHeader() {
    table_header.innerHTML = "";
}

function loadData() {
    params.date_range_selected = datepicker.getDaysArray();

    removeHeader();
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
    updateButtons();

    let url = `/daily_data_joined/?date__gte=${params.date_range_selected[0]}&date__lte=${params.date_range_selected[params.date_range_selected.length - 1]}&app__id=${app_id}`;

    while (url) {
        let response = await fetch(url)
            .then((response) => {
                return response.json();
            });
        params.data.data = params.data.data.concat(response.results);
        url = response.next;
    }
    params.data.isLoading = false;
    console.log("Data is loaded!");
    console.log(params);
    if (params.data.data.length == 0) {
        alert("По выбранным параметрам нет данных!");
    }
    updateTable();
}
