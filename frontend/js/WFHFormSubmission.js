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

    requestDates.forEach(date => {
        formData.append('request_dates', date);
    });

    // Send form data using fetch API
    fetch('http://127.0.0.1:5200/request', {
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
