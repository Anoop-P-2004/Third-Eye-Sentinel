document.addEventListener("DOMContentLoaded", () => {
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

    function showMessage(message, duration = 500) {
        messageBox.textContent = message;
        messageBox.style.display = "block";
        setTimeout(() => {
            messageBox.style.display = "none";
        }, duration);
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        
        const username = document.querySelector("input[type='text']").value;
        const password = document.querySelector("input[type='password']").value;
        
        if (!username || !password) {
            showMessage("Please enter both username and password.");
            return;
        }
        
        const data = { username, password };
        
        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.flag === 0) {
                showMessage("Login successful!");
                localStorage.setItem("access-token", result["access-token"]);
                localStorage.setItem("role", result.role);
                
                if (result.role === "user") {
                    const token = localStorage.getItem('access-token');
                    window.location.href="/view_report?Authorization="+encodeURIComponent(token);
                } else if (result.role === "admin") {
                    const token = localStorage.getItem('access-token');
                    window.location.href="/admin?Authorization="+encodeURIComponent(token);
                }
            } else {
                showMessage(result.message);
            }
        } catch (error) {
            console.error("Error:", error);
            showMessage("An error occurred. Please try again later.");
        }
    }); 
});
