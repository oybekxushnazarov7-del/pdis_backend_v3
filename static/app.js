const API_URL = "https://pdis-backend-v3.onrender.com";

// ✅ 1. Smart Fetch (Auto-refresh token if available)
async function authFetch(url, options = {}) {
    let accessToken = localStorage.getItem('pdis_token');

    // Prepare headers
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`
    };

    let response = await fetch(API_URL + url, options);

    // If token expired (401 error)
    if (response.status === 401) {
        const refreshToken = localStorage.getItem('pdis_refresh');

        if (refreshToken) {
            // Request new access token from server
            const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('pdis_token', data.access_token);

                // Retry request with new token
                options.headers['Authorization'] = `Bearer ${data.access_token}`;
                return await fetch(API_URL + url, options);
            }
        }
        // If refresh fails or token doesn't exist - logout
        doLogout();
    }
    return response;
}

// ✅ 2. Login Function
async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showToast("Please enter email and password!", 'error');
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

            showToast('Welcome! 👋');
            setTimeout(() => location.reload(), 1000); // Reload page to dashboard
        } else {
            showToast(data.detail || "Login error", 'error');
        }
    } catch (error) {
        showToast("No connection to server", 'error');
    }
}

// ✅ 3. Add User (without ID)
async function addUser() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();

    if (!name || !email) {
        showToast("Please enter name and email!", 'error');
        return;
    }

    try {
        const response = await authFetch('/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email }) // Only name and email!
        });

        if (response.ok) {
            showToast('✅ User added!');
            document.getElementById('user-name').value = '';
            document.getElementById('user-email').value = '';
            loadUsers(); // Refresh user list
            loadStats(); // Refresh dashboard stats
        } else {
            const err = await response.json();
            showToast(err.detail || "Error occurred", 'error');
        }
    } catch (e) {
        showToast("Error!", 'error');
    }
}

// ✅ 4. Add Expense (without ID)
async function addExpense() {
    const category = document.getElementById('exp-category').value.trim();
    const amount = parseFloat(document.getElementById('exp-amount').value);

    if (!category || !amount) {
        showToast("Please enter category and amount!", 'error');
        return;
    }

    try {
        const response = await authFetch('/expenses/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, amount }) // Only category and amount!
        });

        if (response.ok) {
            showToast('✅ Expense added!');
            document.getElementById('exp-category').value = '';
            document.getElementById('exp-amount').value = '';
            loadExpenses();
            loadStats();
        }
    } catch (e) {
        showToast("Error!", 'error');
    }
}

// ✅ 5. Logout Function
function doLogout() {
    localStorage.clear();
    location.reload();
} 1