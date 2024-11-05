document.addEventListener('DOMContentLoaded', function () {
    const deptDropdown = document.getElementById('departmentdropdown'); // Reference to the department dropdown
    const wfhTypeDropdown = document.getElementById('wfhtypedropdown');
    const requestDateInput = document.getElementById('requestdate');
    const clearFiltersButton = document.getElementById('clearfilters');
    const searchInput = document.getElementById('searchInput'); // Add search input element

    let allRequests = [];
    let searchQuery = '';

    // Retrieve data from session storage
    const dept = sessionStorage.getItem('dept');
    const position = sessionStorage.getItem('position');
    const staffId = sessionStorage.getItem('staff_id');

    // Debugging: Log retrieved values
    console.log('Dept:', dept);
    console.log('Position from session storage:', position);
    console.log('Staff ID:', staffId);

    // Check if position is valid
    if (!position || typeof position !== 'string') {
        console.error('Position is missing or not a string:', position);
        return; // Exit if position is not valid
    }

    // Set today's date for the request date input
    const today = new Date().toISOString().split('T')[0];
    requestDateInput.value = today;

    // Event listeners
    requestDateInput.addEventListener('change', function () {
        fetchSchedulesForDate(this.value);
    });

    deptDropdown.addEventListener('change', applyFilters);
    wfhTypeDropdown.addEventListener('change', applyFilters);

    // Debounce function to limit the rate at which a function is called
    function debounce(func, delay) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Use debounced version of applyFilters for search input
    const debouncedApplyFilters = debounce(applyFilters, 300); // Adjust delay as needed

    searchInput.addEventListener('input', function () {
        searchQuery = this.value.toLowerCase();
        debouncedApplyFilters(); // Use the debounced function
    });

    clearFiltersButton.addEventListener('click', function () {
        requestDateInput.value = today;
        wfhTypeDropdown.value = "All"; // Reset WFH type filter
        deptDropdown.value = "All"; // Reset department filter
        searchQuery = ''; // Reset search query

        fetchSchedulesForDate(today);
    });

    function fetchSchedulesForDate(date) {
        let url;

        // Determine the appropriate URL based on position and department
        if (position === 'MD' && dept === 'CEO') {
            url = `http://localhost:5200/ceo/director_schedules?date=${date}`;
        } else if (position.includes('Director')) {
            url = `http://localhost:5200/director/team_schedules?staff_id=${staffId}&date=${date}&department=${dept}`;
        } else {
            console.error('Unauthorized position for viewing schedules.');
            return; // Exit if unauthorized
        }

        // Fetch schedules from the API
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.code === 200) {
                    allRequests = data.data;
                    console.log('Fetched data:', allRequests);
                    applyFilters(); // Apply filters based on fetched data
                } else {
                    console.error('Error fetching schedules:', data.message);
                }
            })
            .catch(error => console.error('Error during the fetch operation:', error));
    }

    function applyFilters() {
        const selectedWFHType = wfhTypeDropdown.value;
        const selectedDept = deptDropdown.value;

        const filteredRequests = allRequests.filter(request => {
            const matchesWFHType = selectedWFHType === "All" || request.wfh_status === selectedWFHType;
            const matchesDept = selectedDept === "All" || request.department === selectedDept;
            const matchesSearch = searchQuery === '' || (
                request.employee_first_name.toLowerCase().includes(searchQuery) ||
                request.employee_last_name.toLowerCase().includes(searchQuery) ||
                request.position.toLowerCase().includes(searchQuery) ||
                request.department.toLowerCase().includes(searchQuery)
            );

            return matchesWFHType && matchesDept && matchesSearch;
        });

        console.log('Filtered requests:', filteredRequests);
        renderTable(filteredRequests);
    }

    function renderTable(requests) {
        const tableBody = document.getElementById('wfhRequestTableBody');
        tableBody.innerHTML = '';

        if (requests.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6">No schedules available for the selected filters.</td></tr>`;
            return;
        }

        requests.forEach(request => {
            const row = document.createElement('tr');
            const isOnLeave = request.leave_status === "On Leave";

            row.innerHTML = `
                <td>${request.employee_first_name} ${request.employee_last_name}</td>
                <td>${request.department}</td>
                <td>${request.position}</td>
                <td>${isOnLeave ? 'N/A' : request.wfh_status}</td>
                <td>${isOnLeave ? 'N/A' : request.in_office_status}</td>
                <td>${request.leave_status}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Fetch schedules for today's date on page load
    fetchSchedulesForDate(requestDateInput.value);
});
