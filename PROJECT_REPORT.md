# 🚀 FinPulse: Unified Finance Management System
## Full Project Technical Report (A to Z)

---

## 🇺🇸 ENGLISH VERSION

### 1. Project Overview
**FinPulse** is a professional-grade, full-stack web application designed for comprehensive financial tracking. It allows users to manage multiple profiles (family or team members) under a single account, track expenses with categorical precision, and visualize financial health through real-time analytics.

### 2. Core Technology Stack
- **Backend**: Python (FastAPI) - High performance, asynchronous API framework.
- **Database**: PostgreSQL (via Supabase) - Relational database for structured data.
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript (ES6+) - Single Page Application (SPA).
- **Authentication**: JWT (JSON Web Tokens) with Secure Refresh Token logic.
- **Email Service**: Brevo HTTP API - For secure 2FA/Email verification.
- **Visuals**: Chart.js - For dynamic, animated financial charts.

### 3. Key Features & Implementation
#### A. Secure Authentication & Verification
- **Registration**: Implemented a multi-step registration process.
- **2FA Verification**: Integrated Brevo API to send unique 6-digit codes. Accounts are only activated upon successful verification.
- **Security**: Passwords are hashed using `bcrypt`. Timezone-aware expiration for verification codes.

#### B. Financial Management
- **Multi-User Profiles**: Users can add sub-profiles (e.g., family members) to track individual spending within one account.
- **Expense Tracking**: Logic to add, delete, and categorize expenses (Food, Transport, Rent, etc.) with automatic emoji integration.
- **Anonymized Data**: Expenses are linked to sub-profiles but managed by the main account holder.

#### C. Analytics & Reporting
- **Real-time Metrics**: Instant calculation of total spending and monthly averages.
- **Visual Charts**: Implemented Pie charts for category distribution and Bar/Line charts for spending trends.
- **CSV Export**: Ability to download financial data as Excel-compatible CSV files.

#### D. Admin Command Center (Restricted Access)
- **Platform Stats**: A real-time dashboard for the administrator (Oybek) to monitor total registered accounts.
- **Global Analytics**: High-level platform metrics showing total money flow and trending categories across all verified users.
- **Timezone Sync**: Database queries adjusted to `Asia/Tashkent` (UTC+5) for accurate reporting in Uzbekistan.
- **Session Security**: Admin access is protected by a secondary "Admin Key" stored in `sessionStorage` (cleared when browser closes).

### 4. Implementation Steps (Chronology)
1. **Init**: Set up FastAPI structure and PostgreSQL connection.
2. **Auth**: Built JWT login and Email verification system.
3. **Core**: Developed expense and user management endpoints.
4. **UI**: Created a sleek, dark-themed SPA with glassmorphism effects.
5. **Stats**: Integrated Chart.js for data visualization.
6. **Admin**: Built the Restricted Access command center with live polling.
7. **Refine**: Fixed timezone offsets, reset database sequences, and enhanced security UI.

---

## 🇺🇿 O'ZBEKCHA VERSIYA

### 1. Loyiha haqida qisqacha
**FinPulse** — bu to'liq funksional, professional darajadagi moliyaviy hisob-kitob tizimi. U foydalanuvchilarga bitta akkaunt ichida bir nechta profilni (oila a'zolari yoki jamoa) boshqarish, xarajatlarni kategoriyalar bo'yicha kuzatish va real vaqt rejimida grafiklar orqali tahlil qilish imkonini beradi.

### 2. Texnologiyalar to'plami
- **Backend**: Python (FastAPI) - Yuqori tezlikdagi asinxron API.
- **Ma'lumotlar bazasi**: PostgreSQL (Supabase orqali) - Ishonchli relyatsion baza.
- **Frontend**: Vanilla HTML5, CSS3 va JavaScript (SPA) - Sahifani yangilamasdan ishlovchi interfeys.
- **Autentifikatsiya**: JWT (JSON Web Tokens) va xavfsiz Refresh Token tizimi.
- **Email Xizmati**: Brevo API - 2FA tasdiqlash kodlarini yuborish uchun.
- **Grafiklar**: Chart.js - Dinamik va chiroyli diagrammalar uchun.

### 3. Asosiy imkoniyatlar va amalga oshirish
#### A. Xavfsiz Autentifikatsiya
- **Ro'yxatdan o'tish**: Ism, email va parol orqali ko'p bosqichli tizim.
- **Email Tasdiqlash**: Brevo API orqali 6 xonali kod yuborish. Faqat kodi tasdiqlangan foydalanuvchilargina tizimga kira oladi.
- **Xavfsizlik**: Parollar `bcrypt` bilan shifrlangan. Tasdiqlash kodlari uchun amal qilish muddati belgilangan.

#### B. Moliyaviy Boshqaruv
- **Ko'p foydalanuvchili tizim**: Bitta hisob egasi o'z oilasi yoki jamoasi uchun alohida profillar qo'shishi mumkin.
- **Xarajatlar nazorati**: Har bir xarajat uchun kategoriya (Oziq-ovqat, Transport va h.k.), summa va sana belgilash imkoniyati.
- **Kategoriyalar**: Emojilar bilan boyitilgan tayyor kategoriyalar tizimi.

#### C. Analitika va Hisobotlar
- **Real-vaqt ko'rsatkichlari**: Jami xarajatlar va oylik o'rtacha summalarni oniy hisoblash.
- **Diagrammalar**: Xarajatlar taqsimoti (Pie chart) va kunlik/haftalik trendlar (Bar chart).
- **Eksport**: Barcha ma'lumotlarni Excel'ga mos CSV formatida yuklab olish.

#### D. Admin Boshqaruv Markazi (Maxfiy Bo'lim)
- **Platform Stats**: Administrator (Oybek) uchun foydalanuvchilarni real vaqtda kuzatish paneli.
- **Global Analitika**: Butun platforma bo'yicha anonim moliyaviy oqim va trendlarni kuzatish.
- **Vaqtni sozlash**: Uzbekistan vaqti (`Asia/Tashkent` UTC+5) bilan to'liq sinxronizatsiya.
- **Kirish nazorati**: Maxsus "Admin Key" orqali himoyalangan, faqat sessiya vaqtida ishlovchi kirish tizimi.

### 4. Amalga oshirilgan ishlar tartibi
1. **Boshlanish**: FastAPI strukturasi va PostgreSQL bazasi sozlandi.
2. **Autentifikatsiya**: JWT login va Email tasdiqlash tizimi qurildi.
3. **Yadro**: Xarajatlar va foydalanuvchilarni boshqarish API'lari yaratildi.
4. **Dizayn**: Dark-theme (to'q rangli), glassmorphism effektli zamonaviy UI yaratildi.
5. **Analitika**: Chart.js grafiklari integratsiya qilindi.
6. **Admin bo'limi**: Maxfiy "Restricted Access" boshqaruv markazi va avtomatik yangilanish tizimi qo'shildi.
7. **Sozlash**: Vaqt farqlari to'g'rilandi, baza IDlari reset qilindi va xavfsizlik kuchaytirildi.
