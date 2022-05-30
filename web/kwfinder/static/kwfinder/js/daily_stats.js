import { datepicker } from './datepicker.js';

let params = {
    platform: {
        list: [],
        chosen: null,
    },
    app_type: {
        list: [],
        chosen: null,
    },
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
        limit: 10
    },
    stata: {
        list: [],
        labels: [],
        isLoading: false,
        states: {},
        chart: null
    }
}

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

    // setupCharts();

    getPlatforms();
    getAppTypes();
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

// Platform controller

async function getPlatforms() {
    let response = await fetch("/app_platforms/")
        .then((response) => {
            return response.json();
        });
    params.platform.list = response.results;
    updatePlatformsPicker();
}

function updatePlatformsPicker() {
    let platform_picker_opener = document.getElementsByClassName("platform_picker--opener")[0];
    let s = "";
    for (let i in params.platform.list) {
        let platform = params.platform.list[i];
        s += ` <li class="platform_picker--element dropdown--element" data-id="${platform.id}">${platform.name}</li>`;
    }

    let platform_picker = document.getElementsByClassName("platform_picker")[0];
    platform_picker.innerHTML = s;
    platform_picker_opener.addEventListener("click", togglePlatformPicker);
    let platforms = platform_picker.getElementsByClassName("platform_picker--element");
    for (let i = 0; platforms.length > i; i++) {
        platforms[i].addEventListener("click", platformSelected);
    }
}

function togglePlatformPicker() {
    let platform_picker_opener = document.getElementsByClassName("platform_picker--opener")[0];
    let arrow = platform_picker_opener.getElementsByClassName("arrow")[0];
    let platform_picker = document.getElementsByClassName("platform_picker")[0];

    if (platform_picker_opener.classList.contains("platform_picker--opener__active")) {
        if (arrow.classList.contains("up")) {
            arrow.classList.remove("up");
        }
        if (!arrow.classList.contains("down")) {
            arrow.classList.add("down");
        }
        platform_picker_opener.classList.remove('platform_picker--opener__active');

        if (!platform_picker.classList.contains("platform_picker__hidden")) {
            platform_picker.classList.add("platform_picker__hidden");
        }
    } else {
        if (arrow.classList.contains("down")) {
            arrow.classList.remove("down");
        }
        if (!arrow.classList.contains("up")) {
            arrow.classList.add("up");
        }
        platform_picker_opener.classList.add('platform_picker--opener__active');

        platform_picker.classList.remove("platform_picker__hidden");
    }
}

function platformSelected(e) {
    let selectedPlatform = e.currentTarget;
    let platform_id = selectedPlatform.getAttribute("data-id");

    let platforms = params.platform.list.filter((x) => x.id == parseInt(platform_id));
    if (platforms.length < 1) {
        console.log(`Can't find platform with such id ${platform_id}`);
        return;
    }

    let platform = platforms[0];
    let platform_picker_opener = document.getElementsByClassName("platform_picker--opener")[0];
    platform_picker_opener.classList.remove('platform_picker--opener__active');
    platform_picker_opener.innerHTML = `<div class="button--title">${platform.name} <i class="arrow down"></i></div>`;
    params.platform.chosen = platform;

    let platform_picker = document.getElementsByClassName("platform_picker")[0];
    if (!platform_picker.classList.contains("platform_picker__hidden")) {
        platform_picker.classList.add("platform_picker__hidden");
    }
}

// App types controller

async function getAppTypes() {
    let response = await fetch("/app_types/")
        .then((response) => {
            return response.json();
        });
    params.app_type.list = response.results;
    updateAppTypePicker()
}

function updateAppTypePicker() {
    let app_type_picker_opener = document.getElementsByClassName("app_type_picker--opener")[0];
    let s = "";
    for (let i in params.app_type.list) {
        let app_type = params.app_type.list[i];
        s += ` <li class="app_type_picker--element dropdown--element" data-id="${app_type.id}">${app_type.name}</li>`;
    }

    let app_type_picker = document.getElementsByClassName("app_type_picker")[0];
    app_type_picker.innerHTML = s;
    app_type_picker_opener.addEventListener("click", toggleAppTypePicker);
    let app_types = app_type_picker.getElementsByClassName("app_type_picker--element");
    for (let i = 0; app_types.length > i; i++) {
        app_types[i].addEventListener("click", appTypeSelected);
    }
}

function toggleAppTypePicker() {
    let app_type_picker_opener = document.getElementsByClassName("app_type_picker--opener")[0];
    let arrow = app_type_picker_opener.getElementsByClassName("arrow")[0];
    let app_type_picker = document.getElementsByClassName("app_type_picker")[0];

    if (app_type_picker_opener.classList.contains("app_type_picker--opener__active")) {
        if (arrow.classList.contains("up")) {
            arrow.classList.remove("up");
        }
        if (!arrow.classList.contains("down")) {
            arrow.classList.add("down");
        }
        app_type_picker_opener.classList.remove('app_type_picker--opener__active');

        if (!app_type_picker.classList.contains("app_type_picker__hidden")) {
            app_type_picker.classList.add("app_type_picker__hidden");
        }
    } else {
        if (arrow.classList.contains("down")) {
            arrow.classList.remove("down");
        }
        if (!arrow.classList.contains("up")) {
            arrow.classList.add("up");
        }
        app_type_picker_opener.classList.add('app_type_picker--opener__active');

        app_type_picker.classList.remove("app_type_picker__hidden");
    }
}

function appTypeSelected(e) {
    let selectedapp_type = e.currentTarget;
    let app_type_id = selectedapp_type.getAttribute("data-id");

    let app_types = params.app_type.list.filter((x) => x.id == parseInt(app_type_id));
    if (app_types.length < 1) {
        console.log(`Can't find app_type with such id ${app_type_id}`);
        return;
    }

    let app_type = app_types[0];
    let app_type_picker_opener = document.getElementsByClassName("app_type_picker--opener")[0];
    app_type_picker_opener.classList.remove('app_type_picker--opener__active');
    app_type_picker_opener.innerHTML = `<div class="button--title">${app_type.name} <i class="arrow down"></i></div>`;
    params.app_type.chosen = app_type;

    let app_type_picker = document.getElementsByClassName("app_type_picker")[0];
    if (!app_type_picker.classList.contains("app_type_picker__hidden")) {
        app_type_picker.classList.add("app_type_picker__hidden");
    }
}

function applySettings() {
    if (params.platform.chosen === null || params.app_type.chosen === null) {
        alert("Сначала выберите платформу и тип приложения");
        return;
    }

    params.apps = {
        list: [],
        chosen: []
    };
    params.keywords = {
        list: [],
        chosen: [],
        count: 0,
        next: null,
        previous: null,
        isLoading: false,
        limit: 10
    };

    toggleSettings()

    updateAppsController();
    updateKeywordsController();
    getApps();
    getKeywords();
}

// App controller

async function getApps() {
    let response = await fetch(`/apps/?platform__id${params.platform.chosen.id}&app_type__id=${params.app_type.chosen.id}`)
        .then((response) => {
            return response.json();
        });
    params.apps.list = response.results.sort((a, b) =>
        (a.name.toLowerCase() > b.name.toLowerCase()) ? 1 : ((b.name.toLowerCase() > a.name.toLowerCase()) ? -1 : 0));
    updateAppsController();
}

function updateAppsController() {
    updateAppsChosenList();
    updateAppsPicker();
}

function updateAppsPicker() {
    let appInput = document.getElementsByClassName("app_finder")[0];
    let appListObj = document.getElementsByClassName("app_list")[0];
    let filter_value = appInput.value.toLowerCase();

    let s = "";
    for (let i in params.apps.list) {
        let app = params.apps.list[i];
        if (filter_value != "" && !app.name.toLowerCase().includes(filter_value)) {
            continue;
        }
        
        let disabled_str = "";
        if (isObjWithIdInList(app.id, params.apps.chosen)) {
            disabled_str = " dropdown--element__disabled";
        }

        s += `<li tabIndex="-1" class="app_list--element dropdown--element${disabled_str}" data-id="${app.id}">${app.name}</li>`;
    }
    appListObj.innerHTML = s;

    let apps = document.getElementsByClassName("app_list--element");
    for (let i = 0; apps.length > i; i++) {
        apps[i].addEventListener('mousedown', chooseApp);
    }
}

function updateAppsChosenList() {
    let appListObj = document.getElementsByClassName("app_chosen_list")[0];

    let s = "";
    for (let i in params.apps.chosen) {
        let app = params.apps.chosen[i];
        s += `<div class="app_chosen_list--element" data-id="${app.id}">${app.name}<i class="cross"></i></div>`;
    }
    appListObj.innerHTML = s;
    let appsCrosses = appListObj.getElementsByClassName("cross");
    for (let i = 0; appsCrosses.length > i; i++) {
        appsCrosses[i].addEventListener('click', removeApp);
    }
}

function chooseApp(e) {
    let appObj = e.currentTarget;
    if (appObj.classList.contains("dropdown--element__disabled"))
        return;

    let app_id = appObj.getAttribute('data-id');

    let app = isObjWithIdInList(app_id, params.apps.list);
    if (!app) {
        alert(`Невозможно найти приложение с id ${app_id}`);
        return;
    }
    params.apps.chosen.push(app);
    updateAppsController();
}

function removeApp(e) {
    let appObj = e.currentTarget.parentElement;
    let app_id = appObj.getAttribute('data-id');

    params.apps.chosen = removeObjFromListById(app_id, params.apps.chosen);
    updateAppsController();
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
    updateAppsPicker();
}


// Keywords controller


async function getKeywords(url) {
    if (url === undefined) {
        url = `/keywords/?limit=${params.keywords.limit}&app_type__id=${params.app_type.chosen.id}`;
    }
    params.keywords.isLoading = true;
    updateAppsController();
    let response = await fetch(url)
        .then((response) => {
            return response.json();
        });
    params.keywords.count = response.count;
    params.keywords.next = response.next;
    params.keywords.previous = response.previous;
    params.keywords.list = response.results;
    // .sort((a, b) =>(a.name.toLowerCase() > b.name.toLowerCase()) ? 1 : ((b.name.toLowerCase() > a.name.toLowerCase()) ? -1 : 0));
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

        s += `<li tabIndex="-1" class="keyword_list--element dropdown--element${disabled_str}" data-id="${keyword.id}">${keyword.name}</li>`;
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
    let url = `/keywords/?limit=${params.keywords.limit}&app_type__id=${params.app_type.chosen.id}`;

    let keywordInput = document.getElementsByClassName("keyword_finder")[0];
    if (keywordInput.value != "") {
        url += `&search=${keywordInput.value}`;
    }
    getKeywords(url);
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
        data: []
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
            }
        }
    };

    params.stata.chart = new Chart(
        document.getElementById('myChart'),
        config
    );
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