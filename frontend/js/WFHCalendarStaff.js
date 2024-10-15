let tokenClient;
let accessToken = null;

// Check for employee ID and redirect to login if missing
function getEmployeeId() {
    const sid = sessionStorage.getItem('staff_id');
    if (!sid) {
      console.error('Employee ID not found in session storage. Redirecting to login page.');
      window.location.href = 'login.html';
    } else {
      console.log('Employee ID found:', sid); // Debugging: Check if ID is found before redirection
    }
    return sid;
  }

function initializeGoogleCalendar() {
  tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: '', // replace with actual client id 
    scope: 'https://www.googleapis.com/auth/calendar.events',
    callback: (tokenResponse) => {
      accessToken = tokenResponse.access_token;
      fetchApprovedRequests(); // Automatically fetch approved requests after obtaining the access token
    },
  });
}

function requestAccessToken() {
  if (!accessToken) {
    tokenClient.requestAccessToken(); // Automatically request the access token
  } else {
    fetchApprovedRequests(); // If access token is already available, fetch data immediately
  }
}

function refreshCalendarIframe() {
    const calendarIframe = document.getElementById("calendarIframe");
    if (calendarIframe) {
        // Reload the iframe by updating its src attribute
        const src = calendarIframe.src;
        calendarIframe.src = src;
        console.log("Calendar iframe refreshed");
    } else {
        console.error("Calendar iframe not found");
    }
}

function addEventToCalendar(requestDate, type, rid) {
    let processedRequests = JSON.parse(localStorage.getItem('processedRequests') || '[]');
    
    if (processedRequests.includes(rid)) {
        console.log(`Event for request ID ${rid} already created, skipping.`);
        return;
    }

    processedRequests.push(rid);
    localStorage.setItem('processedRequests', JSON.stringify(processedRequests));

    let startTime, endTime,summary;

    if (type === "AM") {
        startTime = "09:00:00";
        endTime = "12:00:00";
        summary = 'WFH (AM)';
    } else if (type === "PM") {
        startTime = "13:00:00";
        endTime = "17:00:00";
        summary = 'WFH (PM)';
    } else { // Full Day
        startTime = "09:00:00";
        endTime = "17:00:00";
        summary = 'WFH (Full Day)';
    }

    const startDateTime = `${requestDate}T${startTime}`;
    const endDateTime = `${requestDate}T${endTime}`;

    const event = {
        summary: summary,
        start: { dateTime: startDateTime, timeZone: 'Asia/Singapore' },
        end: { dateTime: endDateTime, timeZone: 'Asia/Singapore' }
    };

    const queryStartTime = new Date(`${requestDate}T00:00:00`).toISOString();
    const queryEndTime = new Date(`${requestDate}T23:59:59`).toISOString();

    fetch(`https://www.googleapis.com/calendar/v3/calendars/d6c62e38d0acc337129c40e729e598c02515e1ea326722ca0b5ad5f2f2078214@group.calendar.google.com/events?timeMin=${queryStartTime}&timeMax=${queryEndTime}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const existingEvent = data.items.find(item => item.summary === event.summary && item.start.dateTime === startDateTime);

        if (existingEvent) {
            console.log(`Event already exists on ${requestDate} for request ID ${rid}, skipping.`);
            return;
        } else {
            return fetch('https://www.googleapis.com/calendar/v3/calendars/d6c62e38d0acc337129c40e729e598c02515e1ea326722ca0b5ad5f2f2078214@group.calendar.google.com/events', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(event)
            });
        }
    })
    .then(response => {
        if (response && !response.ok) {
            return response.json().then(error => Promise.reject(error));
        }
        return response ? response.json() : null;
    })
    .then(data => {
        if (data) {
            console.log('Event created:', data.htmlLink);
            refreshCalendarIframe();
        }
    })
    .catch(error => {
        console.error('Error creating event:', error);
        
        // Rollback in case of error
        processedRequests = processedRequests.filter(id => id !== rid);
        localStorage.setItem('processedRequests', JSON.stringify(processedRequests));
    });
}

function fetchApprovedRequests() {
    const sid = getEmployeeId();
    if (!sid) return;

    const processedRequests = JSON.parse(localStorage.getItem('processedRequests') || '[]');
    console.log('Currently processed requests:', processedRequests);

    fetch(`http://127.0.0.1:5200/request/employee/${sid}`, { method: 'GET' })
    .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const approvedRequests = data.data.filter(request => request.status === 'Approved');
                console.log('Approved requests:', approvedRequests);

                const unprocessedRequests = approvedRequests.filter(request => !processedRequests.includes(request.rid));
                console.log('Unprocessed requests:', unprocessedRequests);

                unprocessedRequests.forEach(request => {
                    const { request_date, wfh_type, rid } = request;
                    addEventToCalendar(request_date, wfh_type, rid); // Pass rid to avoid duplicate creation
                });
            } else {
                console.error('No approved requests found:', data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching requests:', error);
        });
}


// Initialize Google Calendar client and check login status on page load
window.onload = function() {
  const sid = getEmployeeId();
  if (sid) {
    initializeGoogleCalendar();
    requestAccessToken();
  }
};