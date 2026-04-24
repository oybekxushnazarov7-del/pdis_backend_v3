const API_URL = "https://pdis-backend-v3.onrender.com"; // V3 ga o'zgargan bo'lsa tekshiring

// ✅ 1. Aqlli Fetch funksiyasi (Token o'lsa avtomatik yangilaydi)
async function authorizedFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    
    // Headerlarni tayyorlash
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    let response = await fetch(url, options);

    // Agar token muddati tugagan bo'lsa (401 xatosi)
    if (response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
            // Serverdan yangi access token so'raymiz
            const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (refreshRes.ok) {
                const refreshData = await refreshRes.json();
                localStorage.setItem('access_token', refreshData.access_token);
                
                // Eski so'rovni yangi token bilan qayta urinib ko'ramiz
                options.headers['Authorization'] = `Bearer ${refreshData.access_token}`;
                return await fetch(url, options);
            } else {
                // Refresh ham o'lgan bo'lsa - logout
                logout();
            }
        } else {
            logout();
        }
    }

    return response;
}

// ✅ 2. Login funksiyasi
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // ✅ Ikkala tokenni ham saqlaymiz
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user_email', email); // Dashboardda ko'rsatish uchun
            
            showDashboard();
        } else {
            alert("Xato: " + (data.detail || "Kirishda xatolik"));
        }
    } catch (error) {
        console.error("Login xatosi:", error);
        alert("Server bilan aloqa yo'q");
    }
}

// ✅ 3. Dashboardni ko'rsatish
async function showDashboard() {
    const authCard = document.getElementById('auth-card');
    const dataSection = document.getElementById('data-section');
    
    if(authCard) authCard.style.display = 'none';
    if(dataSection) dataSection.style.display = 'block';

    // Foydalanuvchilarni olish (authorizedFetch orqali)
    const response = await authorizedFetch(`${API_URL}/users/`);
    
    if (response.ok) {
        const users = await response.json();
        const list = document.getElementById('user-list');
        if (list) {
            list.innerHTML = users.map(u => `
                <li class="user-item">
                    <span>${u.name}</span> 
                    <small>${u.email}</small>
                </li>
            `).join('');
        }
    }
}

// ✅ 4. Logout funksiyasi
function logout() {
    localStorage.clear();
    window.location.reload();
}

// Sahifa yuklanganda holatni tekshirish
window.onload = () => {
    if (localStorage.getItem('access_token')) {
        showDashboard();
    }
};