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
        // Fetch team requests using the manager's staff ID
        const response = await fetch(`http://localhost:5200/request/team/${staffId}`);

        // Check if the response is OK (status code 200)
        if (response.ok) {
            const data = await response.json();
            console.log("Team Requests:", data.data); // Process the returned requests as needed

            // Store fetched data globally for filtering
            const allRequests = data.data;

            // Call the function to populate the table with the fetched team requests
            populateWFHTable(allRequests);

            // Call the function to populate the position dropdown with unique positions
            populatePositionDropdown(allRequests);

            document.getElementById('statusdropdown').addEventListener('change', () => filterRequests(allRequests));
            document.getElementById('teamdropdown').addEventListener('change', () => filterRequests(allRequests));
            document.getElementById('requestdate').addEventListener('change', () => filterRequests(allRequests)); // 'change' for date picker
            document.getElementById('clearfilters').addEventListener('click', () => clearFilters(allRequests));
            document.getElementById('wfhtypedropdown').addEventListener('change', () => filterRequests(allRequests));

        } else {
            const errorData = await response.json();
            console.error("Error fetching team requests:", errorData.message);
            // Handle error UI here
        }
    } catch (error) {
        console.error("An error occurred while fetching team requests:", error);
        // Handle network errors or other issues
    }
});


// Function to format the date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit' };
    const formattedDate = date.toLocaleDateString('en-GB', options).replace(/,/, '');
    const timeString = date.toLocaleTimeString('en-GB');
    return `${formattedDate}, ${timeString}`;
}
// Helper function to truncate reason to a maximum of 50 words
function truncateReason(reason) {
    const words = reason.split(' ');
    return words.length > 10 ? words.slice(0, 10).join(' ') + '...' : reason;
}
// Function to populate the WFH requests table
function populateWFHTable(requests) {
    const tableBody = document.getElementById('wfhRequestTableBody');
    tableBody.innerHTML = ''; // Clear the existing table content
    if (requests.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7">No requests found</td></tr>';
        return;
    }
    // Loop through the requests and create table rows
    requests.forEach(request => {
        const row = document.createElement('tr');
        // Concatenate first name and last name
        const fullName = `${request.fname} ${request.lname}`;
        row.innerHTML = `
            <td>${fullName}</td>
            <td>${request.position}</td>
            <td>${formatDate(request.createdAt)}</td>
            <td>${formatDate(request.request_date)}</td>
            <td>${truncateReason(request.reason)}</td>
            <td>${request.wfh_type}</td>
            <td>${request.approval_count}</td>
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

        tableBody.appendChild(row);
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

        // Return true if all conditions match (no priority for any filter)
        return matchesPosition && matchesStatus && matchesWfhType && matchesRequestDate;
    });

    // Repopulate the table with filtered results
    populateWFHTable(filteredRequests);
}

// Clear filters: Reset all filter inputs and show all requests
function clearFilters(allRequests) {
    document.getElementById('statusdropdown').value = ''; // Reset status to "All"
    document.getElementById('wfhtypedropdown').value = ''; // Reset WFH type to "All"
    document.getElementById('requestdate').value = ''; // Clear date filter
    document.getElementById('teamdropdown').value = 'All'; // Set department to "All"

    // Reapply filters with cleared values (which should show all requests)
    populateWFHTable(allRequests);
}
