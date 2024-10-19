//!!DO NOT EDIT THIS PAGE!!//

//for dropdown menu toggling
function toggleDropdown(dropdownId, arrowId) {
    const dropdown = document.getElementById(dropdownId);
    const arrow = document.getElementById(arrowId);
    const dropdownContainer = dropdown.parentNode; // Get the parent node (dropdown div)

    dropdownContainer.classList.toggle('show'); // Toggle the dropdown visibility
}

//for page navigation in the nav bar or other pages.
function navigateTo(page) {
    window.location.href = page; // The session storage data will remain intact
}

// for page navigations esp the back button to go back to the previous page they were at
function backTo() {
    window.history.back();
    window.location.reload();
}

//for logout and clear session storage

// Create the log out confirmation modal and append it to the document body
document.addEventListener('DOMContentLoaded', function () {
    const modalHTML = `
    <div id="logoutModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center;">
        <div style="background:white; padding:20px; border-radius:8px; text-align:center;">
            <h2>Confirm Logout</h2>
            <p>Are you sure you want to log out?</p>
            <button id="confirmLogout">Yes</button>
            <button id="cancelLogout">No</button>
        </div>
    </div>
    `;
    // Insert the modal into the body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Attach event listeners for the buttons
    document.getElementById('confirmLogout').addEventListener('click', function () {
        sessionStorage.clear();
        window.location.href = 'login.html';
    });

    document.getElementById('cancelLogout').addEventListener('click', function () {
        document.getElementById('logoutModal').style.display = 'none';
    });
});

// Function to trigger logout with the modal
function logout(page) {
    // Show the modal
    document.getElementById('logoutModal').style.display = 'flex';
}