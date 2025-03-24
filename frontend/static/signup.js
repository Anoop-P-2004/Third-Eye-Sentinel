document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
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

    function showMessage(message, duration = 1000) {
        messageBox.textContent = message;
        messageBox.style.display = "block";
        setTimeout(() => {
            messageBox.style.display = "none";
        }, duration);
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent form from refreshing the page

        const username = document.querySelector("input[placeholder='Username']").value.trim();
        const password = document.querySelector("input[placeholder='Password']").value.trim();
        const confirmPassword = document.querySelector("input[placeholder='Confirm Password']").value.trim();

        // Check if passwords match
        if (password !== confirmPassword) {
            showMessage("Passwords do not match!");
            return;
        }

        // Prepare data to send
        const requestData = {
            username: username,
            password: password
        };

        try {
            const response = await fetch("/signup/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.flag === 1) {
                showMessage(result.message); // Username already exists
            } else {
                showMessage(result.message); // Account created successfully
                window.location.href = "/"; // Redirect to login page
            }
        } catch (error) {
            console.error("Error:", error);
            showMessage("An error occurred. Please try again.");
        }
    });
});
