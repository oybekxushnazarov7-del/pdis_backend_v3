const API_URL = window.location.origin;
console.log("Connecting to API at:", API_URL);

let accessToken = localStorage.getItem('finpulse_access') || '';
let refreshToken = localStorage.getItem('finpulse_refresh') || '';
let userEmail = localStorage.getItem('finpulse_email') || '';
let pendingVerificationEmail = localStorage.getItem('finpulse_pending_verification_email') || '';
let resendCooldownSeconds = 0;
let resendCooldownInterval = null;
let expenseFilter = 'all';
let allUsers = [];
let allExpenses = [];
let trendChart = null;
let categoryChart = null;
let userCompareChart = null;
let globalTrendChart = null;
let globalCategoryChart = null;
let selectedUserId = null;
let selectedUserName = null;

// Theme management
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('light-mode');
    if (isDark) {
        body.classList.remove('light-mode');
        localStorage.setItem('pdis_theme', 'dark');
        document.getElementById('theme-icon').textContent = '🌙';
        document.getElementById('theme-text').textContent = 'Dark';
    } else {
        body.classList.add('light-mode');
        localStorage.setItem('pdis_theme', 'light');
        document.getElementById('theme-icon').textContent = '☀️';
        document.getElementById('theme-text').textContent = 'Light';
    }
}

function initTheme() {
    const theme = localStorage.getItem('pdis_theme') || 'dark';
    if (theme === 'light') {
        document.body.classList.add('light-mode');
        document.getElementById('theme-icon').textContent = '☀️';
        document.getElementById('theme-text').textContent = 'Light';
    }
}

window.onload = () => {
    initTheme();
    if (accessToken) {
        showPage('page-dashboard');
        document.getElementById('sidebar-email').textContent = userEmail;
        loadStats();
    } else if (pendingVerificationEmail) {
        const verifyInput = document.getElementById('verify-email');
        if (verifyInput) verifyInput.value = pendingVerificationEmail;
        showPage('page-verify-email');
    } else {
        showPage('page-login');
    }
};

function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const page = document.getElementById(id);
    if (page) page.classList.add('active');
}

async function showSection(name) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    const section = document.getElementById('section-' + name);
    if (section) section.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const nav = document.getElementById('nav-' + name);
    if (nav) nav.classList.add('active');
    closeSidebar();
    
    if (name === 'users') await loadUsers();
    if (name === 'expenses') { 
        await loadExpenses(); 
        loadCategoryStats(); 
        await loadCategories(); 
    }
    if (name === 'home') await loadStats();
    if (name === 'report') await loadReport();
    
    if (name === 'admin') {
        initAdminTab();
    } else {
        stopAdminPolling();
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-sidebar-overlay');
    const isOpen = sidebar.classList.toggle('open');
    overlay.classList.toggle('show', isOpen);
    document.body.classList.toggle('menu-open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-sidebar-overlay');
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
    document.body.classList.remove('menu-open');
    document.body.style.overflow = '';
}

function showToast(msg, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function updateResendLinkUI() {
    const resendLink = document.getElementById('resend-link');
    if (!resendLink) return;
    if (resendCooldownSeconds > 0) {
        resendLink.textContent = `Resend (${resendCooldownSeconds}s)`;
        resendLink.style.pointerEvents = 'none';
        resendLink.style.opacity = '0.6';
    } else {
        resendLink.textContent = 'Resend';
        resendLink.style.pointerEvents = 'auto';
        resendLink.style.opacity = '1';
    }
}

function startResendCooldown(seconds = 60) {
    resendCooldownSeconds = seconds;
    updateResendLinkUI();
    if (resendCooldownInterval) clearInterval(resendCooldownInterval);
    resendCooldownInterval = setInterval(() => {
        resendCooldownSeconds -= 1;
        if (resendCooldownSeconds <= 0) {
            resendCooldownSeconds = 0;
            clearInterval(resendCooldownInterval);
            resendCooldownInterval = null;
        }
        updateResendLinkUI();
    }, 1000);
}

async function authFetch(url, options = {}) {
    let token = localStorage.getItem('pdis_access');
    if (!token && !url.includes('/auth/')) {
        showPage('page-login');
        return null;
    }
    const headers = options.headers || {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
        let res = await fetch(API_URL + url, { ...options, headers });
        
        // If 401, try to refresh token
        if (res.status === 401 && !url.includes('/auth/refresh')) {
            const refreshToken = localStorage.getItem('pdis_refresh');
            if (refreshToken) {
                const refreshRes = await fetch(API_URL + '/auth/refresh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
                
                if (refreshRes.ok) {
                    const data = await refreshRes.json();
                    localStorage.setItem('pdis_access', data.access_token);
                    accessToken = data.access_token;
                    
                    // Retry original request
                    headers['Authorization'] = `Bearer ${data.access_token}`;
                    return await fetch(API_URL + url, { ...options, headers });
                }
            }
            
            // If refresh fails or no refresh token, logout
            localStorage.removeItem('pdis_access');
            localStorage.removeItem('pdis_refresh');
            accessToken = '';
            refreshToken = '';
            showPage('page-login');
            return null;
        }
        return res;
    } catch (e) {
        console.error('Fetch error:', e);
        return null;
    }
}

async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();
    if (!email || !password) {
        showToast('Please fill all fields!', 'error');
        return;
    }
    try {
        const res = await fetch(API_URL + '/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('pdis_access', data.access_token);
            localStorage.setItem('pdis_refresh', data.refresh_token || '');
            localStorage.setItem('pdis_email', email);
            accessToken = data.access_token;
            userEmail = email;
            document.getElementById('login-email').value = '';
            document.getElementById('login-password').value = '';
            showPage('page-dashboard');
            document.getElementById('sidebar-email').textContent = email;
            loadStats();
        } else {
            const errEl = document.getElementById('login-error');
            let errorText = data.detail;
            if (typeof errorText === 'object') errorText = JSON.stringify(errorText);
            errEl.textContent = errorText || 'Login failed!';
            errEl.style.display = 'block';
        }
    } catch (e) {
        const errEl = document.getElementById('login-error');
        errEl.textContent = 'Unable to connect to server!';
        errEl.style.display = 'block';
    }
}

async function doRegister() {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    if (!name || !email || !password) {
        showToast('Please fill all fields!', 'error');
        return;
    }
    try {
        const res = await fetch(API_URL + '/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('reg-name').value = '';
            document.getElementById('reg-email').value = '';
            document.getElementById('reg-password').value = '';
            localStorage.setItem('pdis_pending_verification_email', email);
            pendingVerificationEmail = email;
            showPage('page-verify-email');
            document.getElementById('verify-email').value = email;
            startResendCooldown(60);
        } else {
            const errEl = document.getElementById('reg-error');
            let errorText = data.detail;
            if (typeof errorText === 'object') errorText = JSON.stringify(errorText);
            errEl.textContent = errorText || 'Registration failed!';
            errEl.style.display = 'block';
        }
    } catch (e) {
        const errEl = document.getElementById('reg-error');
        errEl.textContent = 'Unable to connect to server!';
        errEl.style.display = 'block';
    }
}

async function verifyEmailCode() {
    const email = document.getElementById('verify-email').value.trim();
    const code = document.getElementById('verify-code').value.trim();
    if (!email || !code) {
        showToast('Please fill all fields!', 'error');
        return;
    }
    try {
        const res = await fetch(API_URL + '/auth/verify-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('verify-email').value = '';
            document.getElementById('verify-code').value = '';
            localStorage.removeItem('pdis_pending_verification_email');
            pendingVerificationEmail = '';
            showToast('✅ Email verified! You can now login.');
            showPage('page-login');
        } else {
            const errEl = document.getElementById('verify-error');
            let errorText = data.detail;
            if (typeof errorText === 'object') errorText = JSON.stringify(errorText);
            errEl.textContent = errorText || 'Verification failed!';
            errEl.style.display = 'block';
        }
    } catch (e) {
        const errEl = document.getElementById('verify-error');
        errEl.textContent = 'Unable to connect to server!';
        errEl.style.display = 'block';
    }
}

async function resendVerificationCode() {
    const email = document.getElementById('verify-email').value.trim();
    if (!email) {
        showToast('Please enter your email!', 'error');
        return;
    }
    try {
        const res = await fetch(API_URL + '/auth/resend-verification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        if (res.ok) {
            showToast('✅ Verification code sent!');
            startResendCooldown(60);
        } else {
            const data = await res.json();
            let errorText = data.detail;
            if (typeof errorText === 'object') errorText = JSON.stringify(errorText);
            showToast(errorText || 'Resend failed!', 'error');
        }
    } catch (e) {
        showToast('Error resending code!', 'error');
    }
}

function doLogout() {
    accessToken = '';
    refreshToken = '';
    userEmail = '';
    selectedUserId = null;
    selectedUserName = null;
    spaAdminKey = null;
    
    localStorage.removeItem('pdis_access');
    localStorage.removeItem('pdis_refresh');
    localStorage.removeItem('pdis_email');
    
    // Clear admin session key so it asks again on next login
    sessionStorage.removeItem('spaAdminKey');
    
    // Stop any active admin polling
    stopAdminPolling();
    
    // Reset UI elements
    document.getElementById('sidebar-email').textContent = 'guest@example.com';
    const contextBox = document.getElementById('user-context-box');
    if (contextBox) contextBox.style.display = 'none';
    const activeUserName = document.getElementById('active-user-name');
    if (activeUserName) activeUserName.textContent = '';
    
    // Proactively reset Admin UI to locked state
    const adminAuth = document.getElementById('admin-auth-container');
    const adminData = document.getElementById('admin-data-container');
    if (adminAuth) adminAuth.style.display = 'block';
    if (adminData) adminData.style.display = 'none';
    const adminPwdInput = document.getElementById('spa-admin-password');
    if (adminPwdInput) adminPwdInput.value = '';
    
    showPage('page-login');
    showToast('Logged out successfully!');
}

// Dashboard Statistics and Charts
async function loadStats() {
    try {
        const query = selectedUserId ? `?user_id=${selectedUserId}` : '';
        const [usersRes, expensesRes] = await Promise.all([
            authFetch('/users/'),
            authFetch('/expenses/' + query)
        ]);
        if (!usersRes || !expensesRes) return;

        allUsers = await usersRes.json();
        allExpenses = await expensesRes.json();

        if (!Array.isArray(allUsers)) allUsers = [];
        if (!Array.isArray(allExpenses)) allExpenses = [];

        const total = allExpenses.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);
        const now = new Date();
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
        const monthExpenses = allExpenses.filter(exp => new Date(exp.created_at) >= monthStart);
        const monthTotal = monthExpenses.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);

        document.getElementById('stat-users').textContent = allUsers.length;
        document.getElementById('stat-total').textContent = total.toLocaleString() + ' UZS';
        document.getElementById('stat-month').textContent = monthTotal.toLocaleString() + ' UZS';

        updateCharts();
    } catch (error) {
        console.warn('Stats error', error);
    }
}

function updateCharts() {
    updateTrendChart();
    updateCategoryChart();
}

function updateTrendChart() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    const months = [];
    const data = [];
    for (let i = 5; i >= 0; i--) {
        const date = new Date();
        date.setMonth(date.getMonth() - i);
        const monthName = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        months.push(monthName);

        const monthStart = new Date(date.getFullYear(), date.getMonth(), 1);
        const monthEnd = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        const monthExpenses = allExpenses.filter(exp => {
            const expDate = new Date(exp.created_at);
            return expDate >= monthStart && expDate <= monthEnd;
        });
        const total = monthExpenses.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);
        data.push(total);
    }

    if (trendChart) trendChart.destroy();
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Monthly Expenses (UZS)',
                data: data,
                borderColor: '#6c63ff',
                backgroundColor: 'rgba(108, 99, 255, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#6c63ff',
                pointBorderColor: '#fff',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { color: '#7a7a9a' }, grid: { color: '#2a2a3a' } },
                x: { ticks: { color: '#7a7a9a' }, grid: { color: '#2a2a3a' } }
            }
        }
    });
}

function updateCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    const container = ctx.parentElement;
    if (allExpenses.length === 0) {
        if (categoryChart) categoryChart.destroy();
        if (container) {
            container.innerHTML = '<canvas id="categoryChart"></canvas><div class="no-data-msg" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--muted); font-size: 14px; pointer-events: none;">No data for this user</div>';
        }
        return;
    }

    // Clear "No data" message if it exists
    const msg = container.querySelector('.no-data-msg');
    if (msg) msg.remove();

    const categories = {};
    allExpenses.forEach(exp => {
        const cat = exp.category || 'Other';
        categories[cat] = (categories[cat] || 0) + Number(exp.amount);
    });

    const labels = Object.keys(categories);
    const data = Object.values(categories);
    const colors = ['#6c63ff', '#ff6584', '#43e97b', '#f1ab86', '#a8e6cf', '#ffd3b6', '#ffaaa5'];

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#e8e8f0' }
                }
            }
        }
    });
}

// Users Section
async function loadUsers() {
    const el = document.getElementById('users-list');
    el.innerHTML = '<div class="empty-state">Loading...</div>';
    try {
        const res = await authFetch('/users/');
        if (!res) return;
        allUsers = await res.json();
        if (!Array.isArray(allUsers)) allUsers = [];

        if (allUsers.length === 0) {
            el.innerHTML = '<div class="empty-state"><div class="empty-icon">👥</div>No users added yet</div>';
            return;
        }

        const html = `<table class="data-table">
            <thead><tr><th>#</th><th>Name</th><th>Email</th><th>Action</th></tr></thead>
            <tbody id="users-tbody">${allUsers.map((u, i) => `<tr class="user-row" data-email="${u.email}">
                <td class="num-cell">${i + 1}</td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>
                    <button class="export-btn" style="background: rgba(67, 233, 123, 0.1); color: var(--green); border-color: rgba(67, 233, 123, 0.2);" onclick="selectUser(${u.id}, '${u.name}')">🎯 Select</button>
                    <button class="btn-delete" onclick="deleteUser(${u.id})">🗑 Delete</button>
                </td>
            </tr>`).join('')}</tbody>
        </table>`;
        el.innerHTML = html;
    } catch (e) {
        el.innerHTML = '<div class="empty-state">Error loading users</div>';
    }
}

function filterUsers() {
    const search = document.getElementById('user-search').value.toLowerCase();
    const rows = document.querySelectorAll('.user-row');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

async function addUser() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    if (!name || !email) {
        showToast('Please fill all fields!', 'error');
        return;
    }
    try {
        const res = await authFetch('/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });
        if (!res) return;
        const data = await res.json();
        if (res.ok) {
            showToast('✅ User added successfully!');
            document.getElementById('user-name').value = '';
            document.getElementById('user-email').value = '';
            loadUsers();
            loadStats();
        } else {
            showToast(data.detail || 'Error!', 'error');
        }
    } catch (e) {
        showToast('Error!', 'error');
    }
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
        const res = await authFetch('/users/' + id, { method: 'DELETE' });
        if (!res) return;
        if (res.ok) {
            showToast('✅ User deleted successfully!');
            loadUsers();
            loadStats();
        } else {
            const d = await res.json();
            showToast(d.detail || 'Error!', 'error');
        }
    } catch (e) {
        showToast('Error!', 'error');
    }
}

function exportUsersToCSV() {
    if (allUsers.length === 0) {
        showToast('No users to export!', 'error');
        return;
    }
    const csv = 'Name,Email\n' + allUsers.map(u => `${u.name},${u.email}`).join('\n');
    downloadCSV(csv, 'users.csv');
    showToast('✅ Users exported to CSV!');
}

// Expenses Section
async function loadExpenses() {
    const el = document.getElementById('expenses-list');
    if (!el) return;
    el.innerHTML = '<div class="empty-state">Loading...</div>';
    try {
        const query = selectedUserId ? `?user_id=${selectedUserId}` : '';
        const res = await authFetch('/expenses/' + query);
        if (!res) return;
        const data = await res.json();
        allExpenses = Array.isArray(data) ? data : [];
        renderExpensesTable(el, allExpenses);
    } catch (e) {
        el.innerHTML = '<div class="empty-state">Error loading expenses</div>';
    }
}

function renderExpensesTable(el, expenses) {
    const filtered = expenses.filter(matchesExpenseFilter);
    if (filtered.length === 0) {
        el.innerHTML = '<div class="empty-state"><div class="empty-icon">💸</div>No expenses</div>';
        return;
    }
    el.innerHTML = `<table class="data-table">
        <thead><tr><th>#</th><th>Category</th><th>Amount</th><th>Date</th><th>Action</th></tr></thead>
        <tbody id="expenses-tbody">${filtered.map((exp, i) => {
        const date = new Date(exp.created_at).toLocaleDateString();
        return `<tr class="expense-row" data-category="${exp.category.toLowerCase()}">
                <td class="num-cell">${i + 1}</td>
                <td>${exp.category}</td>
                <td class="amount">${Number(exp.amount).toLocaleString()} UZS</td>
                <td>${date}</td>
                <td><button class="btn-delete" onclick="deleteExpense(${exp.id})">🗑 Delete</button></td>
            </tr>`;
    }).join('')}</tbody>
    </table>`;
}

function filterExpenses() {
    const search = document.getElementById('expense-search').value.toLowerCase();
    const rows = document.querySelectorAll('.expense-row');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

function setExpenseFilter(type) {
    expenseFilter = type;
    document.querySelectorAll('.filter-chip').forEach(chip => chip.classList.remove('active'));
    const selected = document.getElementById('filter-' + type);
    if (selected) selected.classList.add('active');
    loadExpenses();
}

function matchesExpenseFilter(expense) {
    if (expenseFilter === 'all') return true;
    const created = new Date(expense.created_at);
    const now = new Date();
    if (expenseFilter === 'today') {
        return created.toDateString() === now.toDateString();
    }
    if (expenseFilter === 'week') {
        const start = new Date(now);
        start.setDate(now.getDate() - 7);
        return created >= start;
    }
    if (expenseFilter === 'month') {
        return created.getFullYear() === now.getFullYear() && created.getMonth() === now.getMonth();
    }
    return true;
}

async function loadCategoryStats() {
    const container = document.getElementById('category-stats');
    if (!container) return;

    const categories = {};
    allExpenses.forEach(exp => {
        const cat = exp.category || 'Other';
        categories[cat] = (categories[cat] || 0) + Number(exp.amount);
    });

    if (Object.keys(categories).length === 0) {
        container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--muted);">No expenses to analyze</div>';
        return;
    }

    container.innerHTML = Object.entries(categories).map(([cat, total]) => `
        <div class="category-stat">
            <div class="category-name">${cat}</div>
            <div class="category-amount">${total.toLocaleString()} UZS</div>
        </div>
    `).join('');
}

async function loadCategories() {
    const select = document.getElementById('exp-category');
    if (!select) return;
    try {
        const res = await authFetch('/expenses/categories/list');
        if (!res) return;
        const categories = await res.json();
        if (Array.isArray(categories)) {
            const currentVal = select.value;
            select.innerHTML = '<option value="">Select category...</option>' + 
                categories.map(c => `<option value="${c.name}">${c.emoji} ${c.name}</option>`).join('');
            if (currentVal) select.value = currentVal;
        }
    } catch (e) {
        console.warn('Error loading categories', e);
    }
}

async function addExpense() {
    const category = document.getElementById('exp-category').value.trim();
    const amount = parseFloat(document.getElementById('exp-amount').value);
    if (!category || isNaN(amount) || amount <= 0) {
        showToast('Please fill all fields correctly!', 'error');
        return;
    }
    try {
        const res = await authFetch('/expenses/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, amount, user_id: selectedUserId })
        });
        if (!res) return;
        const data = await res.json();
        if (res.ok) {
            showToast('✅ Expense added successfully!');
            document.getElementById('exp-category').value = '';
            document.getElementById('exp-amount').value = '';
            loadExpenses();
            loadCategoryStats();
            loadStats();
        } else {
            showToast(data.detail || 'Error!', 'error');
        }
    } catch (e) {
        showToast('Error!', 'error');
    }
}

async function deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense?')) return;
    try {
        const res = await authFetch('/expenses/' + id, { method: 'DELETE' });
        if (!res) return;
        if (res.ok) {
            showToast('✅ Expense deleted successfully!');
            loadExpenses();
            loadCategoryStats();
            loadStats();
        } else {
            const d = await res.json();
            showToast(d.detail || 'Error!', 'error');
        }
    } catch (e) {
        showToast('Error!', 'error');
    }
}

function exportExpensesToCSV() {
    if (allExpenses.length === 0) {
        showToast('No expenses to export!', 'error');
        return;
    }
    const csv = 'Category,Amount,Date\n' + allExpenses.map(exp => {
        const date = new Date(exp.created_at).toLocaleDateString();
        return `${exp.category},${exp.amount},${date}`;
    }).join('\n');
    downloadCSV(csv, 'expenses.csv');
    showToast('✅ Expenses exported to CSV!');
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Key events
document.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
        if (document.getElementById('page-login')?.classList.contains('active')) doLogin();
        if (document.getElementById('page-register')?.classList.contains('active')) doRegister();
        if (document.getElementById('page-verify-email')?.classList.contains('active')) verifyEmailCode();
    }
    if (e.key === 'Escape') closeSidebar();
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 900) {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-sidebar-overlay');
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
        document.body.classList.remove('menu-open');
        document.body.style.overflow = '';
    }
});

// User Selection Context Logic
function selectUser(id, name) {
    selectedUserId = id;
    selectedUserName = name;
    
    // Update UI
    const contextBox = document.getElementById('user-context-box');
    const activeUserName = document.getElementById('active-user-name');
    
    if (contextBox && activeUserName) {
        contextBox.style.display = 'block';
        activeUserName.textContent = name;
    }
    
    showToast(`🎯 Switched to: ${name}`);
    showSection('home');
}

function clearUserSelection() {
    selectedUserId = null;
    selectedUserName = null;
    
    const contextBox = document.getElementById('user-context-box');
    if (contextBox) contextBox.style.display = 'none';
    
    showToast('🔙 Back to Main Account');
    showSection('home');
}

// Report Logic
async function loadReport() {
    const el = document.getElementById('report-summary-list');
    el.innerHTML = '<div class="empty-state">Loading report...</div>';
    
    try {
        const res = await authFetch('/expenses/report/summary');
        if (!res) return;
        const summary = await res.json();
        
        if (!summary || summary.length === 0) {
            el.innerHTML = '<div class="empty-state">No data for report</div>';
            return;
        }
        
        // Render Table
        el.innerHTML = `
            <table class="data-table">
                <thead><tr><th>User</th><th>Total Expenses</th></tr></thead>
                <tbody>
                    ${summary.map(s => `
                        <tr>
                            <td style="font-weight: 600;">${s.user_name}</td>
                            <td class="amount">${Number(s.total_amount).toLocaleString()} UZS</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        // Render Chart
        updateUserCompareChart(summary);
        
    } catch (e) {
        el.innerHTML = '<div class="empty-state">Error loading report</div>';
    }
}

function updateUserCompareChart(summary) {
    const ctx = document.getElementById('userCompareChart');
    if (!ctx) return;
    
    const labels = summary.map(s => s.user_name);
    const data = summary.map(s => s.total_amount);
    const colors = ['#6c63ff', '#ff6584', '#43e97b', '#f1ab86', '#a8e6cf', '#ffd3b6', '#ffaaa5'];
    
    if (userCompareChart) userCompareChart.destroy();
    
    userCompareChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Expenses (UZS)',
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#7a7a9a' },
                    grid: { color: '#2a2a3a' }
                },
                x: { 
                    ticks: { color: '#7a7a9a' },
                    grid: { display: false }
                }
            }
        }
    });
}

function togglePassword(id) {
    const input = document.getElementById(id);
    const btn = input.nextElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '👓';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}

// ================= ADMIN PLATFORM STATS LOGIC =================
let spaAdminKey = sessionStorage.getItem('spaAdminKey') || null; 
let adminPollingInterval = null;
let adminPreviousTotal = -1;

function initAdminTab() {
    if (spaAdminKey) {
        document.getElementById('admin-auth-container').style.display = 'none';
        document.getElementById('admin-data-container').style.display = 'block';
        fetchSpaAdminStats();
        fetchGlobalStats();
        startAdminPolling();
    } else {
        document.getElementById('admin-auth-container').style.display = 'block';
        document.getElementById('admin-data-container').style.display = 'none';
        document.getElementById('spa-admin-password').value = '';
        document.getElementById('spa-admin-password').focus();
    }
}

async function checkSpaAdminPassword() {
    const pwd = document.getElementById('spa-admin-password').value;
    if (!pwd) return;

    spaAdminKey = pwd;
    const success = await fetchSpaAdminStats();
    
    if (success) {
        sessionStorage.setItem('spaAdminKey', spaAdminKey);
        fetchGlobalStats();
        document.getElementById('admin-auth-container').style.display = 'none';
        document.getElementById('admin-data-container').style.display = 'block';
        document.getElementById('admin-error-msg').style.display = 'none';
        startAdminPolling();
    } else {
        document.getElementById('admin-error-msg').style.display = 'block';
        spaAdminKey = null;
        sessionStorage.removeItem('spaAdminKey');
    }
}

function startAdminPolling() {
    stopAdminPolling();
    adminPollingInterval = setInterval(() => {
        fetchSpaAdminStats();
        fetchGlobalStats();
    }, 5000);
}

function stopAdminPolling() {
    if (adminPollingInterval) {
        clearInterval(adminPollingInterval);
        adminPollingInterval = null;
    }
}

async function fetchSpaAdminStats() {
    try {
        const response = await fetch(API_URL + '/auth/stats', {
            headers: {
                'x-admin-key': spaAdminKey
            }
        });
        
        if (response.status === 403) {
            spaAdminKey = null;
            sessionStorage.removeItem('spaAdminKey');
            stopAdminPolling();
            document.getElementById('admin-auth-container').style.display = 'block';
            document.getElementById('admin-data-container').style.display = 'none';
            return false;
        }
        
        if (!response.ok) throw new Error("Network error");
        
        const data = await response.json();
        updateAdminDashboard(data);
        
        const now = new Date();
        document.getElementById('admin-last-updated').textContent = `Last updated: ${now.toLocaleTimeString()}`;
        return true;
    } catch (error) {
        console.error("Error fetching admin stats:", error);
        return false;
    }
}

function updateAdminDashboard(data) {
    const totalCountEl = document.getElementById('admin-total-users');
    const todayCountEl = document.getElementById('admin-today-users');
    const tbody = document.getElementById('admin-users-table');
    
    // Animation for update
    if (adminPreviousTotal !== -1 && adminPreviousTotal !== data.total_users) {
        totalCountEl.style.transform = 'scale(1.2)';
        totalCountEl.style.color = 'var(--green)';
        setTimeout(() => {
            totalCountEl.style.transform = 'scale(1)';
            totalCountEl.style.color = 'var(--accent)';
        }, 300);
    }
    adminPreviousTotal = data.total_users;

    totalCountEl.textContent = data.total_users;

    const todayStr = new Date().toISOString().split('T')[0];
    let todayCount = 0;

    if (data.users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 2rem; color: var(--muted);">No users yet.</td></tr>`;
        todayCountEl.textContent = "0";
        return;
    }

    let rowsHtml = '';
    data.users.forEach((user) => {
        let isNew = false;
        if (user.date === todayStr) {
            todayCount++;
            isNew = true;
        }

        const statusBadge = isNew 
            ? `<span style="background: rgba(67, 233, 123, 0.1); color: var(--green); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid rgba(67, 233, 123, 0.2);">New</span>` 
            : `<span style="background: rgba(108, 99, 255, 0.1); color: var(--accent); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid rgba(108, 99, 255, 0.2);">Active</span>`;

        rowsHtml += `
            <tr style="transition: background 0.3s;">
                <td style="color: var(--muted); font-family: monospace;">#${user.id}</td>
                <td style="font-weight: 500;">${user.name}</td>
                <td style="color: var(--muted);">${user.email}</td>
                <td>${user.date}</td>
                <td style="font-family: monospace; color: #e8e8f0;">${user.time}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });

    tbody.innerHTML = rowsHtml;
    todayCountEl.textContent = todayCount;
}

// ================= GLOBAL ANALYTICS LOGIC =================
async function fetchGlobalStats() {
    if (!spaAdminKey) return false;
    try {
        const response = await fetch(API_URL + '/auth/global-stats', {
            headers: { 'x-admin-key': spaAdminKey }
        });
        if (!response.ok) return false;
        const data = await response.json();
        
        // Update Metrics
        document.getElementById('global-total-spent').textContent = data.total_spent.toLocaleString() + ' UZS';
        document.getElementById('global-month-spent').textContent = data.month_spent.toLocaleString() + ' UZS';
        
        updateGlobalCharts(data);
        return true;
    } catch (e) {
        console.error("Global stats error:", e);
        return false;
    }
}

function updateGlobalCharts(data) {
    // 1. Global Category Chart
    const catCtx = document.getElementById('globalCategoryChart');
    if (catCtx) {
        const labels = data.categories.map(c => c.category);
        const values = data.categories.map(c => c.total);
        const colors = ['#6c63ff', '#ff6584', '#43e97b', '#f1ab86', '#a8e6cf', '#ffd3b6'];

        if (globalCategoryChart) globalCategoryChart.destroy();
        globalCategoryChart = new Chart(catCtx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{ data: values, backgroundColor: colors }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'right', labels: { color: '#e8e8f0', font: { size: 10 } } } }
            }
        });
    }

    // 2. Global Trend Chart (Last 7 Days)
    const trendCtx = document.getElementById('globalTrendChart');
    if (trendCtx) {
        const labels = data.daily_trend.map(t => t.date);
        const values = data.daily_trend.map(t => t.total);

        if (globalTrendChart) globalTrendChart.destroy();
        globalTrendChart = new Chart(trendCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Platform Daily Spending',
                    data: values,
                    backgroundColor: 'rgba(108, 99, 255, 0.4)',
                    borderColor: '#6c63ff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#7a7a9a' }, grid: { color: '#2a2a3a' } },
                    x: { ticks: { color: '#7a7a9a' }, grid: { display: false } }
                }
            }
        });
    }
}

