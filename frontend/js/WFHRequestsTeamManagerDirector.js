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

            // Add event listener to dropdown for filtering
            document.getElementById('teamdropdown').addEventListener('change', () => {
                filterRequestsByPosition(allRequests);
            });

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


// Helper function to format dates (YYYY-MM-DD format)
function formatDate(dateString) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Function to populate the WFH requests table
function populateWFHTable(requests) {
    const tableBody = document.getElementById('wfhRequestTableBody');
    tableBody.innerHTML = ''; // Clear the existing table content

    // Loop through the requests and create table rows
    requests.forEach(request => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${request.sid}</td>
            <td>${request.position}</td>
            <td>${formatDate(request.createdAt)}</td>
            <td>${formatDate(request.request_date)}</td>
            <td>${truncateReason(request.reason)}</td>
            <td>${request.wfh_type}</td>
            <td>${request.approved_wfh}</td>
            <td>${request.approved_by ? request.approved_by : 'N/A'}</td>
            <td>${request.status}</td>
            

        `;

        tableBody.appendChild(row);
    });
}

// Function to populate the position dropdown with unique positions
function populatePositionDropdown(requests) {
    const positionDropdown = document.getElementById('teamdropdown');
    const uniquePositions = new Set(); // Set to store unique positions

    // Loop through the requests to extract unique positions
    requests.forEach(request => {
        uniquePositions.add(request.position);
    });

    // Clear the current dropdown options
    positionDropdown.innerHTML = '';

    // Populate the dropdown with unique positions
    uniquePositions.forEach(position => {
        const option = document.createElement('option');
        option.textContent = position;
        positionDropdown.appendChild(option);
    });
}

// Function to filter WFH requests by the selected position
function filterRequestsByPosition(allRequests) {
    const selectedPosition = document.getElementById('teamdropdown').value;

    // Filter the requests by selected position
    const filteredRequests = allRequests.filter(request => request.position === selectedPosition);

    // Repopulate the table with the filtered requests
    populateWFHTable(filteredRequests);
}
// Helper function to truncate reason to a maximum of 50 words
function truncateReason(reason) {
    const words = reason.split(' ');
    return words.length > 10 ? words.slice(0, 10).join(' ') + '...' : reason;
}
