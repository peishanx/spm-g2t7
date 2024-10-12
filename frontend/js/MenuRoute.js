//!!DO NOT EDIT THIS PAGE!!//

//for dropdown menu toggling
function toggleDropdown(dropdownId, arrowId) {
    const dropdown = document.getElementById(dropdownId);
    const arrow = document.getElementById(arrowId);
    const dropdownContainer = dropdown.parentNode; // Get the parent node (dropdown div)

    dropdownContainer.classList.toggle('show'); // Toggle the dropdown visibility
}

//for page navigation in the nav bar
function navigateTo(page) {
    window.location.href = page; // The session storage data will remain intact
}

//for logout and clear session storage
function logout(page){
    sessionStorage.clear();
    window.location.href = page; 
}