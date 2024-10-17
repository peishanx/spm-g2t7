document.addEventListener('DOMContentLoaded', function () {
    const staffId = sessionStorage.getItem('staff_id');
    

    let allRequests = [];

    if (!staffId) {
        console.error('Staff ID is missing from session storage.');
        return;
    }

    // Fetch WFH requests for the current employee (staffId)
    fetch(`http://localhost:5200/request/employee/${staffId}`)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                allRequests = data.data; // Store all requests for filtering
                populateWFHTable(allRequests); // Initial render of all requests
            } else {
                console.error('Error fetching requests:', data.message);
            }
        })
        .catch(error => {
            console.error('Error during the fetch operation:', error);
        });

    // Event listeners for filters
    document.getElementById('statusdropdown').addEventListener('change', applyFilters);
    document.getElementById('wfhtypedropdown').addEventListener('change', applyFilters);
    document.getElementById('requestdate').addEventListener('change', applyFilters); // 'change' for date picker
    document.getElementById('clearfilters').addEventListener('click', clearFilters);

    // Function to apply the filters and update the table
    function applyFilters() {
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

            return matchesStatus && matchesWfhType && matchesRequestDate;
        });

        // Repopulate the table with filtered results
        populateWFHTable(filteredRequests);
    }

        // Function to clear all filters and show all requests
        function clearFilters() {
            document.getElementById('statusdropdown').value = ''; // Reset to "All"
            document.getElementById('wfhtypedropdown').value = ''; // Reset to "All"
            document.getElementById('requestdate').value = ''; // Clear date filter
            populateWFHTable(allRequests); // Show all requests again
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

// Function to truncate strings
function truncateString(str, maxLength = 50) {
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
    if (staffId == "130002" &&  dept == "CEO"){
        applybtn.style.display = 'none';
    }
    tableBody.innerHTML = ''; // Clear the table before adding new rows

    if (requests.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7">No requests found</td></tr>';
        return;
    }

    requests.forEach(request => {
        if (request.approved_by === null) {
            request.approved_by = "Not approved by any reporting manager yet";
        }

        const formattedCreatedAt = formatDate(request.createdAt);
        const formattedRequestDate = formatDate(request.request_date);
        const truncatedReason = truncateString(request.reason, 50);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formattedCreatedAt}</td>
            <td>${formattedRequestDate}</td>
            <td>${truncatedReason}</td>
            <td>${request.wfh_type}</td>
            <td>${request.approved_wfh}</td>
            <td>${request.approved_by}</td>
            <td>${request.status}</td>
        `;
        tableBody.appendChild(row);
    });
}
