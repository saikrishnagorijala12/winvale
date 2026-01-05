from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Winvale MOCK API's",
    description="Pure mock Swagger UI – no database, no logic",
    version="0.0.1"
)

# ---------------- HEALTH ----------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- AUTH / USERS ----------------
@app.post("/users")
def create_user():
    return {
        "user_id": 1,
        "name": "Demo User",
        "email": "demo@test.com",
        "role_id": 1,
        "created_time": datetime.utcnow()
    }

@app.get("/users")
def list_users():
    return [{"user_id": 1, "name": "Demo User"}]

# ---------------- ROLES ----------------
@app.get("/roles")
def list_roles():
    return [
        {"role_id": 1, "role_name": "ADMIN"},
        {"role_id": 2, "role_name": "USER"}
    ]

# ---------------- VENDORS ----------------
@app.post("/vendors")
def create_vendor():
    return {"vendor_id": 101, "company_name": "ACME Corp"}

@app.get("/vendors")
def list_vendors():
    return [{"vendor_id": 101, "company_name": "ACME Corp"}]

# ---------------- CLIENT PROFILE ----------------
@app.post("/client-profiles")
def create_client_profile():
    return {
        "vendor_profile_id": 5001,
        "contract_number": "GSA-001",
        "created_time": datetime.utcnow()
    }

@app.get("/client-profiles/{vendor_id}")
def get_client_profile(vendor_id: int):
    return {
        "vendor_id": vendor_id,
        "contract_number": "GSA-001"
    }

# ---------------- PRODUCTS ----------------
@app.post("/products")
def create_product():
    return {"product_id": 9001, "item_name": "Laptop"}

@app.get("/products")
def list_products():
    return [{"product_id": 9001, "item_name": "Laptop"}]

# ---------------- PRODUCT DIMENSIONS ----------------
@app.get("/product-dimensions/{product_id}")
def get_product_dimensions(product_id: int):
    return {
        "product_id": product_id,
        "length": 10,
        "width": 5,
        "height": 2
    }

# ---------------- PRODUCT HISTORY ----------------
@app.get("/product-history/{product_id}")
def get_product_history(product_id: int):
    return [
        {"version": 1, "is_current": False},
        {"version": 2, "is_current": True}
    ]

# ---------------- CPL UPLOAD ----------------
@app.post("/cpl/upload")
def upload_cpl():
    return {
        "job_id": 3001,
        "status": "PROCESSING"
    }

# ---------------- JOBS ----------------
@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    return {
        "job_id": job_id,
        "status": "COMPLETED"
    }

# ---------------- MODIFICATION ACTIONS ----------------
@app.get("/actions/job/{job_id}")
def get_actions(job_id: int):
    return [
        {"action_type": "PRICE_UPDATE", "count": 25}
    ]

# ---------------- FILE UPLOADS ----------------
@app.post("/file-uploads")
def upload_file():
    return {
        "upload_id": 7001,
        "filename": "cpl.xlsx"
    }

# ---------------- TEMPLATES ----------------
@app.get("/templates")
def list_templates():
    return [
        {"template_id": 1, "name": "GSA Contract"},
        {"template_id": 2, "name": "Cover Page"}
    ]
