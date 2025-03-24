function navigateTo(page) {
    const token = localStorage.getItem('access-token');
    window.location.href = page + "?Authorization=" + encodeURIComponent(token);
}
const messageBox = document.createElement("div");
messageBox.style.position = "fixed";
messageBox.style.top = "20px";
messageBox.style.left = "50%";
messageBox.style.transform = "translateX(-50%)";
messageBox.style.padding = "10px 20px";
messageBox.style.background = "rgba(0, 0, 0, 0.8)";
messageBox.style.color = "#fff";
messageBox.style.borderRadius = "5px";
messageBox.style.display = "none";
document.body.appendChild(messageBox);

function showMessage(message, duration = 2000) {
    messageBox.textContent = message;
    messageBox.style.display = "block";
    setTimeout(() => {
        messageBox.style.display = "none";
    }, duration);
}

function confirmDelete(username) {
    if (confirm("Are you sure you want to delete this user?")) {
        // Perform the delete operation using fetch API
        const token = localStorage.getItem('access-token');
        const path="/manage_user/delete_user?Authorization="+encodeURIComponent(token)+"&username="+username;
        fetch(path)
        .then(response => response.json())
        .then(data => {
            if (!data.flag) {
                showMessage('User deleted successfully');
                location.reload();  // Reload the page to reflect changes
            } else {
                showMessage('Error deleting user');
            }
        })
        .catch(error => {
            showMessage('Error: ' + error);
        });
    }
}

function makeAdmin(username) {
    const token = localStorage.getItem('access-token');
    const path="/manage_user/make_admin?Authorization="+encodeURIComponent(token)+"&username="+username;
    fetch(path)
    .then(response => response.json())
    .then(data => {
        if (!data.flag) {
            showMessage('User is now an admin');
            location.reload();  // Reload the page to reflect changes
        } else {
            showMessage('Error making admin');
        }
    })
    .catch(error => {
        showMessage('Error: ' + error);
    });
}