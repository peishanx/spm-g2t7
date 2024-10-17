document.addEventListener('DOMContentLoaded', async () => {
    // Get logged-in staff ID from session storage
    const staffId = sessionStorage.getItem('staff_id'); // User Staff ID
    const roleNum = sessionStorage.getItem('rolenum'); //  User Role num

    console.log(staffId, roleNum);

    // Check if staffId and roleNum are available
    if (!staffId || !roleNum) {
        console.error("Missing required session storage values.");
        return;
    }

    try {
        // Fetch team requests using the user's staff ID
        const response = await fetch(`http://localhost:5200/request/team/${staffId}`);

        // Check if the response is OK (status code 200)
        if (response.ok) {
            const data = await response.json();
            console.log("Team Requests:", data.data);

            // Store fetched data globally for filtering
            const allRequests = data.data;

            // Call the function to populate the table with the fetched team requests
            populateWFHTable(allRequests);

            // Call the function to populate the department dropdown with unique department
            populateDepartmentnDropdown(allRequests);

            // Add event listener to dropdown for filtering
            // document.getElementById('departmentdropdown').addEventListener('change', () => {
            //     filterRequestsByPosition(allRequests);
            // });
            document.getElementById('statusdropdown').addEventListener('change', () => filterRequests(allRequests));
            document.getElementById('departmentdropdown').addEventListener('change', () => filterRequests(allRequests));
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

//truncate reason to a maximum of 10 words
function truncateReason(reason) {
    const words = reason.split(' ');
    return words.length > 10 ? words.slice(0, 10).join(' ') + '...' : reason;
}

// Function to format the date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit' };
    const formattedDate = date.toLocaleDateString('en-GB', options).replace(/,/, '');
    const timeString = date.toLocaleTimeString('en-GB');
    return `${formattedDate}, ${timeString}`;
}
// Function to populate the WFH requests table
function populateWFHTable(requests) {
    const tableBody = document.getElementById('wfhRequestTableBody');
    tableBody.innerHTML = ''; // Clear the existing table content

    // Loop through the requests and create table rows
    requests.forEach(request => {
        const row = document.createElement('tr');
        // Concatenate first name and last name
        const fullName = `${request.fname} ${request.lname}`;
        
        row.innerHTML = `
            <td>${fullName}</td>
            <td>${request.department}</td>
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

// Dropdown Options: Populate the department dropdown with unique department
function populateDepartmentnDropdown(requests) {
    const departmentDropdown = document.getElementById('departmentdropdown');
    const uniqueDepartments = new Set(); // Set to store unique positions

    // Loop through the requests to extract unique departments
    requests.forEach(request => {
        uniqueDepartments.add(request.department);
    });

    // Clear the current dropdown options
    departmentDropdown.innerHTML = '';

    //add a "all" option
    const alloption = document.createElement('option');
    alloption.textContent = "All";
    departmentDropdown.appendChild(alloption);

    // Populate the dropdown with unique departments
    uniqueDepartments.forEach(department => {
        const option = document.createElement('option');
        option.textContent = department;
        departmentDropdown.appendChild(option);
    });


}

// Filtering: Apply all filters together (department, status, WFH type, and request date)
function filterRequests(allRequests) {
    const selectedDepartment = document.getElementById('departmentdropdown').value;
    const statusFilter = document.getElementById('statusdropdown').value;
    const requestDateFilter = document.getElementById('requestdate').value; // Assuming it's a date picker input
    const wfhTypeFilter = document.getElementById('wfhtypedropdown').value;

    // Filter the requests based on selected filters
    const filteredRequests = allRequests.filter(request => {
        const matchesDepartment = selectedDepartment === "All" || selectedDepartment === '' || request.department === selectedDepartment;
        const matchesStatus = statusFilter === '' || request.status === statusFilter;
        const matchesWfhType = wfhTypeFilter === '' || request.wfh_type === wfhTypeFilter;

        // Extract only the date part from request.request_date
        const requestDateOnly = request.request_date.split('T')[0]; // Get the date part (YYYY-MM-DD) from ISO format
        const matchesRequestDate = requestDateFilter === '' || requestDateOnly === requestDateFilter; // Compare only the date

        // Return true if all conditions match (no priority for any filter)
        return matchesDepartment && matchesStatus && matchesWfhType && matchesRequestDate;
    });

    // Repopulate the table with filtered results
    populateWFHTable(filteredRequests);
}

// Clear filters: Reset all filter inputs and show all requests
function clearFilters(allRequests) {
    document.getElementById('statusdropdown').value = ''; // Reset status to "All"
    document.getElementById('wfhtypedropdown').value = ''; // Reset WFH type to "All"
    document.getElementById('requestdate').value = ''; // Clear date filter
    document.getElementById('departmentdropdown').value = 'All'; // Set department to "All"
    
    // Reapply filters with cleared values (which should show all requests)
    populateWFHTable(allRequests);
}
