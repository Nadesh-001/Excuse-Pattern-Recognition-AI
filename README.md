# 🤖 Excuse Pattern Recognition AI

**AI-Powered Task Management & Delay Analysis System**

This application helps organizations manage tasks efficiently while using **AI (Groq)** to analyze delay reasons. It identifies patterns, authenticity, and avoidance strategies in employee excuses, promoting accountability and transparency.

## 🚀 Features

### 🧠 Intelligent AI Analysis (Groq)
- **Real-time Excuse Verification**: Uses `openai/gpt-oss-20b` (Groq) to score authenticity (0-100%).
- **Pattern Detection**: Identifies recurring categories (Health, Personal, Technical) and risk levels.
- **Voice Input**: Supports audio transcription for verbal delay explanations.

### 📝 Advanced Task Management
- **Smart Attachments**: Analyzing content of attached PDF/DOCX files and URLs.
- **⏱️ Timer System**: Track "Estimated vs Elapsed" time with real-time status badges (On-Track/Overtime).
- **Role-Based Access**: Specialized Dashboards for **Employees**, **Managers**, and **Admins**.

### 📊 Comprehensive Analytics
- **Team Insights**: Manager visuals for team performance and high-risk employees.
- **Visual Reports**:
    - 📈 Delay Frequency Trends
    - 🥧 Risk Distribution Pie Charts
    - 📊 Category Breakdown Bar Charts

### 🎨 Premium UI/UX
- **Glassmorphism Design**: Modern, clean aesthetics with dark mode support.
- **Custom Icons**: Integrated SVG icons for a professional look.
- **Responsive Layout**: Optimized for all screen sizes.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend Language**: Python 3.8+
- **Database**: MySQL / TiDB Cloud (Secure TLS Connection)
- **AI Engine**: [Groq API](https://groq.com/)

---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Nadesh-001/Excuse-Pattern-Recognition-AI.git
   cd Excuse-Pattern-Recognition-AI
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets (.env)**
   Create a `.env` file in the root directory:
   ```env
   # Database
   DB_HOST=your_tidb_host
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_NAME=test
   DB_PORT=4000

   # AI Keys
   GROQ_API_KEY=gsk_...
   ```

4. **Run the Application**
   ```bash
   python -m streamlit run app.py
   ```

---

## 📚 Documentation

For detailed usage instructions, please refer to the **[User Manual](USER_MANUAL.md)**.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

*Built for Final Year Project 2026.*
