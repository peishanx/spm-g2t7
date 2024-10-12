function toggleDropdown(dropdownId, arrowId) {
    const dropdown = document.getElementById(dropdownId);
    const arrow = document.getElementById(arrowId);
    const dropdownContainer = dropdown.parentNode; // Get the parent node (dropdown div)

    dropdownContainer.classList.toggle('show'); // Toggle the dropdown visibility
}

function navigateTo(page) {
    window.location.href = page; // The session storage data will remain intact
}