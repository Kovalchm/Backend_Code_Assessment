import bash
This project contains API tests for ReqRes API using Playwright and Python.

## 📋 Prerequisites
- Python 3.9+ installed
- pip package manager
## 🚀 Setup Instructions
### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Backend_Code_Assessment
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright
```bash
pip install playwright pytest-playwright
```

### 5. Install Playwright browsers
```bash
playwright install chromium
```

### 6. Configure API key
1. Go to https://app.reqres.in
2. Sign up and get your API key
3. Open `back/test/conftest.py`
4. Replace `"YOUR_API_KEY"` with your actual API key
```python
extra_http_headers={
    "x-api-key": "your_actual_api_key_here",
    ...
}
```

## ▶️ Run Tests
### Run all tests
```bash
pytest back/test/ -v
```

### Run specific test file
```bash
pytest back/test/test_api_reqres.py -v
```

### Run with output (see print statements)
```bash
pytest back/test/test_api_reqres.py -v -s
```

### Run specific test
```bash
pytest back/test/test_api_reqres.py::test_login_user -v
```

## 📊 Test Coverage
- ✅ GET `/api/users` - List users
- ✅ GET `/api/users/{id}` - Get single user
- ✅ POST `/api/users` - Create user
- ✅ PUT `/api/users/{id}` - Update user
- ✅ DELETE `/api/users/{id}` - Delete user
- ✅ POST `/api/login` - User authentication

## 📁 Project Structure
```
Backend_Code_Assessment/
├── back/
│   └── test/
│       ├── conftest.py          # Test configuration & fixtures
│       └── test_api_reqres.py   # API tests
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'playwright'`

**Solution:**
```bash
pip install playwright pytest-playwright
playwright install
```

### Issue: `403 Forbidden - invalid_api_key`

**Solution:** Make sure you've set your API key in `conftest.py`
