const API_URL = "";

let accessToken = localStorage.getItem('pdis_token') || '';
let refreshToken = localStorage.getItem('pdis_refresh') || '';
let userEmail = localStorage.getItem('pdis_email') || '';
let pendingVerificationEmail = localStorage.getItem('pdis_pending_verification_email') || '';
let resendCooldownSeconds = 0;
let resendCooldownInterval = null;
let expenseFilter = 'all';

window.onload = () => {
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
    if (name === 'expenses') {
        loadExpenses();
        loadCategories();
    }
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
    options.headers = options.headers || {};
    if (accessToken) {
        options.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    let response = await fetch(API_URL + url, options);
    if (response.status === 401 && refreshToken) {
        const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        if (refreshRes.ok) {
            const data = await refreshRes.json();
            accessToken = data.access_token;
            localStorage.setItem('pdis_token', accessToken);
            options.headers['Authorization'] = `Bearer ${accessToken}`;
            response = await fetch(API_URL + url, options);
        } else {
            doLogout();
            return null;
        }
    }
    return response;
}

async function doRegister() {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const errEl = document.getElementById('reg-error');
    const sucEl = document.getElementById('reg-success');
    errEl.style.display = 'none';
    sucEl.style.display = 'none';
    if (!name || !email || !password) {
        errEl.textContent = 'Please fill all fields!';
        errEl.style.display = 'block';
        return;
    }
    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            pendingVerificationEmail = email;
            localStorage.setItem('pdis_pending_verification_email', pendingVerificationEmail);
            const verifyInput = document.getElementById('verify-email');
            if (verifyInput) verifyInput.value = pendingVerificationEmail;
            sucEl.textContent = '✅ Verification code sent to your email.';
            sucEl.style.display = 'block';
            setTimeout(() => showPage('page-verify-email'), 900);
        } else {
            errEl.textContent = data.detail || 'Registration error';
            errEl.style.display = 'block';
        }
    } catch (error) {
        errEl.textContent = 'Unable to reach server';
        errEl.style.display = 'block';
    }
}

async function verifyEmailCode() {
    const emailInput = document.getElementById('verify-email');
    const codeInput = document.getElementById('verify-code');
    const errEl = document.getElementById('verify-error');
    const sucEl = document.getElementById('verify-success');
    const email = emailInput.value.trim();
    const code = codeInput.value.trim();
    errEl.style.display = 'none';
    sucEl.style.display = 'none';
    if (!email || !code) {
        errEl.textContent = 'Please enter email and code';
        errEl.style.display = 'block';
        return;
    }
    try {
        const res = await fetch(`${API_URL}/auth/verify-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.removeItem('pdis_pending_verification_email');
            pendingVerificationEmail = '';
            sucEl.textContent = '✅ Email verified. Please login.';
            sucEl.style.display = 'block';
            setTimeout(() => showPage('page-login'), 1000);
        } else {
            errEl.textContent = data.detail || 'Verification error';
            errEl.style.display = 'block';
        }
    } catch (error) {
        errEl.textContent = 'Unable to reach server';
        errEl.style.display = 'block';
    }
}

async function resendVerificationCode() {
    if (resendCooldownSeconds > 0) return;
    const emailInput = document.getElementById('verify-email');
    const errEl = document.getElementById('verify-error');
    const sucEl = document.getElementById('verify-success');
    const email = emailInput.value.trim();
    errEl.style.display = 'none';
    sucEl.style.display = 'none';
    if (!email) {
        errEl.textContent = 'Please enter your email';
        errEl.style.display = 'block';
        return;
    }
    try {
        const res = await fetch(`${API_URL}/auth/resend-verification`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (res.ok) {
            sucEl.textContent = '✅ New code sent';
            sucEl.style.display = 'block';
            startResendCooldown(60);
        } else {
            errEl.textContent = data.detail || 'Unable to resend code';
            errEl.style.display = 'block';
            if (res.status === 429) startResendCooldown(60);
        }
    } catch (error) {
        errEl.textContent = 'Unable to reach server';
        errEl.style.display = 'block';
    }
}

async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const errEl = document.getElementById('login-error');
    errEl.style.display = 'none';
    if (!email || !password) {
        errEl.textContent = 'Please enter email and password';
        errEl.style.display = 'block';
        return;
    }
    try {
        const form = new URLSearchParams();
        form.append('username', email);
        form.append('password', password);
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: form
        });
        const data = await res.json();
        if (res.ok) {
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            userEmail = email;
            localStorage.setItem('pdis_token', accessToken);
            localStorage.setItem('pdis_refresh', refreshToken);
            localStorage.setItem('pdis_email', email);
            document.getElementById('sidebar-email').textContent = email;
            showPage('page-dashboard');
            loadStats();
            showToast('Welcome! 👋');
        } else {
            if (res.status === 403) {
                pendingVerificationEmail = email;
                localStorage.setItem('pdis_pending_verification_email', pendingVerificationEmail);
                const verifyInput = document.getElementById('verify-email');
                const verifyErr = document.getElementById('verify-error');
                if (verifyInput) verifyInput.value = pendingVerificationEmail;
                if (verifyErr) {
                    verifyErr.textContent = data.detail || 'Email not verified';
                    verifyErr.style.display = 'block';
                }
                showPage('page-verify-email');
                return;
            }
            errEl.textContent = data.detail || 'Login error';
            errEl.style.display = 'block';
        }
    } catch (error) {
        errEl.textContent = 'Unable to reach server';
        errEl.style.display = 'block';
    }
}

function doLogout() {
    accessToken = '';
    refreshToken = '';
    userEmail = '';
    localStorage.removeItem('pdis_token');
    localStorage.removeItem('pdis_refresh');
    localStorage.removeItem('pdis_email');
    showPage('page-login');
    showToast('Logged out');
}

async function loadStats() {
    try {
        const [usersRes, expensesRes] = await Promise.all([authFetch('/users/'), authFetch('/expenses/')]);
        if (!usersRes || !expensesRes) return;
        const users = await usersRes.json();
        const expenses = await expensesRes.json();
        document.getElementById('stat-users').textContent = Array.isArray(users) ? users.length : 0;
        document.getElementById('stat-expenses').textContent = Array.isArray(expenses) ? expenses.length : 0;
        const total = Array.isArray(expenses) ? expenses.reduce((sum, item) => sum + (Number(item.amount) || 0), 0) : 0;
        document.getElementById('stat-total').textContent = total.toLocaleString() + ' so\'m';
    } catch (error) {
        console.warn('Stats error', error);
    }
}

async function loadUsers() {
    const el = document.getElementById('users-list');
    el.innerHTML = '<div class="empty-state">Loading...</div>';
    try {
        const res = await authFetch('/users/');
        if (!res) return;
        const data = await res.json();
        if (!Array.isArray(data) || data.length === 0) {
            el.innerHTML = '<div class="empty-state"><div class="empty-icon">👥</div>No users yet</div>';
            return;
        }
        el.innerHTML = `<table class="data-table">
      <thead><tr><th>#</th><th>Name</th><th>Email</th><th>Action</th></tr></thead>
      <tbody>${data.map((user, index) => `<tr>
        <td class="num-cell">${index + 1}</td>
        <td>${user.name}</td>
        <td>${user.email}</td>
        <td><button class="btn-delete" onclick="deleteUser(${user.id})">🗑 Delete</button></td>
      </tr>`).join('')}</tbody></table>`;
    } catch (error) {
        el.innerHTML = '<div class="empty-state">Error loading users</div>';
    }
}

async function addUser() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    if (!name || !email) {
        showToast('Please enter name and email!', 'error');
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
            showToast('✅ User added!');
            document.getElementById('user-name').value = '';
            document.getElementById('user-email').value = '';
            loadUsers();
            loadStats();
        } else {
            showToast(data.detail || 'Error adding user', 'error');
        }
    } catch (error) {
        showToast('Error adding user', 'error');
    }
}

async function deleteUser(id) {
    if (!confirm('Delete this user?')) return;
    try {
        const res = await authFetch(`/users/${id}`, { method: 'DELETE' });
        if (!res) return;
        if (res.ok) {
            showToast('✅ User deleted');
            loadUsers();
            loadStats();
        } else {
            const data = await res.json();
            showToast(data.detail || 'Error deleting user', 'error');
        }
    } catch (error) {
        showToast('Error deleting user', 'error');
    }
}

async function loadExpenses() {
    const el = document.getElementById('expenses-list');
    el.innerHTML = '<div class="empty-state">Loading...</div>';
    try {
        const res = await authFetch('/expenses/');
        if (!res) return;
        const data = await res.json();
        const items = Array.isArray(data) ? data.filter(matchesExpenseFilter) : [];
        if (items.length === 0) {
            el.innerHTML = '<div class="empty-state"><div class="empty-icon">💸</div>No expenses yet</div>';
            return;
        }
        el.innerHTML = `<table class="data-table">
      <thead><tr><th>#</th><th>Category</th><th>Amount</th><th>Date</th><th>Action</th></tr></thead>
      <tbody>${items.map((expense, index) => `<tr>
        <td class="num-cell">${index + 1}</td>
        <td>${expense.category}</td>
        <td class="amount">${Number(expense.amount).toLocaleString()} so\'m</td>
        <td style="color:var(--muted);font-size:12px">${new Date(expense.created_at).toLocaleDateString()}</td>
        <td><button class="btn-delete" onclick="deleteExpense(${expense.id})">🗑 Delete</button></td>
      </tr>`).join('')}</tbody></table>`;
    } catch (error) {
        el.innerHTML = '<div class="empty-state">Error loading expenses</div>';
    }
}

async function addExpense() {
    const category = document.getElementById('exp-category').value.trim();
    const amount = parseFloat(document.getElementById('exp-amount').value);
    if (!category || !amount) {
        showToast('Please enter category and amount!', 'error');
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
            showToast('✅ Expense added!');
            document.getElementById('exp-category').value = '';
            document.getElementById('exp-amount').value = '';
            loadExpenses();
            loadStats();
        } else {
            showToast(data.detail || 'Error adding expense', 'error');
        }
    } catch (error) {
        showToast('Error adding expense', 'error');
    }
}

async function deleteExpense(id) {
    if (!confirm('Delete this expense?')) return;
    try {
        const res = await authFetch(`/expenses/${id}`, { method: 'DELETE' });
        if (!res) return;
        if (res.ok) {
            showToast('✅ Expense deleted');
            loadExpenses();
            loadStats();
        } else {
            const data = await res.json();
            showToast(data.detail || 'Error deleting expense', 'error');
        }
    } catch (error) {
        showToast('Error deleting expense', 'error');
    }
}

function setExpenseFilter(filter) {
    expenseFilter = filter;
    document.querySelectorAll('.filter-chip').forEach(chip => chip.classList.toggle('active', chip.id === `filter-${filter}`));
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
        const weekAgo = new Date(now);
        weekAgo.setDate(now.getDate() - 7);
        return created >= weekAgo;
    }
    if (expenseFilter === 'month') {
        return created.getFullYear() === now.getFullYear() && created.getMonth() === now.getMonth();
    }
    return true;
}

async function loadCategories() {
    try {
        const res = await authFetch('/expenses/categories/list');
        if (!res) return;
        const data = await res.json();
        const datalist = document.getElementById('category-list');
        if (!datalist || !Array.isArray(data)) return;
        datalist.innerHTML = data.map(category => `<option value="${category.name}">${category.emoji} ${category.description}</option>`).join('');
    } catch (error) {
        console.warn('Category load error', error);
    }
}

document.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
        if (document.getElementById('page-login').classList.contains('active')) doLogin();
        if (document.getElementById('page-register').classList.contains('active')) doRegister();
        if (document.getElementById('page-verify-email').classList.contains('active')) verifyEmailCode();
    }
    if (e.key === 'Escape') {
        closeSidebar();
    }
});

window.addEventListener('resize', () => {
    if (window.innerWidth > 900) {
        closeSidebar();
    }
});
