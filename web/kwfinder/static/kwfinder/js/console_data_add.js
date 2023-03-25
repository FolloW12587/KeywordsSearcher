import { datepicker } from './datepicker.js';

let params = {
    console: {
        isLoading: false,
        data: []
    },
    data: {
        to_save: [],
        isSaving: false
    },
    date_selected: datepicker.date.from
}

const table = document.getElementById("table");
const load_data_button = document.getElementById("load_data__button");
const save_data_button = document.getElementById("save_data__button");
const csrftoken = getCookie('csrftoken');

document.addEventListener("DOMContentLoaded", () => {
    datepicker.install("single");
    datepicker.render();

    load_data_button.addEventListener('click', loadData);
    save_data_button.addEventListener('click', saveData);
    updateButtons();

});

function updateTable() {
    if (params.console.isLoading) {
        updateButtons();
        params.data.to_save = [];
        removeAllTableRows();
        return
    }

    prepareDataToSave();
    params.data.to_save.forEach(data => {
        let row = document.createElement("tr");
        row.classList.add('row');
        let s = "";
        let keyword_name = keywords[data.keyword__id];
        s += `<td>${keyword_name}</td>`;

        s += `<td><input type="text" name="views" id="views_${data.keyword__id}" value="${data.views}"></td>`;
        s += `<td><input type="text" name="installs" id="installs_${data.keyword__id}" value="${data.installs}"></td>`;

        row.innerHTML = s;
        table.getElementsByTagName("tbody")[0].appendChild(row);
    });
    let views = document.getElementsByName("views");
    views.forEach(view_input => {
        view_input.addEventListener('change', viewsInputChanged);
    });
    let installs = document.getElementsByName("installs");
    installs.forEach(install_input => {
        install_input.addEventListener('change', installsInputChanged);
    });
    updateButtons();
}

function viewsInputChanged(e) {
    let target = e.currentTarget;

    let keyword_id = target.id.split("_")[1];
    params.data.to_save.forEach(data => {
        if (data.keyword__id != keyword_id) {
            return
        }
        let value = parseInt(target.value);
        if (isNaN(value)) {
            target.value = data.views;
            return;
        }
        target.value = value;
        data.views = value;
    });
}

function installsInputChanged(e) {
    let target = e.currentTarget;

    let keyword_id = target.id.split("_")[1];
    params.data.to_save.forEach(data => {
        if (data.keyword__id != keyword_id) {
            return
        }
        let value = parseInt(target.value);
        if (isNaN(value)) {
            target.value = data.installs;
            return;
        }
        target.value = value;
        data.installs = value;
    });
}

function prepareDataToSave() {
    for (let keyword_id in keywords) {
        let data_to_save = {
            "keyword__id": keyword_id,
            "date": params.date_selected.format("yyyy-mm-dd")
        };
        let keyword_info = params.console.data.filter(data => data.keyword == keyword_id)[0];
        if (keyword_info === undefined) {
            data_to_save["views"] = 0;
            data_to_save["installs"] = 0;
            params.data.to_save.push(data_to_save);
            continue
        }

        data_to_save["views"] = keyword_info.views;
        data_to_save["installs"] = keyword_info.installs;

        params.data.to_save.push(data_to_save);
    }
}

function updateButtons() {
    if (params.console.isLoading || params.data.isSaving) {
        load_data_button.disabled = true;
        save_data_button.disabled = true;
        return
    }

    load_data_button.disabled = false;
    if (params.data.to_save.length != 0) {
        save_data_button.disabled = false;
    }
}


function removeAllTableRows() {
    let rows = table.getElementsByClassName("row");
    while (rows.length > 0) {
        rows[0].remove();
    }
}

function loadData() {
    params.date_selected = datepicker.date.from;

    loadConsoleData();
}

async function saveData() {
    if (datepicker.date.from.format("yyyy-mm-dd") != params.date_selected.format("yyyy-mm-dd")){
        alert(`Данные загружены за период ${params.date_selected.format("yyyy-mm-dd")}, а выбранная дата стоит ${datepicker.date.from.format("yyyy-mm-dd")}! 
            Если дата загруженных данных верная, выберете ее и нажмите сохранить заново. 
            Если нет, сначала загрузите данные за нужный период!`);
        return;
    }
    console.log(params.data.to_save);
    updateButtons();
    params.data.isSaving = true;
    let data = {
        "data": params.data.to_save
    };

    let url = `.`;
    let response = await fetch(url, {
        method: "POST",
        body: JSON.stringify(data),
        credentials: "include",
        headers: { 'X-CSRFToken': csrftoken },
    })
        .then((response) => {
            return response.json();
        });

    params.data.isSaving = false;
    updateButtons();
    alert(JSON.stringify(response));
}

async function loadConsoleData() {
    if (params.console.isLoading) {
        console.log("Console data is already loading!");
        return
    }
    console.log("Console data is loading!");
    params.date_selected = datepicker.date.from;
    params.console.data = [];
    params.console.isLoading = true;
    updateTable();

    let url = `/console_data/?date=${params.date_selected.format("yyyy-mm-dd")}&app__id=${app_id}`;

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
    console.log(params);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}