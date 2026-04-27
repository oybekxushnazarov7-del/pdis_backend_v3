// Auto-detect API URL based on environment
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? ''
    : window.location.origin;

let accessToken = localStorage.getItem('pdis_token') || '';
let refreshToken = localStorage.getItem('pdis_refresh') || '';
let userEmail = localStorage.getItem('pdis_email') || '';
let pendingVerificationEmail = localStorage.getItem('pdis_pending_verification_email') || '';
let resendCooldownSeconds = 0;
let resendCooldownInterval = null;
let expenseFilter = 'all';
let allUsers = [];
let allExpenses = [];
let trendChart = null;
let categoryChart = null;

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

function showSection(name) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    const section = document.getElementById('section-' + name);
    if (section) section.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const nav = document.getElementById('nav-' + name);
    if (nav) nav.classList.add('active');
    closeSidebar();
    if (name === 'users') loadUsers();
    if (name === 'expenses') { loadExpenses(); loadCategoryStats(); }
    if (name === 'home') loadStats();
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
    const token = localStorage.getItem('pdis_access');
    if (!token && !url.includes('/auth/')) {
        showPage('page-login');
        return null;
    }
    const headers = options.headers || {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
        const res = await fetch(API_URL + url, { ...options, headers });
        if (res.status === 401) {
            localStorage.removeItem('pdis_access');
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
            errEl.textContent = data.detail || 'Login failed!';
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
            errEl.textContent = data.detail || 'Registration failed!';
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
            errEl.textContent = data.detail || 'Verification failed!';
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
            showToast(data.detail || 'Resend failed!', 'error');
        }
    } catch (e) {
        showToast('Error resending code!', 'error');
    }
}

function doLogout() {
    accessToken = '';
    refreshToken = '';
    userEmail = '';
    localStorage.removeItem('pdis_access');
    localStorage.removeItem('pdis_refresh');
    localStorage.removeItem('pdis_email');
    showPage('page-login');
    showToast('Logged out successfully!');
}

// Dashboard Statistics and Charts
async function loadStats() {
    try {
        const [usersRes, expensesRes] = await Promise.all([
            authFetch('/users/'),
            authFetch('/expenses/')
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
                <td><button class="btn-delete" onclick="deleteUser(${u.id})">🗑 Delete</button></td>
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
    el.innerHTML = '<div class="empty-state">Loading...</div>';
    try {
        const res = await authFetch('/expenses/');
        if (!res) return;
        allExpenses = await res.json();
        if (!Array.isArray(allExpenses)) allExpenses = [];

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
            body: JSON.stringify({ category, amount })
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
