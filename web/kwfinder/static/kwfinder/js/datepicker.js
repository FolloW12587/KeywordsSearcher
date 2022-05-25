
export var datepicker = {
  date: {
    from: new Date(),
    to: new Date(),
    selected: new Date(),
  },
  pending: {
    from: new Date(),
    to: new Date()
  },
  isSelecting: false,
  isOpened: false,
  pickedRange: null,
  hovered: null,
  currentMonth: new Date().getMonth(),
  currentYear: new Date().getFullYear(),
  render: () => {
    removeEvents(datepicker.events.eventHandlers);
    datepicker.events.eventHandlers = [];
    document.getElementsByClassName("date_range--picker")[0].innerHTML = new DatePicker().render();
    addEvents(datepicker.events.eventHandlers);
  },
  getDaysArray: getDaysArray,
  events: {
    eventHandlers: [],
    customEvents: {}
  }
}


/**
 * Abstract Class Obj.
 *
 * @class Obj
 */
class Obj {
  constructor() {

  }

  render() {
    throw new Error("Method 'render()' must be implemented.");
  }
}

class Style {
  constructor(class_list, attrs = {}) {
    this.class_list = class_list;
    this.attrs = attrs;
  }

  addClass(class_name) {
    if (!this.class_list.includes(class_name))
      this.class_list.push(class_name);
  }

  addAttr(name, value) {
    this.attrs[name] = value;
  }

  removeClass(class_name) {
    if (this.class_list.includes(class_name))
      this.class_list = this.class_list.filter((c) => c != class_name);
  }

  toggleClass(class_name) {
    if (this.class_list.includes(class_name))
      this.class_list = this.class_list.filter((c) => c != class_name);
    else
      this.class_list.push(class_name);
  }

  getString() {
    if (this.class_list.length == 0)
      return '';
    return this.class_list.join(" ");
  }

  getAttrString() {
    var str = '';
    for (var name in this.attrs) {
      if (this.attrs[name] == '')
        str += `${name} `;
      else
        str += `${name}="${value} "`;
    }
    return str;
  }

  containsClass(class_name) {
    return this.class_list.includes(class_name);
  }
}

/**
 * DatePicker.
 *
 * @class DatePicker
 * @extends {Obj}
 */
export class DatePicker extends Obj {
  render() {
    return `
    <div class="DatePicker_normal">
      ${new DateRangeContainer().render()}
    </div>`;
  }
}

const toText = date => {
  const day = date.getDate();
  const month = monthTitles[date.getMonth()];
  const year = date.getFullYear();
  return `${day} ${month} ${year}`;
}

/**
 * DateRangeContainer.
 *
 * @class DateRangeContainer
 * @extends {Obj}
 */
class DateRangeContainer extends Obj {
  render() {
    return `
      <div class="DateRange_normal">
        <div class="DateRange_current">
          ${new DateRangeButton().render()}
        </div>
        ${new DateDropdown().render()}
      </div>
    `;
  }
}

/**
 * DateRangeButton.
 *
 * @class DateRangeButton
 * @extends {Obj}
 */
class DateRangeButton extends Obj {
  constructor() {
    super();
    this.style = new Style(['DateRange_currentButton']);
    this.fillStyles();
    this.addEvents();
  }

  addEvents() {
    var that = this;
    datepicker.events.eventHandlers.push({
      class_name: "DateRange_currentButton",
      type: "click",
      func: that.handleOpen,
      attrs: []
    });
  }

  fillStyles() {
    // if (data.isUploading) {
    //   this.style.addClass("DateRange_current_disabled");
    //   this.style.addAttr("disabled", '');
    // }
  }

  dateTransform = () => {
    const { from, to } = datepicker.date;
    const textFrom = toText(from);
    const textTo = toText(to);
    const text = textFrom === textTo ? textFrom : `${textFrom} - ${textTo}`;
    return text;
  }

  handleOpen = event => {
    event.preventDefault();
    datepicker.isOpened = !datepicker.isOpened;
    datepicker.render();
  }

  render() {
    return `
      <button data-button="dateButton" class="${this.style.getString()}" ${this.style.getAttrString()}>
        <i class="Icon_if Icon_calendars DateRange_currentIcon"></i>
        <span class="DateRange_currentDate">${this.dateTransform()}</span>
      </button>
    `;
  }
}

/**
 * DateDropdown.
 *
 * @class DateDropdown
 * @extends {Obj}
 */
class DateDropdown extends Obj {
  constructor() {
    super();
    this.style = new Style(["DateDropdown_dropdown"]);
    this.addEvents();
  }

  addEvents() {
    var that = this;

    /* outside click */
    datepicker.events.eventHandlers.push({
      class_name: "container",
      type: "click",
      func: that.handleClickOutside,
      attrs: []
    });
  }

  handleClickOutside = event => {
    const target = event.target;
    if (target.getAttribute('data-button') !== 'dateButton' && !document.getElementsByClassName("DateDropdown_dropdown")[0].contains(target) && datepicker.isOpened) {
      datepicker.isOpened = false;
      datepicker.render();
    }
  }

  render() {
    if (datepicker.isOpened)
      this.style.addClass("DateDropdown_active");
    else
      this.style.removeClass("DateDropdown_active");

    return `
      <div class="${this.style.getString()}">
        ${new DateRangePicker().render()}

        <ul class="DateDropdown_list">
          ${dateRangeValues.map(r => {
      return new PickRange(r).render();
    }).join("")}
        </ul>
      </div>
    `;
  }
}

/**
 * DateRangePicker.
 *
 * @class DateRangePicker
 * @extends {Obj}
 */
class DateRangePicker extends Obj {
  constructor() {
    super();
    this.addEvents();
  }

  addEvents() {
    var that = this;

    datepicker.events.eventHandlers.push({
      class_name: "DateRangePicker__PaginationArrow--previous",
      type: "click",
      func: that.previous,
      attrs: []
    });

    datepicker.events.eventHandlers.push({
      class_name: "DateRangePicker__PaginationArrow--next",
      type: "click",
      func: that.next,
      attrs: []
    });
  }

  next(e) {
    datepicker.currentMonth = (datepicker.currentMonth + 1) % 12;
    if (datepicker.currentMonth == 12) {
      datepicker.currentMonth = 0;
      datepicker.currentYear += 1
    }
    e.stopPropagation();
    datepicker.render();
  }

  previous(e) {
    datepicker.currentMonth = datepicker.currentMonth - 1;
    if (datepicker.currentMonth == -1) {
      datepicker.currentMonth = 11;
      datepicker.currentYear -= 1
    }
    e.stopPropagation();
    datepicker.render();
  }

  render() {
    return `
      <div class="DateRangePicker">
        <div class="DateRangePicker__PaginationArrow DateRangePicker__PaginationArrow--previous">
          <div
            class="DateRangePicker__PaginationArrowIcon DateRangePicker__PaginationArrowIcon--previous">
          </div>
        </div>
        ${new DateRangePicker__Month(0).render()}
        ${new DateRangePicker__Month(1).render()}

        <div class="DateRangePicker__PaginationArrow DateRangePicker__PaginationArrow--next">
          <div class="DateRangePicker__PaginationArrowIcon DateRangePicker__PaginationArrowIcon--next">
          </div>
        </div>
      </div>
    `;
  }
}

/**
 * DateRangePicker__Month.
 *
 * @class DateRangePicker__Month
 * @extends {Obj}
 */
class DateRangePicker__Month extends Obj {
  constructor(index) {
    super();
    this.index = index;
  }

  render() {
    return `
      <div class="DateRangePicker__Month">
        ${new DateRangePicker__MonthHeader(this.index).render()}
        ${new DateRangePicker__MonthDates(this.index).render()}
      </div>
    `;
  }
}

/**
 * DateRangePicker__MonthHeader.
 *
 * @class DateRangePicker__MonthHeader
 * @extends {Obj}
 */
class DateRangePicker__MonthHeader extends Obj {
  constructor(index) {
    super();
    this.index = index;
    this.addEvents();
  }

  addEvents() {
    var that = this;

    datepicker.events.eventHandlers.push({
      class_name: "DateRangePicker__MonthHeaderSelect",
      type: "change",
      func: that.monthChanged,
      attrs: [{
        name: "data-source",
        value: `month_${that.index}`
      },]
    });

    datepicker.events.eventHandlers.push({
      class_name: "DateRangePicker__MonthHeaderSelect",
      type: "change",
      func: that.yearChanged,
      attrs: [{
        name: "data-source",
        value: `year_${that.index}`
      },]
    });
  }

  monthChanged(e) {
    const target = e.target;
    datepicker.currentMonth = parseInt(target.value);
    e.stopPropagation();
    datepicker.render();
  }

  yearChanged(e) {
    const target = e.target;
    datepicker.currentYear = parseInt(target.value);
    e.stopPropagation();
    datepicker.render();
  }

  getYears(date) {
    var output = [];
    for (var i = -5; i < 6; i++) {
      output.push(date.getFullYear() + i);
    }
    return output;
  }

  render() {
    const date = new Date(datepicker.currentYear, datepicker.currentMonth + this.index);
    return `
      <div class="DateRangePicker__MonthHeader">
        <span class="DateRangePicker__MonthHeaderLabel DateRangePicker__MonthHeaderLabel--month">${monthLabels[date.getMonth()]}
          <select data-source="month_${this.index}" class="DateRangePicker__MonthHeaderSelect">
            ${monthLabels.map((v, i) => `<option value="${i}" ${i == date.getMonth() ? "selected" : ""}>${monthLabels[i]}</option>`).join("")}
          </select>
        </span> 
        <span class="DateRangePicker__MonthHeaderLabel DateRangePicker__MonthHeaderLabel--year">${date.getFullYear()}
          <select data-source="year_${this.index}" class="DateRangePicker__MonthHeaderSelect">
            ${this.getYears(date).map((d) => `<option value="${d}" ${date.getFullYear() == d ? "selected" : ""}>${d}</option>`).join("")}
          </select>
        </span>
      </div>
    `;
  }
}

/**
 * DateRangePicker__MonthDates.
 *
 * @class DateRangePicker__MonthDates
 * @extends {Obj}
 */
class DateRangePicker__MonthDates extends Obj {
  constructor(index) {
    super();
    this.index = index;
  }

  getDaysInMonth(date) {
    const year = date.getFullYear();
    const month = date.getMonth();
    date = new Date(year, month, 1);
    var days = [];
    while (date.getMonth() === month) {
      days.push(new Date(date));
      date.setDate(date.getDate() + 1);
    }
    return days;
  }

  getTableDates(curDate) {
    var days = this.getDaysInMonth(curDate);
    var daysCount = days.length;

    var date = days[0];
    var distance = date.getDay();
    for (var i = 0; distance != 1; i--) {
      date = new Date(datepicker.currentYear, datepicker.currentMonth + this.index, i);
      days.unshift(date);
      distance = date.getDay();
    }

    date = days[days.length - 1];
    distance = date.getDay();
    for (var i = 1; distance != 0; i++) {
      date = new Date(datepicker.currentYear, datepicker.currentMonth + this.index, daysCount + i);
      days.push(date);
      distance = date.getDay();
    }
    return days;
  }

  render() {
    const date = new Date(datepicker.currentYear, datepicker.currentMonth + this.index);
    const days = this.getTableDates(date);
    return `
      <table class="DateRangePicker__MonthDates">
        <thead>
          <tr class="DateRangePicker__Weekdays">
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr
                title="понедельник">пн</abbr></th>
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr title="вторник">вт</abbr>
            </th>
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr title="среда">ср</abbr></th>
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr title="четверг">чт</abbr>
            </th>
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr title="пятница">пт</abbr>
            </th>
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr title="суббота">сб</abbr>
            </th>
            <th class="DateRangePicker__WeekdayHeading" scope="col"><abbr
                title="воскресенье">вс</abbr></th>
          </tr>
        </thead>
        <tbody>
        ${days.map(
      (day, i) => {
        var str = '';
        if (i % 7 == 0) {
          str += '<tr class="DateRangePicker__Week">';
        }
        str += new DateRangePicker__Date(date, day).render();
        if ((i + 1) % 7 == 0) {
          str += "</tr>";
        }
        return str;
      }
    ).join("")}
        </tbody>
      </table>
    `;
  }
}

/**
 * DateRangePicker__Date.
 *
 * @class DateRangePicker__Date
 * @extends {Obj}
 */
class DateRangePicker__Date extends Obj {
  constructor(date, day) {
    super();
    this.date = date;
    this.day = day;
    this.tdStyle = new Style(['DateRangePicker__Date']);
    this.divSelectionStyle = new Style([]);
    this.divHighlightedStyle = new Style([]);
    const status = datepicker.isSelecting ? 'selecting' : "notSelecting";
    const funcsForStatus = {
      "selecting": {
        isSelected: this.isPendingSelected,
        isEnd: this.isPendingEnd,
        isStart: this.isPendingStart,
        isSingle: this.isPendingSingle,
        isInRange: this.isInPendingRange,
      },
      "notSelecting": {
        isSelected: this.isSelected,
        isEnd: this.isEnd,
        isStart: this.isStart,
        isSingle: this.isSingle,
        isInRange: this.isInRange,
      }
    }
    this.funcs = funcsForStatus[status];
    this.fillStyles();
    this.addEvents();
  }

  addEvents() {
    var that = this;

    datepicker.events.eventHandlers.push({
      class_name: "DateRangePicker__Date",
      type: "click",
      func: that.handleClick,
      attrs: [{
        name: "data-source",
        value: `${this.day.getFullYear()}_${this.day.getMonth()}_${this.day.getDate()}`
      },]
    });

    datepicker.events.eventHandlers.push({
      class_name: "DateRangePicker__Date",
      type: "mouseover",
      func: that.handleHovered,
      attrs: [{
        name: "data-source",
        value: `${this.day.getFullYear()}_${this.day.getMonth()}_${this.day.getDate()}`
      },]
    });
  }

  handleClick(e) {
    const target = e.currentTarget;
    const data_source = target.getAttribute("data-source").split("_");
    const date = new Date(data_source[0], data_source[1], data_source[2]);
    if (datepicker.isSelecting) {
      datepicker.isSelecting = false;
      datepicker.date.from = datepicker.pending.from;
      datepicker.date.to = datepicker.pending.to;
    } else {
      datepicker.isSelecting = true;
      datepicker.date.selected = date;
      datepicker.pending.from = date;
      datepicker.pending.to = date;
    }
    e.stopPropagation();
    datepicker.render();
  }

  handleHovered(e) {
    const target = e.currentTarget;
    const data_source = target.getAttribute("data-source").split("_");
    const date = new Date(data_source[0], data_source[1], data_source[2]);
    if (datepicker.hovered != null && areDatesEqual(datepicker.hovered, date))
      return;

    if (datepicker.isSelecting) {
      if (isD1MoreThanD2(datepicker.date.selected, date)) {
        datepicker.pending.to = datepicker.date.selected;
        datepicker.pending.from = date;
      } else {
        datepicker.pending.from = datepicker.date.selected;
        datepicker.pending.to = date;
      }
      datepicker.hovered = date;
    } else {
      datepicker.hovered = date;
    }

    datepicker.render();
  }

  fillStyles() {
    this.fillTdStyles();
    this.fillDivSelectionStyles();
    this.fillDivHighlightedStyles();
  }

  fillTdStyles() {
    const isSelected = this.funcs.isSelected.call(this);
    if (isSelected) {
      this.tdStyle.addClass("DateRangePicker__Date--is-selected");
    }

    if (this.isHovered()) {
      this.tdStyle.addClass("DateRangePicker__Date--is-highlighted");
    }

    if (this.day.getMonth() != this.date.getMonth()) {
      this.tdStyle.addClass("DateRangePicker__Date--otherMonth");
      if (isSelected) {
        this.tdStyle.addClass("DateRangePicker__Date--otherMonth--is-selected");
      }
    }

    if (this.day.getDay() == 0 || this.day.getDay() == 6) {
      this.tdStyle.addClass("DateRangePicker__Date--weekend");
      if (isSelected) {
        this.tdStyle.addClass("DateRangePicker__Date--weekend--is-selected");
      }
    }
  }

  fillDivSelectionStyles() {
    if (datepicker.isSelecting) {
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--is-pending");
    }
    if (this.funcs.isSingle.call(this)) {
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection");
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--single");
      if (datepicker.isSelecting) {
        this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--single--is-pending");
      }
      return;
    }
    if (this.funcs.isStart.call(this)) {
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection");
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--start");
      if (datepicker.isSelecting) {
        this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--start--is-pending");
      }
      return;
    }
    if (this.funcs.isEnd.call(this)) {
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection");
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--end");
      if (datepicker.isSelecting) {
        this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--end--is-pending");
      }
      return;
    }
    if (this.funcs.isInRange.call(this)) {
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection");
      this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--segment");
      if (datepicker.isSelecting) {
        this.divSelectionStyle.addClass("DateRangePicker__CalendarSelection--segment--is-pending");
      }
      return;
    }
  }

  fillDivHighlightedStyles() {
    if (this.isHovered()) {
      this.divHighlightedStyle.addClass("DateRangePicker__CalendarHighlight")
      this.divHighlightedStyle.addClass("DateRangePicker__CalendarHighlight--single")
    }
  }

  isHovered() {
    if (datepicker.hovered !== null && areDatesEqual(this.day, datepicker.hovered))
      return true;
    return false;
  }

  isInRange() {
    if (isD1MoreThanD2(this.day, datepicker.date.from) && isD1MoreThanD2(datepicker.date.to, this.day))
      return true;
    return false;
  }

  isInPendingRange() {
    if (isD1MoreThanD2(this.day, datepicker.pending.from) && isD1MoreThanD2(datepicker.pending.to, this.day))
      return true;
    return false;
  }

  isStart() {
    if (areDatesEqual(this.day, datepicker.date.from))
      return true;
    return false;
  }

  isPendingStart() {
    if (areDatesEqual(this.day, datepicker.pending.from))
      return true;
    return false;
  }

  isEnd() {
    if (areDatesEqual(this.day, datepicker.date.to))
      return true;
    return false;
  }

  isPendingEnd() {
    if (areDatesEqual(this.day, datepicker.pending.to))
      return true;
    return false;
  }

  isSingle() {
    if (this.isStart() && this.isEnd())
      return true;
    return false;
  }

  isPendingSingle() {
    if (this.isPendingStart() && this.isPendingEnd())
      return true;
    return false;
  }

  isSelected() {
    return this.isInRange() || this.isStart() || this.isEnd();
  }

  isPendingSelected() {
    return this.isInPendingRange() || this.isPendingStart() || this.isPendingEnd();
  }

  getDivsStrings() {
    var str = '';
    var classes = this.divSelectionStyle.getString();
    if (classes != '') {
      str += `<div class="${classes}"></div>`;
    }

    classes = this.divHighlightedStyle.getString();
    if (classes != '') {
      str += `<div class="${classes}"></div>`;
    }
    return str;
  }

  render() {
    const divs = this.getDivsStrings();
    return `
      <td data-source="${this.day.getFullYear()}_${this.day.getMonth()}_${this.day.getDate()}" class="${this.tdStyle.getString()}">
        <div class="DateRangePicker__FullDateStates"></div>
        <span class="DateRangePicker__DateLabel">${this.day.getDate()}</span>
        ${divs}
      </td>
    `;
  }

}


/**
 * PickRange.
 *
 * @class PickRange
 * @extends {Obj}
 */
class PickRange extends Obj {
  constructor(dateRangeValue) {
    /** @type {dateRangeValues[0]} */
    super();
    this.dateRangeValue = dateRangeValue;
    this.addEvents();
  }

  addEvents() {
    var that = this;

    datepicker.events.eventHandlers.push({
      class_name: "PickRange_normal",
      type: "click",
      func: that.handleClick,
      attrs: [{
        name: "data-source",
        value: this.dateRangeValue.title
      }]
    });
  }

  handleClick = event => {
    event.preventDefault();
    datepicker.pickedRange = this.dateRangeValue.title;
    const value = this.dateRangeValue.value();
    datepicker.date.from = value.from;
    datepicker.date.to = value.to;
    datepicker.currentMonth = value.from.getMonth();
    datepicker.currentYear = value.from.getFullYear();
    event.stopPropagation();
    datepicker.render();
  }

  isActive() {
    return datepicker.pickedRange == this.dateRangeValue.title;
  }

  render() {
    return `
      <li class="DateDropdown_item">
        <button data-source="${this.dateRangeValue.title}" class="PickRange_normal ${this.isActive() ? "PickRange_active" : ""}">
          <span class="PickRange_title">${this.dateRangeValue.title}</span>
        </button>
      </li>
    `;
  }
}

const dateRangeValues = [
  {
    title: 'Сегодня',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return {
        from: today,
        to: today
      }
    }
  },
  {
    title: 'Вчера',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const currentDay = today.getDate()
      const yesterday = new Date()
      yesterday.setHours(0, 0, 0, 0)
      yesterday.setDate(currentDay - 1)
      return {
        from: yesterday,
        to: yesterday
      }
    }
  },
  {
    title: 'Неделя',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const currentDay = today.getDate()
      const week = new Date()
      week.setHours(0, 0, 0, 0)
      week.setDate(currentDay - 6)
      return {
        from: week,
        to: today
      }
    }
  },
  {
    title: 'Месяц',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const currentMonth = today.getMonth()
      const month = new Date()
      month.setHours(0, 0, 0, 0)
      month.setMonth(currentMonth - 1)
      return {
        from: month,
        to: today
      }
    }
  },
  {
    title: 'Квартал',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const currentMonth = today.getMonth()
      const quarter = new Date()
      quarter.setHours(0, 0, 0, 0)
      quarter.setMonth(currentMonth - 3)
      return {
        from: quarter,
        to: today
      }
    }
  },
  {
    title: 'Год',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const currentYear = today.getFullYear()
      const year = new Date()
      year.setHours(0, 0, 0, 0)
      year.setYear(currentYear - 1)
      return {
        from: year,
        to: today
      }
    }
  }
];

const monthTitles = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
const monthLabels = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];

var dateFormat = function () {
  var token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
    timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
    timezoneClip = /[^-+\dA-Z]/g,
    pad = function (val, len) {
      val = String(val);
      len = len || 2;
      while (val.length < len) val = "0" + val;
      return val;
    };

  // Regexes and supporting functions are cached through closure
  return function (date, mask, utc) {
    var dF = dateFormat;

    // You can't provide utc if you skip other args (use the "UTC:" mask prefix)
    if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
      mask = date;
      date = undefined;
    }

    // Passing date through Date applies Date.parse, if necessary
    date = date ? new Date(date) : new Date;
    if (isNaN(date)) throw SyntaxError("invalid date");

    mask = String(dF.masks[mask] || mask || dF.masks["default"]);

    // Allow setting the utc argument via the mask
    if (mask.slice(0, 4) == "UTC:") {
      mask = mask.slice(4);
      utc = true;
    }

    var _ = utc ? "getUTC" : "get",
      d = date[_ + "Date"](),
      D = date[_ + "Day"](),
      m = date[_ + "Month"](),
      y = date[_ + "FullYear"](),
      H = date[_ + "Hours"](),
      M = date[_ + "Minutes"](),
      s = date[_ + "Seconds"](),
      L = date[_ + "Milliseconds"](),
      o = utc ? 0 : date.getTimezoneOffset(),
      flags = {
        d: d,
        dd: pad(d),
        ddd: dF.i18n.dayNames[D],
        dddd: dF.i18n.dayNames[D + 7],
        m: m + 1,
        mm: pad(m + 1),
        mmm: dF.i18n.monthNames[m],
        mmmm: dF.i18n.monthNames[m + 12],
        yy: String(y).slice(2),
        yyyy: y,
        h: H % 12 || 12,
        hh: pad(H % 12 || 12),
        H: H,
        HH: pad(H),
        M: M,
        MM: pad(M),
        s: s,
        ss: pad(s),
        l: pad(L, 3),
        L: pad(L > 99 ? Math.round(L / 10) : L),
        t: H < 12 ? "a" : "p",
        tt: H < 12 ? "am" : "pm",
        T: H < 12 ? "A" : "P",
        TT: H < 12 ? "AM" : "PM",
        Z: utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
        o: (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
        S: ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
      };

    return mask.replace(token, function ($0) {
      return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
    });
  };
}();

// Some common format strings
dateFormat.masks = {
  "default": "ddd mmm dd yyyy HH:MM:ss",
  shortDate: "m/d/yy",
  mediumDate: "mmm d, yyyy",
  longDate: "mmmm d, yyyy",
  fullDate: "dddd, mmmm d, yyyy",
  shortTime: "h:MM TT",
  mediumTime: "h:MM:ss TT",
  longTime: "h:MM:ss TT Z",
  isoDate: "yyyy-mm-dd",
  isoTime: "HH:MM:ss",
  isoDateTime: "yyyy-mm-dd'T'HH:MM:ss",
  isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
};

// Internationalization strings
dateFormat.i18n = {
  dayNames: [
    "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
  ],
  monthNames: [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
  ]
};

// For convenience...
Date.prototype.format = function (mask, utc) {
  return dateFormat(this, mask, utc);
};

function isD1MoreThanD2(date1, date2) {
  if (date1.getFullYear() > date2.getFullYear())
    return true;
  if (date1.getFullYear() < date2.getFullYear())
    return false;

  if (date1.getMonth() > date2.getMonth())
    return true;
  if (date1.getMonth() < date2.getMonth())
    return false;

  if (date1.getDate() > date2.getDate())
    return true;

  return false;
}

function areDatesEqual(date1, date2) {
  if (date1.getDate() == date2.getDate() && date1.getMonth() == date2.getMonth() && date1.getFullYear() == date2.getFullYear())
    return true;
  return false;
}

function addEvents(events) {
  for (var i in events) {
    try {
      const { class_name, type, func, attrs } = events[i];
      const els = document.getElementsByClassName(class_name);
      if (els.length > 1 && attrs !== undefined) {
        for (var j = 0; j < els.length; j++) {
          if (checkElementForAttrs(els[j], attrs)) {
            els[j].addEventListener(type, func);
          }
          // if (els[j].hasAttribute(attr.name) && els[j].getAttribute(attr.name) == attr.value) {
          //   els[j].addEventListener(type, func);
          // }
        }
      } else if (els.length > 0) {
        els[0].addEventListener(type, func);
      }
    } catch (e) {
      console.log(i);
      console.error(e);
    }
  }
}

function removeEvents(events) {
  for (var i in events) {
    const { class_name, type, func, attrs } = events[i];
    const els = document.getElementsByClassName(class_name);
    if (els.length > 1 && attrs.length > 0) {
      for (var j = 0; j < els.length; j++) {
        if (checkElementForAttrs(els[j], attrs)) {
          els[j].removeEventListener(type, func);
        }
        // if (els[j].hasAttribute(attrs.name) && els[j].getAttribute(attrs.name) == attrs.value) {
        // }
      }
    } else if (els.length > 0) {
      els[0].removeEventListener(type, func);
    }
  }
  events = [];
}

function checkElementForAttrs(el, attrs) {
  for (var i in attrs) {
    var attr = attrs[i];
    if (!el.hasAttribute(attr.name) || el.getAttribute(attr.name) != attr.value) {
      return false;
    }
  }
  return true;
}

function getDaysArray() {
  let start = datepicker.date.from;
  let end = datepicker.date.to;
  for (var arr = [], dt = new Date(start); dt <= new Date(end); dt.setDate(dt.getDate() + 1)) {
    arr.push(new Date(dt).format("yyyy-mm-dd"));
  }
  return arr;
};