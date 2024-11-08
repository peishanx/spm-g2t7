document.getElementById('submitbtn').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent form from refreshing

    // Get form inputs
    const fromDate = new Date(document.getElementById('from-date').value);
    const toDate = new Date(document.getElementById('to-date').value);
    const type = document.getElementById('type').value;
    const reason = document.getElementById('reason').value;
    const fileInput = document.getElementById('attachment');
    const file = fileInput.files[0];
    const sid = sessionStorage.getItem('staff_id');
    const fname = sessionStorage.getItem('staff_fname');
    const lname = sessionStorage.getItem('staff_lname');
    const email = sessionStorage.getItem('email');
    console.log(`Staff ID: ${fromDate}, Name: ${toDate}, Dept: ${type}, Role: ${reason}, Position: ${fileInput}, Country: ${file}, Reportin Manager: ${sid}`);
    
    // Error display element
    const errorText = document.getElementById('errorText');
    errorText.innerHTML = ''; // Clear any previous error messages
    // Error display element
    const DateerrorText = document.getElementById('DateerrorText');
    DateerrorText.innerHTML = ''; // Clear any previous error messages

    // Today's date without time for comparison
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Validate dates
    if (!fromDate || !toDate) {
        DateerrorText.innerHTML = '*Invalid: Please select both From Date and To Date.';
        return;
    } else if (fromDate < today) {
        DateerrorText.innerHTML = '*Invalid: The From Date cannot be earlier than today.';
        return;
    } else if (toDate < fromDate) {
        DateerrorText.innerHTML = '*Invalid: The To Date cannot be earlier than the From Date.';
        return;
    }

    // Validate form
    if (!fromDate || !toDate || !type || !reason || !file) {
        errorText.innerHTML = '*Invalid: Please fill in all fields and upload a file.';
        return;
    }

    const requestDates = [];
    for (let d = fromDate; d <= toDate; d.setDate(d.getDate() + 1)) {
        requestDates.push(new Date(d).toISOString().split('T')[0]); // Push date in YYYY-MM-DD format
    }

    // Create form data object for file upload and other data
    const formData = new FormData();
    formData.append('sid', sid);
    formData.append('type', type);
    formData.append('reason', reason);
    formData.append('attachment', file);
    formData.append('fname', fname);
    formData.append('lname', lname);
    formData.append('email', email);

    requestDates.forEach(date => {
        formData.append('request_dates', date);
    });
    const isDocker = window.location.hostname === 'request';
    const fetchUrl = isDocker ? 'http://request:5200/request' : 'http://localhost:5200/request';
    // Send form data using fetch API

    // Send form data using fetch API
    // fetch('http://request:5200/request', {
    //     method: 'POST',
    //     body: formData
    // })
    fetch(fetchUrl, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('Request submitted successfully!');
            // Redirect to overview page
            window.location.href = 'WFHRequestsOverview_Staff.html';
            window.history.forward();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to submit the request.');
        });


});

// Create the notification modal
document.addEventListener('DOMContentLoaded', function () {
    const notificationHTML = `
    <div id="notificationModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center;">
        <div style="background:white; padding:20px; border-radius:8px; text-align:center;">
            <h2 id="notificationTitle">Success</h2>
            <p id="notificationMessage">This is a notification message.</p>
            <button id="closeNotification">Close</button>
        </div>
    </div>
    `;
    document.body.insertAdjacentHTML('beforeend', notificationHTML);

    document.getElementById('closeNotification').addEventListener('click', function () {
        document.getElementById('notificationModal').style.display = 'none';
        document.getElementById('Backbtn').style.display = 'none';
        const submitterStaffId = sessionStorage.getItem('submitterStaffId'); // Retrieve from sessionStorage
        const staffId = sessionStorage.getItem('staff_id');
        if (staffId == "130002") {
            window.location.href = "../WFHRequestsOverview_Jack.html"; // Redirect submitter to their requests page
        } else if (staffId == submitterStaffId) {
            window.location.href = "../WFHRequestsOverview_Staff.html"; // Redirect submitter to their requests page
        }
        else {
            window.location.href = "../WFHRequestsOverview_ManagerDirector.html"; // Redirect managers to team requests page
        }

    });
});