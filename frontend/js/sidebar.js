// Function to handle routing for Team Requests based on the user's role
function handleTeamRequestsClick() {
    const role = sessionStorage.getItem('rolenum');
    const position = sessionStorage.getItem('position');
    const dept = sessionStorage.getItem('dept'); 
    console.log('menu_sidebar_check:-->', 'Role:',role,'Position:',position, 'Dept:', dept);

    if (role === '1' && position === 'MD') {
        navigateTo('WFHRequestsOverview_Jack.html');  // Route for Role 1 and MD (Jack)
    } else if((role === '1' && position === 'Director') || (role === '1' && dept === 'HR') || role === '3' ){
        navigateTo('WFHRequestsOverview_ManagerDirector.html');  // Route for Role 2
    } 

    else if (role === '2') {
        navigateTo('WFHRequestsOverview_Staff.html');  // Route for Role 3
    }
}

// Function to handle routing for Team Schedules based on the user's role
function handleTeamSchedulesClick() {
    const role = sessionStorage.getItem('rolenum');
    const position = sessionStorage.getItem('position');
    const dept = sessionStorage.getItem('dept'); 
    console.log('menu_sidebar_check:-->', 'Role:',role,'Position:',position, 'Dept:', dept);

    if (role === '1' && position === 'MD') {
        navigateTo('WFHRequestsSchedules_SHRJack.html');  // Route for Role 1 and MD (Jack)
    } else if((role === '1' && position === 'Director') || (role === '1' && dept === 'HR') ){
        navigateTo('WFHRequestsSchedules_SHRJack.html');  // Route for Role 2
    } 
    else if (role === '2' || role ==='3') {
        navigateTo('WFHRequestsSchedules_Staff.html');  // Route for Role 3
    }
}

// Function to control sidebar visibility and routing based on the user's role
function controlSidebarBasedOnRole() {
    const role = sessionStorage.getItem('rolenum');
    const position = sessionStorage.getItem('position');
    const dept = sessionStorage.getItem('dept'); 
    console.log('menu_sidebar_check:-->', 'Role:',role,'Position:',position, 'Dept:', dept);

    // Apply role-based visibility and routing
    if (role === '1'  && position === 'MD') {
        document.getElementById('applyOption').style.display = 'none';  // Hide Apply option for Role 1 and MD (Jack)
        document.getElementById('myrequestoption').style.display = 'none';
        // document.getElementById('applybtn').style.display = 'none';
    } else if (role === '2') {
        document.getElementById('teamRequestsOption').style.display = 'none';  // Hide Team Requests for Role 2
        document.getElementById('organizationScheduleoption').style.display = 'none';  // Hide Team Requests for Role 2
    }
    else if (role === '3'){
        document.getElementById('organizationScheduleoption').style.display = 'none';  // Hide Team Requests for Role 3
    }
}

// Function to display sidebar and apply role-based logic
function displaysidebar() {
    // Dynamically load the sidebar HTML
    fetch('./sidebar.html')
        .then(response => response.text())
        .then(data => {
            // Inject the sidebar HTML
            document.getElementById('sidebar').innerHTML = data;

            // After loading the sidebar, apply the role-based logic
            controlSidebarBasedOnRole();

            // Bind the Team Requests click handler after the sidebar is loaded
            document.getElementById('teamRequestsOption').addEventListener('click', handleTeamRequestsClick);
            document.getElementById('teamScheduleOption').addEventListener('click', handleTeamSchedulesClick);

        })
        .catch(error => console.error('Error loading sidebar:', error));
}