// View Report Details
function viewDetails(accidentId) {
    const token = localStorage.getItem('access-token');
    const path = /view_report/get_details?Authorization=${encodeURIComponent(token)}&id=${accidentId};

    fetch(path)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch accident details');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('popupAccidentId').textContent = data.id || 'N/A';
            document.getElementById('popupDate').textContent = data.date || 'N/A';
            document.getElementById('popupTime').textContent = data.time || 'N/A';

            const accidentImage = document.getElementById('accidentImage');
            if (data.image_url) {
                accidentImage.src = data.image_url;
                accidentImage.style.display = 'block';
            } else {
                accidentImage.style.display = 'none';
                alert('No image available for this accident report.');
            }

            document.getElementById('popupOverlay').style.display = 'flex';
        })
        .catch(error => {
            console.error('Error fetching details:', error);
            alert('Error fetching report details. Please try again.');
        });
}

// Close Popup
function closePopup() {
    document.getElementById('popupOverlay').style.display = 'none';
}

// Navigation to Dashboard
function navigateTo(page) {
    const token = localStorage.getItem('access-token');
    window.location.href = ${page}?Authorization=${encodeURIComponent(token)};
}

// Logout Function
function logout() {
    localStorage.removeItem('access-token');
    window.location.href = '/';
}  

// Toggle Buttons Based on Role
window.onload = function() {
    const userRole = localStorage.getItem('user-role');
    const backButton = document.getElementById('backButton');
    const logoutButton = document.getElementById('logoutButton');

    if (userRole === 'admin') {
        backButton.style.display = 'inline-block';
        logoutButton.style.display = 'none';
    } else {
        backButton.style.display = 'none';
        logoutButton.style.display = 'inline-block';
    }
};