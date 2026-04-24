const API_URL = "https://pdis-backend-v2.onrender.com";

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });

    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.access_token);
        showDashboard();
    } else { alert("Xato: " + data.detail); }
}

async function showDashboard() {
    document.getElementById('auth-card').style.display = 'none';
    document.getElementById('data-section').style.display = 'block';
    
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/users/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const users = await response.json();
    const list = document.getElementById('user-list');
    list.innerHTML = users.map(u => `<li>${u.name} (${u.email})</li>`).join('');
}

function logout() {
    localStorage.clear();
    location.reload();
}