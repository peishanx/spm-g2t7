document.addEventListener("DOMContentLoaded", function () {
    const requestId = sessionStorage.getItem('selectedRequestId');
    const loggedInStaffId = sessionStorage.getItem('staff_id');
    const managername = sessionStorage.getItem('managername');
    const requesterstaffname = sessionStorage.getItem('requestStaffname');
    console.log(requesterstaffname);
    console.log(sessionStorage.getItem('requestStaffname'));
    console.log(managername);

    if (!requestId) {
        console.error('No requestId found in sessionStorage.');
        return;
    }

    // Fetch the WFH request details based on requestId
    fetch(`http://localhost:5200/request/employee/rid/${requestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const requestDetails = data.data[0];
                console.log(requestDetails);
                const requestStatus = requestDetails.status;
                submitterStaffId = requestDetails.sid; // Store submitter's staff ID here
                sessionStorage.setItem('submitterStaffId', submitterStaffId); // Store in sessionStorage                console.log(submitterStaffId);
                // Populate the WFH request data
                document.getElementById('requestdate').textContent = formatDate(requestDetails.request_date);
                document.getElementById('wfhtype').textContent = requestDetails.wfh_type;
                document.getElementById('reason').textContent = requestDetails.reason;
                if (requestStatus == "Pending"){
                    document.getElementById('reportingmanager').style.display = 'none';
                    document.getElementById('reportingmanagerlabel').style.display='none';
                    document.getElementById('approvaldatetimelabel').style.display='none';
                    document.getElementById('approvaldatetime').style.display='none';

                }
                else if (requestStatus == "Withdrawn"){
                    document.getElementById('reportingmanager').textContent = requesterstaffname;
                    document.getElementById('reportingmanagerlabel').textContent= requestStatus + " by : " ;
                    
                    document.getElementById('approvaldatetimelabel').textContent= "Date and Time of (" +  requestStatus + ") :";
                    document.getElementById('approvaldatetime').textContent=requestDetails.lastupdated;

                }
                else{
                    document.getElementById('reportingmanager').textContent = managername;
                    document.getElementById('reportingmanagerlabel').textContent= requestStatus + " by : " ;
                    
                    document.getElementById('approvaldatetimelabel').textContent= "Date and Time of (" +  requestStatus + ") :";
                    document.getElementById('approvaldatetime').textContent=requestDetails.lastupdated;
                    // console.log(requestDetails.lastupdated);
                }

                if (requestStatus == "Rejected" || requestStatus == "Withdrawn"){
                    document.getElementById('statusadditionalreason').textContent = requestDetails.additionalreason;
                    document.getElementById('additionalreason').style.display='none';
                }

                console.log(requestDetails.updated_by);
                document.getElementById('requeststatus').textContent = requestStatus;
                
                // Display the attachments if present
                document.getElementById('attachments').textContent = requestDetails.attachment || "There are no attachments";

                // Determine if the logged-in user is the submitter or their manager
                const isSubmitter = loggedInStaffId == submitterStaffId;
                // Create the back button using the createButton function
                createButton("Back", backToOverview);
                if (isSubmitter) {
                    // Logged-in user is the request submitter
                    if (requestStatus === 'Pending' || requestStatus === 'Approved') {
                        // createButton("Back",navigateTo("../WFHRequestsOverview_Staff.html"))
                        createButton("Withdraw", withdrawRequest);
                    }
                } else {
                    // Logged-in user is the reporting manager
                    if (requestStatus === 'Pending') {
                        createButton("Approve", approveRequest);
                        createButton("Reject", rejectRequest);
                    } else if (requestStatus === 'Approved') {
                        createButton("Revoke", revokeRequest);
                    }
                }
                // Fetch employee details using the sid from requestDetails
                fetch(`http://localhost:5100/employee/${submitterStaffId}`)
                    .then(response => response.json())
                    .then(employeeData => {
                        if (employeeData.code === 200) {
                            const employeeDetails = employeeData.data;
                            console.log(employeeDetails);

                            // Populate the employee data
                            document.getElementById('firstname').textContent = employeeDetails.Staff_FName;
                            document.getElementById('lastname').textContent = employeeDetails.Staff_LName;
                            document.getElementById('department').textContent = employeeDetails.Dept;
                            document.getElementById('role').textContent = employeeDetails.Position;
                        } else {
                            console.error('Error fetching employee details:', employeeData.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error during fetch operation (employee):', error);
                    });

            } else {
                console.error('Error fetching request details:', data.message);
            }
        })
        .catch(error => {
            console.error('Error during fetch operation (request):', error);
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
// Function to format the date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit' };
    const formattedDate = date.toLocaleDateString('en-GB', options).replace(/,/, '');
    return `${formattedDate}`;
}
// Function to show the notification
function showNotification(code, message) {
    document.getElementById('notificationMessage').textContent = message;
    if (code === 200) {
        document.getElementById('notificationTitle').textContent = "Successful"
    } else {
        document.getElementById('notificationTitle').textContent = "Error"
    }
    document.getElementById('notificationModal').style.display = 'flex'; // Show the modal
}

// Function to withdraw the request
function withdrawRequest(event) {
    event.preventDefault(); // Prevent form submission or page reload

    const additionalReason = document.getElementById('additionalreason').value.trim();
    const errorMessage = document.getElementById('error-message');
    const textarea = document.getElementById('additionalreason');

    textarea.classList.remove('invalid'); 
    errorMessage.style.display = 'none';

    if (!additionalReason) {
        textarea.classList.add('invalid'); 
        errorMessage.style.display = 'inline'; 
        return;
    }

    const requestId = sessionStorage.getItem('selectedRequestId');
    const staffId = sessionStorage.getItem('staff_id');
    const submitterStaffId = sessionStorage.getItem('submitterStaffId'); // Retrieve from sessionStorage
    console.log(staffId);
    console.log(submitterStaffId); // Debug to ensure submitterStaffId is correct

    fetch(`http://localhost:5200/request/${requestId}/employee/${submitterStaffId}/reporting/${staffId}/withdraw`, {
        method: "PUT",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ additional_reason: additionalReason }) // Send reason in request body
    })
        .then(response => response.json())
        .then(data => {
            showNotification(data.code, data.message);
        })
        .catch(error => {
            console.error('Error during withdraw operation:', error);
        });
}


// Function to approve the request
function approveRequest(event) {
    event.preventDefault(); // Prevent form submission or page reload

    const requestId = parseInt(sessionStorage.getItem('selectedRequestId'), 10);  // Convert to integer
    const staffId = parseInt(sessionStorage.getItem('staff_id'), 10);  // Convert to integer
    const submitterStaffId = parseInt(sessionStorage.getItem('submitterStaffId'), 10);  // Convert to integer

    console.log(requestId, staffId, submitterStaffId);

    fetch(`http://localhost:5200/request/${requestId}/employee/${submitterStaffId}/reporting/${staffId}/approve`, { method: "PUT"})
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                showNotification(data.code, data.message);
            } else {
                showNotification(data.code, data.message);
            }
        })
        .catch(error => {
            showNotification(data.code, data.message);
            console.error('Error during approve operation:', error);
        });
}

// Function to reject the request
function rejectRequest(event) {
    event.preventDefault(); // Prevent form submission or page reload

    
    const additionalReason = document.getElementById('additionalreason').value.trim();
    const errorMessage = document.getElementById('error-message');
    const textarea = document.getElementById('additionalreason');

    textarea.classList.remove('invalid'); 
    errorMessage.style.display = 'none';

    if (!additionalReason) {
        textarea.classList.add('invalid'); 
        errorMessage.style.display = 'inline'; 
        return;
    }


    const requestId = sessionStorage.getItem('selectedRequestId');
    const staffId = sessionStorage.getItem('staff_id');
    const submitterStaffId = sessionStorage.getItem('submitterStaffId'); // Retrieve from sessionStorage

    fetch(`http://localhost:5200/request/${requestId}/employee/${submitterStaffId}/reporting/${staffId}/reject`, { 
        method: "PUT",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ additional_reason: additionalReason }) // Send reason in request body
    })
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                showNotification(data.code, data.message);
            } else {
                showNotification(data.code, data.message);
            }
        })
        .catch(error => {
            showNotification(data.code, data.message);
            console.error('Error during reject operation:', error);
        });
}

//Revoke request
function revokeRequest(event) {
    event.preventDefault(); // Prevent form submission or page reload

    
    const additionalReason = document.getElementById('additionalreason').value.trim();
    const errorMessage = document.getElementById('error-message');
    const textarea = document.getElementById('additionalreason');

    textarea.classList.remove('invalid'); 
    errorMessage.style.display = 'none';

    if (!additionalReason) {
        textarea.classList.add('invalid'); 
        errorMessage.style.display = 'inline'; 
        return;
    }


    const requestId = sessionStorage.getItem('selectedRequestId');
    const staffId = sessionStorage.getItem('staff_id');
    const submitterStaffId = sessionStorage.getItem('submitterStaffId'); // Retrieve from sessionStorage

    fetch(`http://localhost:5200/request/${requestId}/employee/${submitterStaffId}/reporting/${staffId}/revoke`, {        
        method: "PUT",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ additional_reason: additionalReason }) // Send reason in request body
    })
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                showNotification(data.code, data.message);
            } else {
                showNotification(data.code, data.message);
            }
        })
        .catch(error => {
            showNotification(data.code, data.message);
            console.error('Error during reject operation:', error);
        });
}


//create button
function createButton(label, actionFunction) {
    const button = document.createElement('button');
    button.className = 'btn btn-primary';
    button.id = label+'btn';
    console.log(button.id);
    button.textContent = label;
    button.addEventListener('click', actionFunction);
    document.querySelector('.form-actions').appendChild(button);
}

// Function to navigate back based on role
function backToOverview(event) {
    event.preventDefault(); // Prevent form submission or page reload

    const staffId = sessionStorage.getItem('staff_id');
    const submitterStaffId = sessionStorage.getItem('submitterStaffId');
    console.log(staffId,submitterStaffId);
    // Check the staffId to determine where to navigate back
    if (staffId == "130002") {
        window.location.href = "../WFHRequestsOverview_Jack.html"; // Redirect specific user
    } else if (staffId == submitterStaffId) {
        window.location.href = "../WFHRequestsOverview_Staff.html"; // Redirect submitter to their requests page
    } else {
        window.location.href = "../WFHRequestsOverview_ManagerDirector.html"; // Redirect managers to team requests page
    }
}