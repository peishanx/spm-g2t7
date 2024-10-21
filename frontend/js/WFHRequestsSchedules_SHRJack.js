document.addEventListener('DOMContentLoaded', function () {
    const dept = sessionStorage.getItem('dept'); // Get department from session storage
    let allRequests = []; // Declare allRequests here
    let recordsPerPage = 10; // Default number of records to display per page
    let currentPage = 1; // Start on the first page

    if (!dept) {
        console.error('Department is missing from session storage.');
        return;
    }

    // Set the current date to the date input
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('requestdate').value = today;

    // Fetch all employees in the same department
    fetchWFHDataByDate(today); // Initial fetch for today’s date

    // Fetch data when the date changes
    document.getElementById('requestdate').addEventListener('change', function () {
        fetchWFHDataByDate(this.value);
    });

    // Fetch data when the records per page selection changes
    document.getElementById('recordsPerPage').addEventListener('change', function () {
        recordsPerPage = parseInt(this.value, 10); // Update the number of records per page
        renderTable(); // Re-render the table with the new setting
    });

    function fetchWFHDataByDate(selectedDate) {
        console.log('Selected date for WFH fetch:', selectedDate); // Log selected date
        fetch(`http://localhost:5000/request/approved/${dept}?date=${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                console.log('WFH data fetch response:', data); // Log response for WFH data
                if (data.code === 200) {
                    allRequests = data.data; // Store all requests for filtering
                    
                    // Fetch leave data for the selected date as well
                    fetchLeaveData(selectedDate).then(leaveData => {
                        console.log('Leave data:', leaveData); // Log leave data
                        combineData(allRequests, leaveData); // Merge both data sets
                        renderTable(); // Render the initial table on load
                    });
                } else {
                    console.error('Error fetching requests:', data.message);
                }
            })
            .catch(error => {
                console.error('Error during the fetch operation:', error);
            });
    }

    function fetchLeaveData(selectedDate) {
        const leavePromises = allRequests.map(request =>
            checkLeaveStatus(request.sid, selectedDate)
        );

        return Promise.all(leavePromises).then(leaveStatuses => {
            return leaveStatuses.map((leaveStatus, index) => ({
                ...allRequests[index],
                leave_status: leaveStatus // Add leave status to each request
            }));
        });
    }

    function combineData(requests, leaveData) {
        const tableBody = document.getElementById('wfhRequestTableBody');
        tableBody.innerHTML = ''; // Clear the table
    
        // Create a flag to determine if any approved WFH requests are found
        let hasApprovedWFH = false;
    
        requests.forEach(request => {
            const leaveEntry = leaveData.find(leave => leave.sid === request.sid) || {};
            const leaveStatus = leaveEntry.leave_status || "N/A"; // Get leave status or default to "N/A"
    
            // Initialize WFH and In Office statuses
            let wfhStatus = "N/A"; // Default to N/A
            let inOfficeStatus = "In Office (Full Day)"; // Default to In Office Full Day
    
            // Check for approved WFH statuses
            if (request.wfh_status === "WFH (AM)") {
                wfhStatus = "WFH (AM)";
                inOfficeStatus = "In Office (PM)";
                hasApprovedWFH = true;
            } else if (request.wfh_status === "WFH (PM)") {
                wfhStatus = "WFH (PM)";
                inOfficeStatus = "In Office (AM)";
                hasApprovedWFH = true;
            } else if (request.wfh_status === "WFH (Full Day)") {
                wfhStatus = "WFH (Full Day)";
                inOfficeStatus = "N/A"; // No office hours for full day
                hasApprovedWFH = true;
            }
    
            // If the employee is on leave, set WFH status to N/A
            if (leaveStatus === "On Leave") {
                wfhStatus = "N/A";
                inOfficeStatus = "N/A"; 
            }
    
            // Set the final status properties
            request.wfh_status = wfhStatus;
            request.in_office_status = inOfficeStatus;
            request.leave_status = leaveStatus;
    
            // Create a new table row with the final statuses
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${request.employee_first_name} ${request.employee_last_name}</td>
                <td>${request.department}</td>
                <td>${request.position}</td>
                <td>${request.wfh_status}</td>
                <td>${request.in_office_status}</td>
                <td>${request.leave_status}</td>
            `;
            tableBody.appendChild(row); 
        });
    
        // If no approved WFH requests were found, set all statuses accordingly
        if (!hasApprovedWFH) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="6">In Office (Full Day)</td> <!-- Span across all columns -->
            `;
            tableBody.appendChild(row);
        }
    
        renderTable();
    }
    
    

    function renderTable() {
        const tableBody = document.getElementById('wfhRequestTableBody');
        tableBody.innerHTML = ''; // Clear the table for repopulation

        // Calculate start and end indices for the current page
        const startIndex = (currentPage - 1) * recordsPerPage;
        const endIndex = startIndex + recordsPerPage;
        const paginatedRequests = allRequests.slice(startIndex, endIndex); 

        paginatedRequests.forEach(request => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${request.employee_first_name} ${request.employee_last_name}</td>
                <td>${request.department}</td>
                <td>${request.position}</td>
                <td>${request.wfh_status}</td>
                <td>${request.in_office_status || "N/A"}</td>
                <td>${request.leave_status}</td>
            `;
            tableBody.appendChild(row);
        });

        updatePaginationControls();
    }

    function updatePaginationControls() {
        const totalRecords = allRequests.length;
        const totalPages = Math.ceil(totalRecords / recordsPerPage);
        const showingText = `Showing ${(currentPage - 1) * recordsPerPage + 1} to ${Math.min(currentPage * recordsPerPage, totalRecords)} out of ${totalRecords} records`;
        document.getElementById('recordDisplayText').textContent = showingText;

        const paginationContainer = document.querySelector('.page-numbers');
        paginationContainer.innerHTML = ''; 

        const prevButton = document.createElement('button');
        prevButton.textContent = '<';
        prevButton.disabled = currentPage === 1;
        prevButton.addEventListener('click', () => {
            currentPage--;
            renderTable();
        });
        paginationContainer.appendChild(prevButton);

        for (let page = 1; page <= totalPages; page++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = page;
            pageButton.classList.toggle('active', page === currentPage);
            pageButton.addEventListener('click', () => {
                currentPage = page;
                renderTable();
            });
            paginationContainer.appendChild(pageButton);
        }

        const nextButton = document.createElement('button');
        nextButton.textContent = '>';
        nextButton.disabled = currentPage === totalPages;
        nextButton.addEventListener('click', () => {
            currentPage++;
            renderTable();
        });
        paginationContainer.appendChild(nextButton);
    }

    // Function to check the leave status of an employee
    function checkLeaveStatus(employeeId, selectedDate) {
        return fetch(`http://localhost:5000/leaves/check/${employeeId}?date=${selectedDate}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.code === 200) {
                    return data.leaveDates.length > 0 ? "On Leave" : "N/A"; 
                }
                return "N/A"; 
            })
            .catch(error => {
                console.error('Error fetching leave status:', error);
                return "N/A"; 
            });
    }

    // Event listeners for filters
    document.getElementById('wfhtypedropdown').addEventListener('change', applyFilters);
    document.getElementById('requestdate').addEventListener('change', applyFilters);
    document.getElementById('clearfilters').addEventListener('click', clearFilters);

    // Function to apply filters
    function applyFilters() {
        const wfhTypeFilter = document.getElementById('wfhtypedropdown').value;
        const requestDateFilter = document.getElementById('requestdate').value;
    
        // Log the selected WFH type for debugging
        console.log('Selected WFH Type Filter:', wfhTypeFilter);
        console.log('Selected Request Date Filter:', requestDateFilter); // Log selected date
    
        // Update allRequests to only include requests that match the filters
        allRequests = allRequests.filter(request => {
            // Log the current request being evaluated
            console.log('Evaluating Request:', request);
    
            // Check if the WFH type matches or if "All" is selected
            const matchesWfhType = wfhTypeFilter === 'All' || request.wfh_status === wfhTypeFilter;
    
            // Convert request_date to a comparable format
            const requestDateOnly = request.request_date ? request.request_date.split('T')[0] : null; 
            console.log(`Request Date Only: ${requestDateOnly}`); // Log formatted request date
            const matchesRequestDate = requestDateFilter === '' || requestDateOnly === requestDateFilter;
    
            // Log both match results
            console.log(`Request Matches WFH Type: ${matchesWfhType}`);
            console.log(`Request Matches Date: ${matchesRequestDate}`);
    
            // Return true only if both match
            return matchesWfhType && matchesRequestDate;
        });
    
        // Log the filtered requests to see what remains
        console.log('Filtered Requests:', allRequests);
        console.log('Request Dates:', allRequests.map(req => req.request_date));
    
        currentPage = 1; // Reset to the first page after filtering
        renderTable(); // Re-render the table to show filtered results
    }
    
    
    // Function to clear all filters
    function clearFilters() {
        document.getElementById('wfhtypedropdown').value = ''; // Reset to "All"
        document.getElementById('requestdate').value = ''; // Clear date filter
        fetchWFHDataByDate(today); // Re-fetch for today
    }
});
