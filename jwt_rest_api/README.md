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
