// Function to format date to YYYY-MM-DD
function formatDateToYYYYMMDD(date) {
    const day = String(date.getDate()).padStart(2, '0'); // Get the day and pad with zero if needed
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Get the month (0-indexed) and pad
    const year = date.getFullYear(); // Get the full year

    return `${year}-${month}-${day}`; // Return formatted date
}

let searchQuery = '';

document.addEventListener('DOMContentLoaded', async () => {
    const staffId = sessionStorage.getItem('staff_id');
    console.log("Staff ID:", staffId); // Debug: Check if staff ID is available

    if (!staffId) {
        console.error("Missing required session storage values.");
        return;
    }

    // Get today's date and set it in the input field
    const today = formatDateToYYYYMMDD(new Date());
    console.log("Today's Date:", today); // Debug: Check today's date
    document.getElementById('requestDate').value = today; // Set today's date in the input

    // Fetch and populate the initial schedule for today's date
    await fetchAndPopulateSchedule(staffId, today, 'All'); // Fetch today's schedule and show all WFH types

    // Event listener for the filter button
    document.getElementById('filterButton').addEventListener('click', () => {
        const requestDate = document.getElementById('requestDate').value; // Get the date from the input
        console.log("Selected Request Date:", requestDate); // Log the selected date for debugging

        const wfhType = document.getElementById('wfhTypeSelect').value; // Get selected WFH type
        fetchAndPopulateSchedule(staffId, requestDate, wfhType); // Fetch the schedule for the selected date and WFH type
    });

    // Event listener for the search input
    document.getElementById('searchInput').addEventListener('input', (event) => {
        searchQuery = event.target.value.toLowerCase(); // Update the search query
        filterSchedules(); // Filter schedules based on the current search query
    });
    document.getElementById('clearfilters').addEventListener('click', () => clearFilters());

});


// Function to fetch and populate the team schedule based on the date and WFH type
async function fetchAndPopulateSchedule(staffId, requestDate, wfhType) {
    try {
        console.log("Formatted Date for API Call:", requestDate); // Log the date being sent to the API
        const response = await fetch(`http://localhost:5200/team_schedule/${staffId}?date=${requestDate}`);

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Error fetching team schedule:", errorData.message);
            return;
        }

        const data = await response.json();
        console.log("API Response:", data); // Debug: Check API response
        const teamSchedules = data.data;

        // Check if teamSchedules is an array
        if (Array.isArray(teamSchedules) && teamSchedules.length > 0) {
            populateTeamScheduleTable(teamSchedules, requestDate, wfhType); // Pass WFH type to the table population function
        } else {
            console.log("No schedules found to display."); // Debug: Notify if no schedules
            document.getElementById('teamScheduleTableBody').innerHTML = '<tr><td colspan="6">No schedules available for the selected date.</td></tr>';
        }
    } catch (error) {
        console.error("An error occurred while fetching team schedules:", error);
    }
}

// Function to populate the team schedule table based on date and WFH type
function populateTeamScheduleTable(schedules, requestDate, wfhType) {
    const tableBody = document.getElementById('teamScheduleTableBody');
    tableBody.innerHTML = ''; // Clear the existing table content

    schedules.forEach(schedule => {
        const row = document.createElement('tr');

        // Initialize WFH status and in-office status
        let wfhStatus = 'N/A';
        let inOfficeStatus = 'In Office (Full Day)'; // Default value

        // Handle leave status: set to "N/A" if not on leave
        let leaveStatus = (schedule.leave_status === "On Leave") ? "On Leave" : "N/A";

        // Handle request_date correctly
        const requestDateValue = schedule.request_date ? new Date(schedule.request_date) : null;

        // Check if request_date is valid and matches the selected date
        if (requestDateValue && !isNaN(requestDateValue.getTime())) {
            const scheduleDate = requestDateValue.toISOString().split('T')[0]; // Format to YYYY-MM-DD
            if (scheduleDate === requestDate) {
                // Set WFH status and prepend "WFH" to it
                wfhStatus = schedule.wfh_status;

                // Prepend "WFH" to the status
                if (wfhStatus === 'PM') {
                    wfhStatus = 'WFH (PM)';
                    inOfficeStatus = 'In Office (AM)';
                } else if (wfhStatus === 'AM') {
                    wfhStatus = 'WFH (AM)';
                    inOfficeStatus = 'In Office (PM)';
                } else if (wfhStatus === 'Full Day') {
                    wfhStatus = 'WFH (Full Day)';
                    inOfficeStatus = 'N/A'; // No in-office if full day WFH
                }
            }
        }

        // If on leave, set WFH and in-office status to N/A
        if (leaveStatus === "On Leave") {
            wfhStatus = 'N/A';
            inOfficeStatus = 'N/A';
        }

        // Only display the row if the WFH status matches the selected type or if it's "N/A"
        if (wfhType === 'All' || wfhStatus === wfhType) {
            // Populate the row with employee details
            row.innerHTML = `
                <td>${schedule.employee_first_name} ${schedule.employee_last_name}</td>
                <td>${schedule.department}</td>
                <td>${schedule.position}</td>
                <td>${wfhStatus}</td>
                <td>${inOfficeStatus}</td>
                <td>${leaveStatus}</td>
            `;

            tableBody.appendChild(row); // Append the new row to the table body
        }
    });
}
// Function to filter and display the team schedule based on the search query
function filterSchedules() {
    const rows = document.querySelectorAll('#teamScheduleTableBody tr'); // Get all rows in the table
    rows.forEach(row => {
        const rowData = row.innerText.toLowerCase(); // Get text content of the row
        row.style.display = rowData.includes(searchQuery) ? '' : 'none'; // Show or hide the row based on search query
    });
}
// Clear filters: Reset all filter inputs and show all data
function clearFilters() {
    document.getElementById('wfhTypeSelect').value = 'All'; // Reset type to "All"
    document.getElementById('requestDate').value = formatDateToYYYYMMDD(new Date()); // Reset to today's date
    document.getElementById('searchInput').value = ''; // Clear search input

    // Reset search query
    searchQuery = '';

    // Reapply filters with cleared values, showing all data
    const staffId = sessionStorage.getItem('staff_id'); // Retrieve staff ID
    const requestDate = document.getElementById('requestDate').value;
    const wfhType = document.getElementById('wfhTypeSelect').value;
    
    fetchAndPopulateSchedule(staffId, requestDate, wfhType); // Call function with updated parameters
}