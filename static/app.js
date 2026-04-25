const API_URL = "https://pdis-backend-v3.onrender.com";

// ✅ 1. Aqlli Fetch (Token o'lsa avtomatik yangilaydi)
async function authFetch(url, options = {}) {
    let accessToken = localStorage.getItem('pdis_token');
    
    // Headerlarni tayyorlash
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`
    };

    let response = await fetch(API_URL + url, options);

    // Agar token muddati tugagan bo'lsa (401 xatosi)
    if (response.status === 401) {
        const refreshToken = localStorage.getItem('pdis_refresh');
        
        if (refreshToken) {
            // Serverdan yangi access token so'raymiz
            const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('pdis_token', data.access_token);
                
                // Eski so'rovni yangi token bilan qayta urinib ko'ramiz
                options.headers['Authorization'] = `Bearer ${data.access_token}`;
                return await fetch(API_URL + url, options);
            }
        }
        // Agar refresh ham o'tmasa yoki bo'lmasa - logout
        doLogout();
    }
    return response;
}

// ✅ 2. Login funksiyasi
async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showToast("Email va parolni kiriting!", 'error');
        return;
    }

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
            localStorage.setItem('pdis_token', data.access_token);
            localStorage.setItem('pdis_refresh', data.refresh_token);
            localStorage.setItem('pdis_email', email);
            
            showToast('Xush kelibsiz! 👋');
            setTimeout(() => location.reload(), 1000); // Sahifani yangilab dashboardga o'tamiz
        } else {
            showToast(data.detail || "Kirishda xatolik", 'error');
        }
    } catch (error) {
        showToast("Server bilan aloqa yo'q", 'error');
    }
}

// ✅ 3. Foydalanuvchi qo'shish (ID-siz!)
async function addUser() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();

    if (!name || !email) {
        showToast("Ism va emailni kiriting!", 'error');
        return;
    }

    try {
        const response = await authFetch('/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email }) // Faqat name va email!
        });

        if (response.ok) {
            showToast('✅ Foydalanuvchi qo\'shildi!');
            document.getElementById('user-name').value = '';
            document.getElementById('user-email').value = '';
            loadUsers(); // Ro'yxatni yangilash
            loadStats(); // Dashboard raqamlarini yangilash
        } else {
            const err = await response.json();
            showToast(err.detail || "Xato yuz berdi", 'error');
        }
    } catch (e) {
        showToast("Xato!", 'error');
    }
}

// ✅ 4. Xarajat qo'shish (ID-siz!)
async function addExpense() {
    const category = document.getElementById('exp-category').value.trim();
    const amount = parseFloat(document.getElementById('exp-amount').value);

    if (!category || !amount) {
        showToast("Kategoriya va miqdorni kiriting!", 'error');
        return;
    }

    try {
        const response = await authFetch('/expenses/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, amount }) // Faqat category va amount!
        });

        if (response.ok) {
            showToast('✅ Xarajat qo\'shildi!');
            document.getElementById('exp-category').value = '';
            document.getElementById('exp-amount').value = '';
            loadExpenses();
            loadStats();
        }
    } catch (e) {
        showToast("Xato!", 'error');
    }
}

// ✅ 5. Logout
function doLogout() {
    localStorage.clear();
    location.reload();
}1