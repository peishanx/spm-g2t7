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
        async fetchCalendarData() {
            const staffId = sessionStorage.getItem('staff_id');
        
            try {
                // Fetch WFH requests
                const wfhResponse = await fetch(`http://localhost:5201/request/employee/${staffId}`);
                const wfhData = await wfhResponse.json();
                
                // Fetch Leave details
                const leaveResponse = await fetch(`http://localhost:5201/leaves`);
                const leaveData = await leaveResponse.json();
                
                console.log('WFH API Response:', wfhData);
                console.log('Leave API Response:', leaveData);
        
                if (wfhData.code === 200 && Array.isArray(wfhData.data)) {
                    // Map WFH events
                    const wfhEvents = wfhData.data.map(event => ({
                        title: event.title,
                        start: event.start,
                        end: event.end,
                        backgroundColor: event.title === 'WFH (Full Day)' ? '#6941C6' : '#B3B3FF' // Full Day WFH in purple, others in light purple
                    }));
        
                    // Map and filter Leave events for the logged-in user
                    const leaveEvents = leaveData.data
                        .filter(leave => leave.staff_id === parseInt(staffId)) // Filter for logged-in user
                        .map(leave => ({
                            title: `Leave`,
                            start: `${leave.leave_date}T09:00:00`, // Set start time for leave events
                            end: `${leave.leave_date}T17:00:00`, // Set end time for leave events
                            backgroundColor: '#FF6347' // Red for Leave
                        }));
        
                    // Create a set of leave dates for quick lookup
                    const leaveDates = new Set(leaveEvents.map(leave => leave.start.split('T')[0]));
        
                    // Filter out WFH and in-office events that overlap with leave dates
                    const filteredEvents = wfhEvents.filter(event => {
                        const eventDate = event.start.split('T')[0];
                        return !leaveDates.has(eventDate); // Exclude if the date is in the leave dates
                    });
        
                    // Combine leave events and filtered WFH events
                    this.events = [...filteredEvents, ...leaveEvents];
        
                    this.initCalendar(); // Initialize the calendar after fetching data
                    this.updateCalendarEvents(); // Update the calendar with the new events
                } else {
                    console.error('Invalid API response format or code:', wfhData);
                }
            } catch (error) {
                console.error('Error fetching calendar data:', error);
            }
        },

        initCalendar() {
            const calendarEl = document.getElementById('calendar');
            this.calendar = new Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                height: '75%', // Set height to 100%
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay,listYear'
                },
                events: this.events,
                eventTimeFormat: {
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                },
                eventDidMount: (info) => {
                    info.el.style.backgroundColor = info.event.backgroundColor; 
                },
                dayMaxEvents: true // Allow for event overflow without scrolling
            });
            this.calendar.render();
            console.log('Calendar initialized with events:', this.events);
        
            // Add resize listener
            window.addEventListener('resize', () => {
                this.calendar.updateSize(); // Update calendar size on window resize
            });
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
                'in_office_full_day': 'In Office (Full Day)',
                'leave': 'Leave' // You can add this to filter specifically for leave events if needed
            };

            const filterTitle = titleMapping[this.filterType];
            return this.events.filter(event => event.title === filterTitle || event.title.startsWith("Leave:"));
        }
    },
    watch: {
        filterType() {
            this.updateCalendarEvents();
        }
    }
}).mount('#app');
