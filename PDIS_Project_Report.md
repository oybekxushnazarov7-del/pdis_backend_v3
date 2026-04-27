# Project Report: Personal Data Intelligence System (PDIS)

## 1. Project Overview & Real-Life Applications
PDIS is a modern web application designed for personal data management and expense tracking. Beyond its technical structure, it serves several practical purposes in daily life:

*   **Personal Budgeting**: Individuals can track their daily spending across categories like food, transport, and utilities to stay within their monthly budget.
*   **Small Business Accounting**: Small business owners or freelancers can monitor their operational expenses and business-related costs in a centralized system.
*   **Student Financial Planning**: Students can manage their limited allowance by tracking where their money goes, helping them save for educational goals.
*   **Family Shared Expenses**: Families can use the system to monitor collective household spending, ensuring transparency and better financial coordination.
*   **Investment Tracking**: Users can categorize surplus funds or savings to analyze their financial growth over time and plan future investments.

## 2. Key Achievements & Technical Solutions

### A. Advanced Authentication System
- **Custom JWT Implementation**: Developed a secure authentication system using JSON Web Tokens (JWT) for session management.
- **Refresh Token Logic**: Implemented a dual-token system (Access + Refresh). This allows users to stay logged in securely without re-entering credentials frequently.
- **Simplified Auth Flow**: Removed heavy OAuth2 dependencies to create a lightweight, "Simple Auth" system that uses standard JSON for login, making it faster and easier to maintain.
- **Manual Header Extraction**: Implemented manual Bearer token extraction from HTTP headers, ensuring the system is independent of third-party security helpers.

### B. Backend Architecture (FastAPI)
- **Database Resilience**: Configured a dynamic database connection system that prioritizes environment variables (`DATABASE_URL`) with fallback support.
- **Automated Data Seeding**: Added a lifespan management system that automatically populates the database with default expense categories (Food, Transport, etc.) upon startup.
- **CORS Optimization**: Properly configured Cross-Origin Resource Sharing (CORS) to ensure the frontend can securely communicate with the backend on cloud platforms like Render.

### C. Frontend Enhancements (Modern UI/UX)
- **Dynamic Category Management**: Replaced static inputs with a dynamic dropdown that fetches available categories directly from the backend API.
- **Robust Error Handling**: Fixed the infamous `[object Object]` error by implementing a robust error-stringification logic that displays readable messages to the user.
- **Automated Fetching**: Developed an `authFetch` wrapper that automatically handles token expiration and background refreshing.

### D. Security & DevOps
- **Git Hygiene**: Cleaned up the repository by removing sensitive files (`.env`, `venv`, `.db`) and updating `.gitignore` to protect credentials.
- **Production Readiness**: Optimized the application for deployment on **Render**, ensuring all paths and API URLs are auto-detected.

---

# Loyiha Hisoboti: Shaxsiy Ma'lumotlarni Boshqarish Tizimi (PDIS)

## 1. Loyiha haqida va Hayotiy qo'llanilishi
PDIS — bu shaxsiy ma'lumotlar va xarajatlarni kuzatish uchun mo'ljallangan zamonaviy veb-ilova. Texnik jihatdan tashqari, u hayotda quyidagi amaliy maqsadlarda xizmat qiladi:

*   **Shaxsiy Budjetni Boshqarish**: Foydalanuvchilar oziq-ovqat, transport va kommunal to'lovlar kabi toifalar bo'yicha kundalik xarajatlarini kuzatib, oylik budjetdan chiqib ketmaslikni nazorat qiladi.
*   **Kichik Biznes Buxgalteriyasi**: Tadbirkorlar yoki frilanserlar o'zlarining operatsion xarajatlarini va biznes bilan bog'liq xarajatlarini markazlashgan tizimda kuzatib borishlari mumkin.
*   **Talabalar Moliyaviy Rejalashtirishi**: Talabalar o'z stipendiyalarini to'g'ri taqsimlash va pul qayerga ketayotganini tahlil qilish orqali jamg'arma qilishni o'rganadilar.
*   **Oila Xarajatlari Nazorati**: Oilalar ro'zg'or uchun qilinayotgan umumiy xarajatlarni birgalikda kuzatib borishlari va moliyaviy shaffoflikni ta'minlashlari mumkin.
*   **Investitsiya Tahlili**: Foydalanuvchilar ortiqcha mablag'larini yoki jamg'armalarini toifalarga ajratib, vaqt o'tishi bilan moliyaviy o'sishni tahlil qilishlari mumkin.

## 2. Asosiy natijalar va texnik yechimlar

### A. Murakkab Autentifikatsiya Tizimi
- **JWT Implementatsiyasi**: Sessiyalarni boshqarish uchun JSON Web Token (JWT) texnologiyasiga asoslangan xavfsiz tizim yaratildi.
- **Refresh Token Logikasi**: Ikki bosqichli token tizimi (Access + Refresh) joriy etildi. Bu foydalanuvchiga har safar parol kiritmasdan, tizimda uzoq vaqt xavfsiz qolish imkonini beradi.
- **Soddalashtirilgan Auth**: Murakkab OAuth2 kutubxonalaridan voz kechilib, "Oddiy Auth" (JSON login) tizimi qurildi. Bu tizimni tezroq va tushunarliroq qiladi.
- **Sarlavhalarni qo'lda o'qish**: HTTP sarlavhalaridan Bearer token-larni qo'lda o'qiydigan mantiq yozildi, bu tizimning mustaqilligini ta'minlaydi.

### B. Backend Arxitekturasi (FastAPI)
- **Ma'lumotlar Bazasi Moslashuvchanligi**: Muhit o'zgaruvchilari orqali ishlaydigan dinamik ulanish tizimi sozlandi.
- **Avtomatik Ma'lumot To'ldirish**: Tizim ishga tushganda bazani standart xarajat kategoriyalari (Oziq-ovqat, Transport va h.k.) bilan avtomatik to'ldirish logikasi qo'shildi.
- **CORS Sozlamalari**: Render kabi platformalarda frontend va backend o'rtasida xavfsiz aloqa o'rnatish uchun CORS parametrlari to'g'ri sozlandi.

### C. Frontend Imkoniyatlari (Zamonaviy UI/UX)
- **Dinamik Kategoriyalar**: Statik kiritish maydonlari o'rniga, bazadan kategoriyalarni avtomatik yuklab oladigan dropdown (tanlov ro'yxati) yaratildi.
- **Xatoliklarni boshqarish**: `[object Object]` xatoligini bartaraf etish uchun barcha backend xabarlarini foydalanuvchiga tushunarli matn holatiga keltiruvchi logika yozildi.
- **Avtomatlashtirilgan So'rovlar**: Token muddati tugaganda uni fonda yangilab, so'rovni qaytadan yuboradigan `authFetch` funksiyasi yaratildi.

### D. Xavfsizlik va DevOps
- **Git Tozaligi**: Maxfiy fayllar (`.env`, `venv`, `.db`) GitHub-dan o'chirildi va xavfsizlikni ta'minlash uchun `.gitignore` yangilandi.
- **Deploymentga tayyorgarlik**: Ilova **Render** platformasida ishlash uchun to'liq optimizatsiya qilindi, barcha API manzillari avtomatik aniqlanadigan holatga keltirildi.
