# TrustGate 🚀

TrustGate is a centralized authentication server built with **FastAPI**, featuring **SSO, RBAC, rate limiting, and Vault as the backend**.

## Features
- ✅ Secure authentication and authorization
- 🔐 Single Sign-On (SSO)
- 🎭 Role-Based Access Control (RBAC)
- 📈 Rate limiting for API protection
- 🏦 HashiCorp Vault for secure secret storage

## Installation

### 1️⃣ Prerequisites
- Python 3.10+
- Poetry
- Docker & Docker Compose

### 2️⃣ Clone the Repository
```sh
git clone https://github.com/KarthikUdyawar/trustgate.git
cd trustgate
```

### 3️⃣ Install Dependencies
```sh
poetry install
```

### 4️⃣ Set Up Environment Variables
```sh
cp .env.example .env
```
Modify `.env` as needed.

### 5️⃣ Run the Application
```sh
poetry run uvicorn src.main:app --reload
```

### 6️⃣ Run Tests
```sh
pytest
```

## 📜 Contribution Guidelines
See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License
TrustGate is licensed under the [MIT License](LICENSE).
