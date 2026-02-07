const dosageMap = {
    paracetamol: "500 mg – Twice a day after food",
    crocin: "500 mg – Twice a day",
    azithromycin: "500 mg – Once a day",
    amoxicillin: "250 mg – Three times a day",
    cetirizine: "10 mg – Once at night",
    ibuprofen: "400 mg – Twice a day after meals"
};

// Login Modal Functions
function openLoginModal() {
    document.getElementById("loginModal").style.display = "block";
}

function closeLoginModal() {
    document.getElementById("loginModal").style.display = "none";
    document.getElementById("loginMessage").innerHTML = "";
}

window.onclick = function(event) {
    let modal = document.getElementById("loginModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

function loginUser(event) {
    event.preventDefault();
    
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    
    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(res => res.json())
    .then(data => {
        let messageEl = document.getElementById("loginMessage");
        if (data.success) {
            messageEl.style.color = "green";
            messageEl.innerHTML = "Login successful! ✓";
            setTimeout(() => {
                closeLoginModal();
                alert("Welcome, " + username + "!");
                document.querySelector(".login-btn").innerHTML = "Logout";
                document.querySelector(".login-btn").onclick = logoutUser;
            }, 1000);
        } else {
            messageEl.style.color = "red";
            messageEl.innerHTML = data.message || "Login failed!";
        }
    })
    .catch(() => {
        document.getElementById("loginMessage").style.color = "red";
        document.getElementById("loginMessage").innerHTML = "Server error!";
    });
}

function logoutUser() {
    document.querySelector(".login-btn").innerHTML = "Login";
    document.querySelector(".login-btn").onclick = openLoginModal;
    alert("Logged out successfully!");
}

function sendMessage() {
    let input = document.getElementById("userInput").value.trim();
    if (!input) return;

    let chat = document.getElementById("chat");

    chat.innerHTML += `<p><b>You:</b> ${input}</p>`;

    let typing = document.createElement("p");
    typing.innerHTML = "<i>HealHome is typing...</i>";
    chat.appendChild(typing);
    chat.scrollTop = chat.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
    })
    .then(res => res.json())
    .then(data => {
        typing.remove();
        chat.innerHTML += `<p><b>HealHome:</b> ${data.reply}</p>`;
        chat.scrollTop = chat.scrollHeight;
    })
    .catch(() => {
        typing.remove();
        chat.innerHTML += `<p><b>HealHome:</b> Server error.</p>`;
    });

    document.getElementById("userInput").value = "";
}

document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
});

function uploadFile() {
    let file = document.getElementById("fileInput").files[0];
    if (!file) {
        alert("Please select a prescription file");
        return;
    }
    
    let data = new FormData();
    data.append("file", file);

    // Show loading message
    let chat = document.getElementById("chat");
    let loading = document.createElement("p");
    loading.innerHTML = "<i>📋 Analyzing prescription...</i>";
    loading.id = "prescLoading";
    chat.appendChild(loading);
    chat.scrollTop = chat.scrollHeight;

    fetch("/upload", { method: "POST", body: data })
        .then(res => res.json())
        .then(d => {
            document.getElementById("prescLoading").remove();
            chat.innerHTML += `<p><b>Prescription Analysis:</b></p>`;
            chat.innerHTML += `<p>${d.message}</p>`;
            if (d.solutions) {
                chat.innerHTML += `<p><b>Solutions & Advice:</b></p><p>${d.solutions}</p>`;
            }
            chat.scrollTop = chat.scrollHeight;
            document.getElementById("fileInput").value = "";
        })
        .catch(() => {
            document.getElementById("prescLoading").remove();
            chat.innerHTML += `<p><b>HealHome:</b> Error processing prescription.</p>`;
        });
}

function updateDosage() {
    let med = document.getElementById("medicine").value;
    document.getElementById("dosageText").innerText =
        med ? "Dosage: " + dosageMap[med] : "";
}

function setReminder() {
    let med = document.getElementById("medicine").value;
    let time = document.getElementById("time").value;

    if (!med || !time) {
        alert("Select medicine and time");
        return;
    }

    fetch("/set-reminder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ medicine: med, time: time })
    })
    .then(res => res.json())
    .then(d => alert(d.message));
}
