document.addEventListener("DOMContentLoaded", function () {
    const datePicker = document.getElementById("requestdate");

    // Set default date (today's date) and fetch data initially
    const today = new Date().toISOString().split('T')[0];
    datePicker.value = today;  // Set the date picker to today
    fetchWFHCounts(today); // Fetch data for today's date initially

    // Trigger fetching data when the user selects a different date
    datePicker.addEventListener("change", function () {
        const selectedDate = datePicker.value;
        if (selectedDate) {  // Check if the selected date is defined
            fetchWFHCounts(selectedDate); // Pass the selected date to the function
        }
    });
});

function fetchWFHCounts(selectedDate) {
    if (!selectedDate) {
        console.error('No date selected for fetching WFH counts.');
        return; // Exit if no date is selected
    }
    
    fetch(`http://127.0.0.1:5100/employee/wfh/counts?date=${selectedDate}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Filtered data:", data); // Check what data you get
            renderWFHData(data); // Call the function to render data
        })
        .catch(error => console.error('Error fetching data:', error));
}

function renderWFHData(data) {
    const container = document.querySelector('.departments-grid');
    let htmlContent = '';

    for (const dept in data) {
        const departmentData = data[dept];
        htmlContent += `<div class="department"><h3 class="department-name">${dept}</h3><div class="positions-grid">`;

        for (const position in departmentData) {
            const positionData = departmentData[position];
            const employeeCount = positionData.employee_count || 0; 
            const totalWFH = positionData.total || 0; 
            const leaves = positionData.leaves || 0; // Get the number of leaves
            
            // Calculate the number of employees in the office correctly
            const inOffice = employeeCount - totalWFH - leaves; // Subtract WFH and leave counts

            const wfhAM = positionData.am || 0;
            const wfhPM = positionData.pm || 0;
            const wfhFullDay = positionData.full_day || 0;

            // Each position card with a front and back side (flipping)
            htmlContent += `
                <div class="position-box" onclick="this.querySelector('.card').classList.toggle('flipped')">
                    <div class="card">
                        <div class="card-front">
                            <h4 class="position-name">${position}</h4>
                            <p>WFH: ${totalWFH}/${employeeCount}</p>
                            <p>In Office: ${inOffice < 0 ? 0 : inOffice}</p> <!-- Ensure inOffice doesn't go negative -->
                            <p>On Leave: ${leaves}</p> <!-- Display leaves count -->
                        </div>
                        <div class="card-back">
                            <p>WFH AM: ${wfhAM}</p>
                            <p>WFH PM: ${wfhPM}</p>
                            <p>WFH Full Day: ${wfhFullDay}</p>
                        </div>
                    </div>
                </div>
            `;
        }

        htmlContent += `</div></div>`; // Close the positions-grid and department divs
    }

    container.innerHTML = htmlContent; // Inject the generated HTML
}

