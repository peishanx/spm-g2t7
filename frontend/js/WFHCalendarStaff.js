import { createApp } from 'https://cdn.jsdelivr.net/npm/vue@3.2.45/dist/vue.esm-browser.js';
const { Calendar } = FullCalendar;

createApp({
    data() {
        return {
            events: [],
            filterType: 'all',
            calendar: null,
        };
    },
    mounted() {
        this.fetchCalendarData();
    },
    methods: {
        fetchCalendarData() {
            const staffId = sessionStorage.getItem('staff_id');
            fetch(`http://localhost:5201/request/employee/${staffId}`)
                .then(response => response.json())
                .then(data => {
                    console.log('API Response:', data);
                    if (data.code === 200 && Array.isArray(data.data)) {
                        this.events = data.data.map(event => {
                            let backgroundColor = ''; // Initialize background color variable

                            // Set background color based on event title
                            switch (event.title) {
                                case 'WFH (AM)':
                                case 'WFH (PM)':
                                case 'WFH (Full Day)':
                                    backgroundColor = '#6941C6'; // Purple for WFH
                                    break;
                                case 'In Office (AM)':
                                case 'In Office (PM)':
                                case 'In Office (Full Day)':
                                    backgroundColor = '#B3B3FF'; // Light purple for In Office
                                    break;
                                default:
                                    backgroundColor = '#B3B3FF'; // Default to light purple
                            }

                            console.log(`Mapped Event: Title: ${event.title}, Start: ${event.start}, End: ${event.end}, Background Color: ${backgroundColor}`);

                            return {
                                title: event.title,
                                start: event.start,
                                end: event.end,
                                backgroundColor: backgroundColor // Add background color for events
                            };
                        });

                        this.initCalendar(); // Initialize the calendar after fetching data
                        this.updateCalendarEvents(); // Update the calendar with the new events
                    } else {
                        console.error('Invalid API response format or code:', data);
                    }
                })
                .catch(error => console.error('Error fetching calendar data:', error));
        },

        initCalendar() {
            const calendarEl = document.getElementById('calendar');
            this.calendar = new Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay,listYear'
                },
                events: this.events, // Set the events directly from the mapped data
                eventTimeFormat: {
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                },
                eventDidMount: (info) => {
                    // Assign colors to event backgrounds
                    info.el.style.backgroundColor = info.event.backgroundColor; 
                }
            });
            this.calendar.render(); // Render the calendar
            console.log('Calendar initialized with events:', this.events); // Log initialized events
        },

        updateCalendarEvents() {
            const filteredEvents = this.getFilteredEvents();
            console.log('Filtered Events:', filteredEvents);
            this.calendar.removeAllEvents();
            this.calendar.addEventSource(filteredEvents);
        },

        getFilteredEvents() {
            if (this.filterType === 'all') {
                return this.events;
            }

            // Create a mapping of filter type to title
            const titleMapping = {
                'wfh_am': 'WFH (AM)',
                'wfh_pm': 'WFH (PM)',
                'wfh_full_day': 'WFH (Full Day)',
                'in_office_am': 'In Office (AM)',
                'in_office_pm': 'In Office (PM)',
                'in_office_full_day': 'In Office (Full Day)'
            };

            const filterTitle = titleMapping[this.filterType];
            return this.events.filter(event => event.title === filterTitle);
        }
    },
    watch: {
        filterType() {
            this.updateCalendarEvents();
        }
    }
}).mount('#app');
