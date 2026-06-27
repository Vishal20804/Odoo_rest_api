# JWT REST API Module for Odoo 18
**Module Technical Name:** `jwt_rest_api`  
**Author:** Vishal Sharma  
**Version:** 18.0.1.0.0

---

## 📦 Module Structure

```
jwt_rest_api/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── jwt_utils.py        ← Core JWT logic + Secret Key management
│   └── jwt_token.py        ← DB model for storing tokens
├── controllers/
│   ├── __init__.py
│   ├── base_controller.py  ← Shared helpers (verify token, response format)
│   ├── auth_controller.py  ← Login, Signup, Refresh, Logout, Me
│   └── crud_controller.py  ← Protected CRUD on res.partner
├── views/
│   ├── jwt_token_views.xml ← List, Form, Search views in Odoo backend
│   └── jwt_menu.xml        ← Top-level menu "JWT REST API"
├── security/
│   └── ir.model.access.csv
└── data/
    └── jwt_secret_data.xml ← Secret key initial record
```

---

## 🔑 Secret Key — Kaise Generate Hoti Hai?

1. Module install hote hi `data/jwt_secret_data.xml` ek **placeholder** value store karta hai
2. Pehli login/signup call pe `jwt.utils.get_or_create_secret_key()` call hota hai
3. Yeh method placeholder detect karta hai → **256-bit random hex key** generate karta hai
4. Key `ir.config_parameter` me key `jwt_rest_api.secret_key` pe store hoti hai
5. Settings → Technical → System Parameters me jaake dekh sakte ho

> ⚠️ Key rotate karne ke liye: `self.env['jwt.utils'].rotate_secret_key()` call karo  
> (Sab purane tokens invalid ho jayenge)

---

## 🌐 API Endpoints

### Base URL: `http://localhost:8069`

| Method | Endpoint                     | Auth Required | Description          |
|--------|------------------------------|---------------|----------------------|
| POST   | /api/v1/auth/signup          | ❌ None       | New user register    |
| POST   | /api/v1/auth/login           | ❌ None       | Login + get tokens   |
| POST   | /api/v1/auth/refresh         | ❌ None       | New access token lo  |
| POST   | /api/v1/auth/logout          | ✅ Bearer     | Token revoke karo    |
| GET    | /api/v1/auth/me              | ✅ Bearer     | Apni profile dekho   |
| GET    | /api/v1/partners             | ✅ Bearer     | Partners list        |
| GET    | /api/v1/partners/<id>        | ✅ Bearer     | Single partner       |
| POST   | /api/v1/partners             | ✅ Bearer     | Partner create       |
| PUT    | /api/v1/partners/<id>        | ✅ Bearer     | Partner update       |
| DELETE | /api/v1/partners/<id>        | ✅ Bearer     | Partner delete       |

---

## 📋 Postman Examples

### 1. Signup
```
POST /api/v1/auth/signup
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "name": "Vishal Sharma",
    "login": "vishal@test.com",
    "password": "Test@1234"
  }
}
```

### 2. Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "login": "vishal@test.com",
    "password": "Test@1234"
  }
}
```
**Response:**
```json
{
  "result": {
    "status": "success",
    "code": 200,
    "data": {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "token_type": "Bearer",
      "expires_in": 900
    }
  }
}
```

### 3. Protected Route (Partners List)
```
GET /api/v1/partners
Authorization: Bearer <access_token>
Content-Type: application/json

{"jsonrpc":"2.0","method":"call","params":{}}
```

### 4. Refresh Token
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "refresh_token": "eyJ..."
  }
}
```

---

## 🔒 Token Flow (Complete)

```
Client                          Odoo Server
  |                                  |
  |-- POST /signup or /login ------> |
  |                         [verify credentials]
  |                         [generate access_token  (15 min)]
  |                         [generate refresh_token (7 days)]
  |                         [store both in jwt.token table]
  |<-- access_token + refresh_token--|
  |                                  |
  |-- GET /partners                  |
  |   Authorization: Bearer <AT> --> |
  |                         [extract token from header]
  |                         [verify signature with secret key]
  |                         [check expiry]
  |                         [check DB: not revoked?]
  |<-- 200 OK + partners data -------|
  |                                  |
  |  ... 15 min baad ...             |
  |                                  |
  |-- GET /partners                  |
  |   Authorization: Bearer <AT> --> |
  |                         [verify → EXPIRED!]
  |<-- 401 "Token has expired" ------|
  |                                  |
  |-- POST /refresh                  |
  |   { refresh_token: <RT> } -----> |
  |                         [verify refresh token signature]
  |                         [check DB: not revoked?]
  |                         [generate NEW access_token]
  |                         [update DB]
  |<-- new access_token -------------|
  |                                  |
  |-- POST /logout                   |
  |   Authorization: Bearer <AT> --> |
  |                         [is_revoked = True in DB]
  |<-- 200 "Logout successful" ------|
```

---

## 🗄️ Database Model (jwt.token)

| Field                | Type     | Description                    |
|---------------------|----------|--------------------------------|
| user_id             | Many2one | Linked Odoo user               |
| access_token        | Text     | Current access token           |
| refresh_token       | Text     | Current refresh token          |
| access_expires_at   | Datetime | Access token expiry            |
| refresh_expires_at  | Datetime | Refresh token expiry           |
| is_revoked          | Boolean  | Logout/revoke flag             |
| last_used           | Datetime | Last API call timestamp        |
| ip_address          | Char     | Client IP                      |
| user_agent          | Char     | Browser/Client info            |

---

## 🏗️ JWT Token Structure (Manual HS256)

```
Header  : {"alg":"HS256","typ":"JWT"}
Payload : {"sub":1,"login":"admin","type":"access","iat":1234,"exp":5678}
Signature: HMAC-SHA256(base64url(header)+"."+base64url(payload), secret_key)

Final Token: base64url(header).base64url(payload).base64url(signature)
```

> **Note:** Yeh module koi external library (PyJWT etc.) use nahi karta.  
> Pure Python `hmac` + `hashlib` + `base64` se JWT manually banate hain.

---

## 🖥️ Odoo Backend Menu

**JWT REST API** (Top menu, sirf Admins ke liye)
- Token Management → All Tokens (list/form view)
- Configuration → System Parameters (secret key yahan)
