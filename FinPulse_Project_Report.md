# Project Report: FinPulse — Unified Finance Management

## 1. Project Overview & Real-Life Applications
FinPulse is a premium web application designed for family and team financial coordination. It moves beyond simple personal tracking by providing a unified workspace where multiple users can manage shared expenses while maintaining individual accountability.

*   **Family Budgeting (Shared Context)**: Families can add multiple members (Dad, Mom, Kids) and track who is spending on what, ensuring total financial transparency.
*   **Team & Small Business Accounting**: Small teams or startups can track operational costs by assigning expenses to specific employees, simplifying month-end reconciliations.
*   **Unified Reporting**: The system aggregates data from all members into a single, comprehensive dashboard for big-picture financial analysis.
*   **Personal Financial Discipline**: Users can switch between personal and shared contexts to manage different aspects of their financial life within one app.

## 2. Key Achievements & Technical Solutions

### A. Multi-User Context System (NEW)
- **Shared Account Architecture**: Developed a system where multiple sub-users (profiles) exist under one primary account.
- **Dynamic Context Switching**: Implemented frontend logic to "switch" between users, allowing the entire dashboard to filter data based on the active member.
- **Relational Data Mapping**: Modified the database schema to link expenses to specific `user_id`s while maintaining the overarching `account_id` relationship.

### B. Advanced Analytics & Reporting (NEW)
- **Unified Summary Reports**: Created a dedicated Reporting section that aggregates spending across all users in real-time.
- **Comparative Data Visualization**: Integrated Chart.js to provide bar charts that compare spending habits between different family/team members.
- **User-Specific Trends**: Individual analytics allow users to see their personal category breakdowns separate from the group.

### C. Secure Authentication System
- **Custom JWT Implementation**: A secure session management system using JSON Web Tokens (JWT).
- **Refresh Token Logic**: A dual-token system (Access + Refresh) that keeps users logged in securely for extended periods.
- **Faxriddin-Compliant Simple Auth**: Removed heavy OAuth2 dependencies in favor of a lightweight, standard-compliant JWT system as requested.

### D. Frontend & Backend Synergy
- **Automated Data Seeding**: System automatically populates localized expense categories (Food, Transport, etc.) on startup.
- **Robust `authFetch` Wrapper**: A custom frontend utility that handles token expiration, background refreshing, and error handling seamlessly.
- **Production-Ready Deployment**: Fully optimized for **Render**, with dynamic path detection and secure environment variable management.

---

# Loyiha Hisoboti: FinPulse — Moliyaviy Boshqaruv Tizimi

## 1. Loyiha haqida va Hayotiy qo'llanilishi
FinPulse — bu oila va jamoalar uchun mo'ljallangan premium moliyaviy boshqaruv platformasi. U oddiy shaxsiy hisob-kitobdan yuqoriroq chiqib, jamoaviy xarajatlarni markazlashgan va shaffof holda boshqarish imkonini beradi.

*   **Oila Budjetini Boshqarish**: Oila a'zolarini (Dada, Oyi, Bolalar) tizimga qo'shib, kim qancha ishlatayotganini aniq kuzatish mumkin.
*   **Kichik Biznes va Jamoalar**: Startaplar yoki kichik jamoalar operatsion xarajatlarni xodimlarga biriktirgan holda hisoblab borishlari mumkin.
*   **Yagona Hisobot Tizimi**: Barcha a'zolarning xarajatlari bitta umumiy dashboard-da yig'ilib, moliyaviy holatni to'liq tahlil qilish imkonini beradi.
*   **Intizom va Shaffoflik**: Foydalanuvchilar o'z shaxsiy va umumiy xarajatlarini bitta ilovada ajratilgan holda boshqarishlari mumkin.

## 2. Texnik yechimlar va erishilgan natijalar

### A. Multi-User Kontekst Tizimi (YANGI)
- **Umumiy Akkaunt Arxitekturasi**: Bitta asosiy akkaunt doirasida bir nechta sub-foydalanuvchilar (profillar) yaratish tizimi ishlab chiqildi.
- **Dinamik Kontekstni O'zgartirish**: Foydalanuvchilar orasida bir marta bosish bilan almashish va butun dashboard ma'lumotlarini tanlangan shaxsga moslab filtrlar orqali ko'rish imkoniyati yaratildi.
- **Ma'lumotlar Bog'liqligi**: Bazadagi xarajatlar endi ham akkauntga (`account_id`), ham foydalanuvchiga (`user_id`) bog'liq holda saqlanadi.

### B. Kengaytirilgan Analitika va Hisobotlar (YANGI)
- **Markazlashgan Hisobotlar**: Barcha foydalanuvchilarning umumiy sarf-xarajatlarini real vaqt rejimida jamlaydigan yangi "Report" bo'limi qo'shildi.
- **Vizual Solishtirish**: Chart.js yordamida oila/jamoa a'zolarining xarajatlarini o'zaro solishtiruvchi bar-chartlar yaratildi.
- **Shaxsiy va Umumiy Tahlil**: Har bir a'zo o'zining shaxsiy toifalar bo'yicha tahlillarini guruhdan ajratilgan holda ko'rishi mumkin.

### C. Autentifikatsiya Tizimi
- **JWT Implementatsiyasi**: Xavfsiz sessiyalar uchun JSON Web Token texnologiyasidan foydalanildi.
- **Refresh Token Logikasi**: Foydalanuvchini har safar parol kiritishdan xalos qiluvchi Access + Refresh token tizimi joriy etildi.
- **Soddalashtirilgan Auth**: Faxriddin aka aytganlaridek, OAuth2 dan voz kechilib, standart va tez ishlovchi "Simple JWT Auth" tizimi qurildi.

### D. Frontend va Backend Hamkorligi
- **Avtomatik Ma'lumot To'ldirish**: Tizim ilk bor ishga tushganda bazani mahalliylashtirilgan xarajat toifalari bilan to'ldiradi.
- **`authFetch` Funksiyasi**: Tokenlarni fonda yangilaydigan va xatolarni tushunarli tilda ko'rsatadigan frontend utility yaratildi.
- **Render Optimizatsiyasi**: Loyiha Render platformasida muammosiz ishlashi uchun barcha URL va muhit sozlamalari to'liq sozlangan.
