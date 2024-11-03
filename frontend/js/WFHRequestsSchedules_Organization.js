document.addEventListener("DOMContentLoaded", function () {
    const datePicker = document.getElementById("requestdate");
    const today = new Date().toISOString().split('T')[0]; // Format today's date
    datePicker.value = today; // Set default value
    fetchWFHCounts(today); // Use today for the initial fetch

    datePicker.addEventListener("change", function () {
        const selectedDate = datePicker.value; // Retrieve the date picker value
        console.log("Selected date:", selectedDate); // Log for debugging
        if (selectedDate) {
            fetchWFHCounts(selectedDate);
        } else {
            console.error("No date selected");
        }
    });
});

function fetchWFHCounts(selectedDate) {
    console.log("Fetching WFH counts for date:", selectedDate); // Log selected date
    fetch(`http://localhost:5200/wfhcount/${selectedDate}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Filtered data:", data);
            renderWFHData(data.data);
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
            const leaves = positionData.leaves || 0;
            const inOffice = employeeCount - totalWFH - leaves;
            const wfhAM = positionData.am || 0;
            const wfhPM = positionData.pm || 0;
            const wfhFullDay = positionData.full_day || 0;

            htmlContent += `
                <div class="position-box" onclick="this.querySelector('.card').classList.toggle('flipped')">
                    <div class="card">
                        <div class="card-front">
                            <h4 class="position-name">${position}</h4>
                            <p>WFH: ${totalWFH}/${employeeCount}</p>
                            <p>In Office: ${inOffice < 0 ? 0 : inOffice}</p>
                            <p>On Leave: ${leaves}</p>
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

        htmlContent += `</div></div>`;
    }

    container.innerHTML = htmlContent;
}

