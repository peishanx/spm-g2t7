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

    // Validate form
    if (!fromDate || !toDate || !type || !reason || !file) {
        alert('Please fill in all fields and upload a file.');
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
    formData.append('fname',fname);
    formData.append('lname',lname);
    formData.append('email',email);

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
