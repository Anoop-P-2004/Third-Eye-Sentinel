// Open Popup
function openPopup() {
    document.getElementById('popupOverlay').style.display = 'flex';
}

// Close Popup
function closePopup() {
    document.getElementById('popupOverlay').style.display = 'none';
}

// Add Camera Function
function addCamera() {
    const cameraName = document.getElementById('cameraName').value.trim();

    if (!cameraName) {
        alert('Please enter a camera name.');
        return;
    }
    const token = localStorage.getItem('access-token');
    const path="/manage_cameras/add_camera?Authorization="+encodeURIComponent(token);
    
    // Send data to backend using fetch API
    fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: cameraName })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.flag) {
            alert('Camera added successfully!');
            location.reload(); // Refresh to show new camera
        } else {
            alert('Failed to add camera: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });

    closePopup();
}

// Navigation to Dashboard
function navigateTo(page) {
    const token = localStorage.getItem('access-token');
    window.location.href = page + "?Authorization=" + encodeURIComponent(token);
}

// Delete Camera Function
function confirmDelete(cameraName) {
    if (confirm(`Are you sure you want to delete camera: ${cameraName}?`)) {
        const token = localStorage.getItem('access-token');
        const path="/manage_cameras/delete_camera?Authorization="+encodeURIComponent(token);
        fetch(path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: cameraName })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.flag) {
                alert('Camera deleted successfully!');
                location.reload();
            } else {
                alert('Failed to delete camera: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
}
