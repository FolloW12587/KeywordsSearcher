import { datepicker } from './datepicker.js';

let params = {
    apps: {
        list: [],
        chosen: []
    },
    keywords: {
        list: [],
        chosen: [],
        count: 0,
        next: null,
        previous: null,
        isLoading: false,
        limit: 10,
        // filter: ""
    },
    stata: {
        list: [],
        labels: [],
        isLoading: false,
        states: {},
        chart: null
    }
}

const closeModalButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

document.addEventListener("DOMContentLoaded", () => {
    let settingsOpener = document.getElementsByClassName("settings--opener")[0];
    settingsOpener.addEventListener("click", toggleSettings);

    let applySettingsObj = document.getElementsByClassName("apply_settings")[0];
    applySettingsObj.addEventListener("click", applySettings);

    let appInput = document.getElementsByClassName("app_finder")[0];
    appInput.addEventListener("focus", toggleAppSearch);
    appInput.addEventListener("blur", toggleAppSearch);
    appInput.addEventListener("input", inputAppSearch);

    let keywordInput = document.getElementsByClassName("keyword_finder")[0];
    keywordInput.addEventListener("focus", toggleKeywordSearch);
    keywordInput.addEventListener("blur", toggleKeywordSearch);
    keywordInput.addEventListener("input", inputKeywordSearch);

    installDatepicker();
    let showData = document.getElementsByClassName("show_data")[0];
    showData.addEventListener('click', showStats);

    let offset_picker_slider = document.getElementsByClassName("offset_picker--slider")[0];
    offset_picker_slider.addEventListener("mouseup", inputSlider);

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
    // setupCharts();
    setChooseAppEvents();
});

function toggleSettings() {
    let settingsOpener = document.getElementsByClassName("settings--opener")[0];
    let settingsObj = document.getElementsByClassName("settings")[0];

    if (settingsOpener.classList.contains("settings--opener__active")) {
        settingsOpener.classList.remove("settings--opener__active");
        if (!settingsObj.classList.contains('settings__hidden')) {
            settingsObj.classList.add('settings__hidden');
        }
    } else {
        settingsOpener.classList.add("settings--opener__active");
        if (settingsObj.classList.contains('settings__hidden')) {
            settingsObj.classList.remove('settings__hidden');
        }
    }
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

// apply settings 

function applySettings() {

    params.keywords.list = [];
    params.keywords.chosen = [];
    params.keywords.count = 0;
    params.keywords.next = null;
    params.keywords.previous = null;
    params.keywords.isLoading = false;

    toggleSettings()

    updateKeywordsController();
    getKeywords();
}

// App controller

function setChooseAppEvents(){
    let apps = document.getElementsByClassName("app_list--element");
    for (let i = 0; apps.length > i; i++) {
        apps[i].addEventListener('mousedown', chooseApp);
    }
}

function appendAppToChosenList(app) {
    let appListObj = document.getElementsByClassName("app_chosen_list")[0];

    let div = document.createElement("div");
    div.classList.add("app_chosen_list--element");
    div.setAttribute("data-id", app.id);
    div.innerHTML = `${app.name}<i class="cross"></i>`;
    div.addEventListener('click', removeApp);
    appListObj.appendChild(div);
}

function chooseApp(e) {
    let appObj = e.currentTarget;
    if (appObj.classList.contains("dropdown--element__disabled"))
        return;

    let app_id = appObj.getAttribute('data-id');
    if (params.apps.chosen.filter(app => app.id == app_id).length != 0) {
        return;
    }
    
    let app = {
        id: app_id,
        name: appObj.innerHTML
    };
    params.apps.chosen.push(app);
    getKeywords();
    appObj.classList.add("dropdown--element__disabled");
    appendAppToChosenList(app);
}

function removeApp(e) {
    let appObj = e.currentTarget;
    let app_id = appObj.getAttribute('data-id');
    let dropdownObj = document.querySelector(`.app_list--element[data-id="${app_id}"]`);

    dropdownObj.classList.remove("dropdown--element__disabled");
    params.apps.chosen = removeObjFromListById(app_id, params.apps.chosen);
    
    appObj.remove();
    params.keywords.chosen = [];
    getKeywords();
}

function toggleAppSearch(e) {
    let appList = document.getElementsByClassName("app_list")[0];
    if (appList.contains(e.relatedTarget)) {
        let appInput = document.getElementsByClassName("app_finder")[0];
        appInput.focus();
    }

    if (appList.classList.contains("app_list__hidden")) {
        appList.classList.remove("app_list__hidden");
    } else {
        appList.classList.add("app_list__hidden");
    }
}

function inputAppSearch() {
    let search_app = document.querySelector(".app_finder").value;
    let appObjs = document.querySelectorAll(".app_list--element");

    for (let i = 0; i < appObjs.length; i++){
        let obj = appObjs[i]
        if (search_app != "" && obj.innerHTML.toLowerCase().includes(search_app.toLowerCase())){
            obj.classList.add("dropdown--element__filtered");
        } else {
            obj.classList.remove("dropdown--element__filtered");
        }
    }
}


// Keywords controller


async function getKeywords(url, search_str) {
    const { from, to } = getDateRange();
    if (url === undefined) {
        let has_data = '1';
        let data_app_ids = '';

        if (params.apps.chosen.length == 0) {
            data_app_ids = '-1';
        } else {
            for (let i in params.apps.chosen) {
                let app = params.apps.chosen[i];
                data_app_ids += `${app.id}`;
    
                if (i != params.apps.chosen.length - 1)
                    data_app_ids += ',';
            }
        }

        url = `/keywords/?has_data=${has_data}&data_app_ids=${data_app_ids}&start_date=${from.format("yyyy-mm-dd")}&end_date=${to.format("yyyy-mm-dd")}&limit=${params.keywords.limit}`;

        if (search_str !== undefined){
            url += `&search=${search_str}`;
        }
    }
    params.keywords.isLoading = true;
    updateKeywordsController();
    let response = await fetch(url)
        .then((response) => {
            return response.json();
        });
    params.keywords.count = response.count;
    params.keywords.next = response.next;
    params.keywords.previous = response.previous;
    params.keywords.list = response.results;
    params.keywords.isLoading = false;
    updateKeywordsController();
}

function updateKeywordsController() {
    updateKeywordsChosenList();
    updateKeywordsPicker();
}

function updateKeywordsPicker() {
    let keywordListObj = document.getElementsByClassName("keyword_list")[0];
    if (params.keywords.isLoading) {
        let s = `<li tabIndex="-1" class="dropdown--element"><img class="spinner" src="/static/kwfinder/img/spinner.gif" style="margin: 0 auto;"></li>`;
        keywordListObj.innerHTML = s;
        return;
    }

    let s = "";
    if (params.keywords.previous !== null) {
        s += `<li tabIndex="-1" class="dropdown--element"><i class="arrow up keywords_arrow"></i></li>`;
    }

    for (let i in params.keywords.list) {
        let keyword = params.keywords.list[i];
        let disabled_str = "";
        if (isObjWithIdInList(keyword.id, params.keywords.chosen)) {
            disabled_str = " dropdown--element__disabled";
        }

        s += `<li tabIndex="-1" class="keyword_list--element dropdown--element${disabled_str}" data-id="${keyword.id}">[${keyword.region}] ${keyword.name}</li>`;
    }

    if (params.keywords.next !== null) {
        s += `<li tabIndex="-1" class="dropdown--element"><i class="arrow down keywords_arrow"></i></li>`;
    }
    keywordListObj.innerHTML = s;

    let keywords = keywordListObj.getElementsByClassName("keyword_list--element");
    for (let i = 0; keywords.length > i; i++) {
        keywords[i].addEventListener('mousedown', chooseKeyword);
    }

    let arrows = keywordListObj.getElementsByClassName("arrow");
    for (let i = 0; arrows.length > i; i++) {
        let arrow = arrows[i];
        if (arrow.classList.contains('up')) {
            arrow.parentElement.addEventListener('mousedown', previousKeywords);
            continue;
        }
        if (arrow.classList.contains('down')) {
            arrow.parentElement.addEventListener('mousedown', nextKeywords);
            continue;
        }
    }
}

function updateKeywordsChosenList() {
    let keywordListObj = document.getElementsByClassName("keyword_chosen_list")[0];

    let s = "";
    for (let i in params.keywords.chosen) {
        let keyword = params.keywords.chosen[i];
        s += `<div class="keyword_chosen_list--element" data-id="${keyword.id}">${keyword.name}<i class="cross"></i></div>`;
    }
    keywordListObj.innerHTML = s;
    let keywordsCrosses = keywordListObj.getElementsByClassName("cross");
    for (let i = 0; keywordsCrosses.length > i; i++) {
        keywordsCrosses[i].addEventListener('click', removeKeyword);
    }
}

function chooseKeyword(e) {
    let keywordObj = e.currentTarget;
    if (keywordObj.classList.contains("dropdown--element__disabled"))
        return;

    let keyword_id = keywordObj.getAttribute('data-id');

    let keyword = isObjWithIdInList(keyword_id, params.keywords.list);
    if (!keyword) {
        alert(`Невозможно найти ключевое слово с id ${keyword_id}`);
        return;
    }
    params.keywords.chosen.push(keyword);
    updateKeywordsController();
}

function removeKeyword(e) {
    let keywordObj = e.currentTarget.parentElement;
    let keyword_id = keywordObj.getAttribute('data-id');

    params.keywords.chosen = removeObjFromListById(keyword_id, params.keywords.chosen);
    updateKeywordsController();
}

function toggleKeywordSearch(e) {
    let keywordList = document.getElementsByClassName("keyword_list")[0];
    if (keywordList.contains(e.relatedTarget)) {
        let keywordInput = document.getElementsByClassName("keyword_finder")[0];
        keywordInput.focus();
    }

    if (keywordList.classList.contains("keyword_list__hidden")) {
        keywordList.classList.remove("keyword_list__hidden");
    } else {
        keywordList.classList.add("keyword_list__hidden");
    }
}

function inputKeywordSearch() {
    let keywordInput = document.getElementsByClassName("keyword_finder")[0];
    if (keywordInput.value != "") {
        getKeywords(undefined, keywordInput.value);
    }
}

function previousKeywords() {
    getKeywords(params.keywords.previous);
}

function nextKeywords() {
    getKeywords(params.keywords.next);
}

// date range controller

function installDatepicker() {
    datepicker.render();
}

function getDateRange() {
    return datepicker.date;
}

// Offset controller

function inputSlider() {
    let ov = document.getElementsByClassName("offset--value")[0];
    ov.innerHTML = this.value;

    let main = document.getElementsByClassName('main')[0];
    main.style.width = `${this.value}%`;
}

// Stata controller

function showStats() {
    if (params.stata.isLoading)
        return;

    if (params.apps.chosen.length == 0 || params.keywords.chosen.length == 0) {
        alert("Вы должны выбрать хотя бы 1 приложение и ключевое слово!");
        return;
    }

    let showData = document.getElementsByClassName("show_data")[0];
    if (!showData.classList.contains('button__disabled'))
        showData.classList.add('button__disabled');

    params.stata.list = []
    params.stata.isLoading = true;
    params.stata.states = {};
    params.stata.labels = getLabels();

    for (let i in params.apps.chosen) {
        let app = params.apps.chosen[i];
        params.stata.states[app.id] = {};
        for (let j in params.keywords.chosen) {
            let keyword = params.keywords.chosen[j];

            params.stata.states[app.id][keyword.id] = 'loading';
            getStats(app.id, keyword.id);
        }
    }
}

async function getStats(app_id, keyword_id) {
    const { from, to } = getDateRange();
    let url = `/daily_data/?app__id=${app_id}&keyword__id=${keyword_id}&date__gte=${from.format("yyyy-mm-dd")}&date__lte=${to.format("yyyy-mm-dd")}&ordering=date`;
    let results = [];
    while (true) {
        let response = await fetch(url)
            .then((response) => {
                return response.json();
            });

        for (let i in response.results) {
            results.push(response.results[i]);
        }
        if (response.next == null)
            break;
        url = response.next;
    }
    params.stata.states[app_id][keyword_id] = 'loaded';

    let dataset = createDataSet(results, app_id, keyword_id);
    params.stata.list.push(dataset);

    if (isAllDataLoaded()) {
        params.stata.isLoading = false;
        let showData = document.getElementsByClassName("show_data")[0];
        if (showData.classList.contains('button__disabled'))
            showData.classList.remove('button__disabled');
        setupCharts()
    }
}

function createDataSet(data, app_id, keyword_id) {
    let dataset = {
        label: `${isObjWithIdInList(app_id, params.apps.chosen).name} - ${isObjWithIdInList(keyword_id, params.keywords.chosen).name}`,
        borderColor: randomRGB(),
        data: [],
        app_id: app_id,
        keyword_id: keyword_id
    }
    let label_i = 0;
    let data_i = 0;

    while (data_i < data.length && label_i < params.stata.labels.length) {
        let label = params.stata.labels[label_i];
        let data_part = data[data_i];

        if (data_part.date != label) {
            dataset.data.push(NaN);
            label_i++;
            continue;
        }

        label_i++;
        data_i++;
        if (data_part.position === 0)
            dataset.data.push(NaN);
        else
            dataset.data.push(data_part.position);
    }
    return dataset;
}

function getLabels() {
    return datepicker.getDaysArray();
}

function isAllDataLoaded() {
    for (let i in params.stata.states) {
        for (let j in params.stata.states[i]) {
            if (params.stata.states[i][j] != "loaded") {
                return false;
            }
        }
    }
    return true;
}

function setupCharts() {
    if (params.stata.chart !== null) {
        params.stata.chart.destroy();
    }
    const data = {
        labels: params.stata.labels,
        datasets: params.stata.list
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            scales: {
                y: {
                    suggestedMin: 0,
                    reverse: true
                }
            },
            // plugins: {
            //     tooltip: {
            //       // Tooltip will only receive click events
            //       events: ['click']
            //     }
            // }
            onClick: graphClickEvent,
        }
    };

    params.stata.chart = new Chart(
        document.getElementById('myChart'),
        config
    );
}

function graphClickEvent(event, array) {
    if (array.length == 0) return;

    if (array.length == 1) {
        loadPositionData(array[0]);
        return;
    }

    openKeywordPickerModal(array)
}

function openKeywordPickerModal(array){
    let modal = document.getElementById("modal-picker");
    let modalBody = modal.getElementsByClassName("modal-body")[0];
    modalBody.innerHTML = "";
    openModal(modal);
    array.forEach(input => {
        let dataset = params.stata.list[input.datasetIndex];
        let label = dataset.label;

        let button = document.createElement("button");
        button.innerHTML = label;
        button.classList.add("keyword_picker_modal");
        modalBody.appendChild(button);
        button.addEventListener('click', () => {
            closeModal(modal);
            loadPositionData(input);
        })
    })
}

async function loadPositionData(input) {
    let dataset = params.stata.list[input.datasetIndex];
    let date = params.stata.labels[input.index];
    console.log(dataset);
    console.log(date);

    let modal = document.getElementById("modal-keyword");
    let modalBody = modal.getElementsByClassName("modal-body")[0];
    modalBody.innerHTML = '<img class="spinner" src="/static/kwfinder/img/spinner.gif" style="margin: 0 auto;">';
    openModal(modal);
    modal.getElementsByClassName("title")[0].innerHTML = dataset.label;

    let url = `/position_data/?app__id=${dataset.app_id}&keyword__id=${dataset.keyword_id}&date=${date}&ordering=run__started_at`;
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

// helpers

function isObjWithIdInList(id, list) {
    let l = list.filter((x) => x.id == id)
    if (l.length == 0)
        return false;
    return l[0];
}

function removeObjFromListById(id, list) {
    return list.filter((x) => x.id != id);
}

const randomNum = () => Math.floor(Math.random() * (235 - 52 + 1) + 52);

const randomRGB = () => `rgb(${randomNum()}, ${randomNum()}, ${randomNum()})`;