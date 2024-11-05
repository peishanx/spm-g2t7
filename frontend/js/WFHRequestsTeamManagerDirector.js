let searchQuery = '';

document.addEventListener('DOMContentLoaded', async () => {

    // Get logged-in staff ID from session storage
    const staffId = sessionStorage.getItem('staff_id'); // Logged-in manager's ID
    const roleNum = sessionStorage.getItem('rolenum'); // Assuming you also store role number

    console.log(staffId, roleNum);

    // Check if staffId and roleNum are available
    if (!staffId || !roleNum) {
        console.error("Missing required session storage values.");
        return;
    }

    try {
        const isDockerReq = window.location.hostname === 'request';
        const fetchUrlReq = isDockerReq ? 'http://request:5200/request' : 'http://localhost:5200/request';
        // Fetch WFH requests for the current employee (staffId)
        fetch(`${fetchUrlReq}/team/${staffId}`)
            .then(response => response.json())
            .then(data => {
                if (data.code === 200 || data.code === 404) {
                    console.log("Team Requests:", data.data); // Process the returned requests as needed

                    // Store fetched data globally for filtering
                    const allRequests = data.data || [];

                    // Call the function to populate the table with the fetched team requests
                    populateWFHTable(allRequests);

                    // Call the function to populate the position dropdown with unique positions
                    populatePositionDropdown(allRequests);

                    document.getElementById('statusdropdown').addEventListener('change', () => filterRequests(allRequests));
                    document.getElementById('teamdropdown').addEventListener('change', () => filterRequests(allRequests));
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

                } else {
                    console.error('Error fetching requests:', data.message);
                }
            })
    } catch (error) {
        console.error("An error occurred while fetching team requests:", error);
        // Handle network errors or other issues
    }
});

// function searchRequests(requests, query) {
//     return requests.filter(request =>
//         `${request.fname} ${request.lname}`.toLowerCase().includes(query) ||
//         request.reason.toLowerCase().includes(query) ||
//         request.status.toLowerCase().includes(query) ||
//         request.wfh_type.toLowerCase().includes(query)
//     );
// }



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
function truncateReason(str) {
    const maxLength = 30
    if (str.length > maxLength) {
        return str.slice(0, maxLength) + '...';
    }
    return str;
}
// Function to populate the WFH requests table
function populateWFHTable(allRequests) {
    const tableBody = document.getElementById('wfhRequestTableBody');
    tableBody.innerHTML = ''; // Clear the existing table content
    if (!allRequests || allRequests.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7">No requests found</td></tr>';
        return;
    }

    // Loop through the requests and create table rows
    allRequests.forEach(request => {
        const row = document.createElement('tr');

        // Concatenate first name and last name
        const fullName = `${request.fname} ${request.lname}`;
        sessionStorage.setItem('requestStaffname', fullName);
        console.log("hii" + request);
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
                        console.log(managername)
                        const truncatedReason = truncateReason(request.reason);
                        row.innerHTML = `
                            <td>${fullName}</td>
                            <td>${request.position}</td>
                            <td>${formatDate(request.createdAt, null)}</td>
                            <td>${formatDate(null, request.request_date)}</td>
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
            <td>${fullName}</td>
            <td>${request.position}</td>
            <td>${formatDate(request.createdAt, null)}</td>
            <td>${formatDate(null, request.request_date)}</td>
            <td>${truncateReason(request.reason)}</td>
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

// Function to populate the position dropdown with unique positions
function populatePositionDropdown(requests) {
    const positionDropdown = document.getElementById('teamdropdown');
    const uniquePositions = new Set(); // Set to store unique positions

    // Loop through the requests to extract unique departments
    requests.forEach(request => {
        uniquePositions.add(request.position);
    });

    // Clear the current dropdown options
    positionDropdown.innerHTML = '';

    //add a "all" option
    const alloption = document.createElement('option');
    alloption.textContent = "All";
    positionDropdown.appendChild(alloption);

    // Populate the dropdown with unique departments
    uniquePositions.forEach(position => {
        const option = document.createElement('option');
        option.textContent = position;
        positionDropdown.appendChild(option);
    });
}


// Filtering: Apply all filters together (department, status, WFH type, and request date)
function filterRequests(allRequests) {
    const selectedTeam = document.getElementById('teamdropdown').value;
    const statusFilter = document.getElementById('statusdropdown').value;
    const requestDateFilter = document.getElementById('requestdate').value; // Assuming it's a date picker input
    const wfhTypeFilter = document.getElementById('wfhtypedropdown').value;

    // Filter the requests based on selected filters
    const filteredRequests = allRequests.filter(request => {
        const matchesPosition = selectedTeam === "All" || selectedTeam === '' || request.position === selectedTeam;
        const matchesStatus = statusFilter === '' || request.status === statusFilter;
        const matchesWfhType = wfhTypeFilter === '' || request.wfh_type === wfhTypeFilter;

        // Extract only the date part from request.request_date
        const requestDateOnly = request.request_date.split('T')[0]; // Get the date part (YYYY-MM-DD) from ISO format
        const matchesRequestDate = requestDateFilter === '' || requestDateOnly === requestDateFilter; // Compare only the date
        // Match search query if provided
        const matchesSearchQuery = searchQuery === '' ||
            `${request.fname} ${request.lname}`.toLowerCase().includes(searchQuery) ||
            request.reason.toLowerCase().includes(searchQuery) ||
            request.status.toLowerCase().includes(searchQuery) ||
            request.wfh_type.toLowerCase().includes(searchQuery) ||
            requestDateOnly.includes(searchQuery);
        // Return true if all conditions match (no priority for any filter)
        return matchesPosition && matchesStatus && matchesWfhType && matchesRequestDate && matchesSearchQuery;
    });

    //searchbar
    // Event listener for search input
    // const searchInput = document.getElementById('searchInput');
    // searchInput.addEventListener('input', () => filterRequests(allRequests));
    // Repopulate the table with filtered results
    populateWFHTable(filteredRequests);
}

// Clear filters: Reset all filter inputs and show all requests
function clearFilters(allRequests) {
    document.getElementById('statusdropdown').value = ''; // Reset status to "All"
    document.getElementById('wfhtypedropdown').value = ''; // Reset WFH type to "All"
    document.getElementById('requestdate').value = ''; // Clear date filter
    document.getElementById('teamdropdown').value = 'All'; // Set department to "All"
    document.getElementById('searchInput').value = '';
    // Reset search query and input field
    searchQuery = '';
    document.getElementById('searchInput').value = '';
    // Reapply filters with cleared values (which should show all requests)
    populateWFHTable(allRequests);
}
