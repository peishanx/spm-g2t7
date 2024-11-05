let searchQuery = '';

document.addEventListener('DOMContentLoaded', function () {
    const staffId = sessionStorage.getItem('staff_id');


    let allRequests = [];

    if (!staffId) {
        console.error('Staff ID is missing from session storage.');
        return;
    }
    const isDockerReq = window.location.hostname === 'request';
    const fetchUrlReq = isDockerReq ? 'http://request:5200/request' : 'http://localhost:5200/request';
    // Fetch WFH requests for the current employee (staffId)
    fetch(`${fetchUrlReq}/employee/${staffId}`)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200 || data.code === 404) {
                allRequests = data.data; // Store all requests for filtering
                console.log(allRequests);
                populateWFHTable(allRequests); // Initial render of all requests
            } else {
                console.error('Error fetching requests:', data.message);
            }
        })
        .catch(error => {
            console.error('Error during the fetch operation:', error);
        });

    // Event listeners for filters
    document.getElementById('statusdropdown').addEventListener('change', () => filterRequests(allRequests));
    document.getElementById('requestdate').addEventListener('change', () => filterRequests(allRequests)); // 'change' for date picker
    document.getElementById('clearfilters').addEventListener('click', () => clearFilters(allRequests));
    document.getElementById('wfhtypedropdown').addEventListener('change', () => filterRequests(allRequests));
    // Debounce function to limit the rate at which a function is called
    function debounce(func, delay) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Add event listener for search input with debounce
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(() => {
        searchQuery = searchInput.value.trim().toLowerCase();
        filterRequests(allRequests, searchQuery);
    }, 300));

});
// Function to apply the filters and update the table
function filterRequests(allRequests) {
    const statusFilter = document.getElementById('statusdropdown').value;
    const wfhTypeFilter = document.getElementById('wfhtypedropdown').value;
    const requestDateFilter = document.getElementById('requestdate').value; // Assuming it's a date picker input

    // Filter the requests based on selected filters
    const filteredRequests = allRequests.filter(request => {
        const matchesStatus = statusFilter === '' || request.status === statusFilter;
        const matchesWfhType = wfhTypeFilter === '' || request.wfh_type === wfhTypeFilter;
        // Extract only the date part from request.request_date
        const requestDateOnly = request.request_date.split('T')[0]; // Get the date part (YYYY-MM-DD) from ISO format
        const matchesRequestDate = requestDateFilter === '' || requestDateOnly === requestDateFilter; // Compare only the date

        const matchesSearchQuery = searchQuery === '' ||
            `${request.fname} ${request.lname}`.toLowerCase().includes(searchQuery) ||
            request.reason.toLowerCase().includes(searchQuery) ||
            request.status.toLowerCase().includes(searchQuery) ||
            request.wfh_type.toLowerCase().includes(searchQuery) ||
            requestDateOnly.includes(searchQuery);
        // Return true if all conditions match (no priority for any filter)
        return matchesStatus && matchesWfhType && matchesRequestDate && matchesSearchQuery;
    });


    // Repopulate the table with filtered results
    populateWFHTable(filteredRequests);
}

// Function to clear all filters and show all requests
function clearFilters(allRequests) {
    document.getElementById('statusdropdown').value = ''; // Reset to "All"
    document.getElementById('wfhtypedropdown').value = ''; // Reset to "All"
    document.getElementById('requestdate').value = ''; // Clear date filter
    // Reset search query and input field
    searchQuery = '';
    document.getElementById('searchInput').value = '';
    populateWFHTable(allRequests); // Show all requests again
}

// Function to format the date
function formatDate(dateString, requestdate) {
    const date = new Date(dateString);
    const requesteddate = new Date(requestdate);
    const options = { weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit' };
    if (dateString == null) {
        const formattedDate = requesteddate.toLocaleDateString('en-GB', options).replace(/,/, '');
        console.log(formattedDate);
        return `${formattedDate}`;
    }
    else if (requestdate == null) {
        const formattedDate = date.toLocaleDateString('en-GB', options).replace(/,/, '');
        const timeString = date.toLocaleTimeString('en-GB');
        return `${formattedDate}, ${timeString}`;
    }

}
// Function to truncate strings
function truncateString(str) {
    const maxLength = 50
    if (str.length > maxLength) {
        return str.slice(0, maxLength) + '...';
    }
    return str;
}

// Function to populate the HTML table with WFH requests
function populateWFHTable(requests) {
    const tableBody = document.getElementById('wfhRequestTableBody');
    const applybtn = document.getElementById('applybtn');
    const staffId = sessionStorage.getItem('staff_id');
    const dept = sessionStorage.getItem('dept');
    if (staffId == "130002" && dept == "CEO") {
        applybtn.style.display = 'none';
    }
    tableBody.innerHTML = ''; // Clear the table before adding new rows

    if (!requests || requests.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7">No requests found</td></tr>';
        return;
    }

    requests.forEach(request => {
        // Concatenate first name and last name
        const fullName = `${request.fname} ${request.lname}`;
        sessionStorage.setItem('requestStaffname', fullName);


        const formattedCreatedAt = formatDate(request.createdAt, null);
        const formattedRequestDate = formatDate(null, request.request_date);
        const truncatedReason = truncateString(request.reason);
        console.log(request)
        const row = document.createElement('tr');
        row.id = "requestdetails";
        const isDockerEmp = window.location.hostname === 'employee';
        const fetchUrlEmp = isDockerEmp ? 'http://employee:5100/employee' : 'http://localhost:5100/employee';
        // const managername;
        if (request.updated_by != null) {
            fetch(`${fetchUrlEmp}/${request.updated_by}`)
                .then(response => response.json())
                .then(data => {
                    if (data.code === 200) {
                        const managerdata = data.data; // Store all requests for filtering
                        console.log(managerdata);
                        const managername = managerdata["Staff_FName"] + " " + managerdata["Staff_LName"];
                        sessionStorage.setItem('managername', managername);
                        console.log(request.approvalcount)
                        row.innerHTML = `
                            <td>${formattedCreatedAt}</td>
                            <td>${formattedRequestDate}</td>
                            <td>${truncatedReason}</td>
                            <td>${request.wfh_type}</td>
                            <td>${request.approvalcount}</td>
                            <td>${managername}</td>
                            <td>${request.status}</td>
                            <td><i class="fa-solid fa-ellipsis"></i></td>
                
                        `;
                        // Add event listener to the row or icon for click navigation
                        row.addEventListener('click', () => {
                            sessionStorage.setItem('selectedRequestId', request.rid);
                            console.log(request.sid)
                            navigateTo('WFHRequestDetails.html');
                        });

                        // Optional: You can also add a separate listener for the ellipsis icon
                        const ellipsisIcon = row.querySelector('.fa-ellipsis');
                        ellipsisIcon.addEventListener('click', (event) => {
                            event.stopPropagation(); // Prevent the row click from firing
                            sessionStorage.setItem('selectedRequestId', request.rid);
                            console.log(request.sid)
                            navigateTo('WFHRequestDetails.html');
                        });
                        row.id = "requestdetails";
                        tableBody.appendChild(row);
                    } else {
                        console.error('Error fetching requests:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error during the fetch operation:', error);
                });


        }
        else {
            row.innerHTML = `
            <td>${formattedCreatedAt}</td>
            <td>${formattedRequestDate}</td>
            <td>${truncatedReason}</td>
            <td>${request.wfh_type}</td>
            <td>${request.approvalcount}</td>
            <td>${request.updated_by ? request.updated_by : 'N/A'}</td>
            <td>${request.status}</td>
            <td><i class="fa-solid fa-ellipsis"></i></td>

        `;
            // Add event listener to the row or icon for click navigation
            row.addEventListener('click', () => {
                sessionStorage.setItem('selectedRequestId', request.rid);
                console.log(request.sid)
                navigateTo('WFHRequestDetails.html');
            });

            // Optional: You can also add a separate listener for the ellipsis icon
            const ellipsisIcon = row.querySelector('.fa-ellipsis');
            ellipsisIcon.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent the row click from firing
                sessionStorage.setItem('selectedRequestId', request.rid);
                console.log(request.sid)
                navigateTo('WFHRequestDetails.html');
            });
            row.id = "requestdetails";
            tableBody.appendChild(row);
        }
    });
}
