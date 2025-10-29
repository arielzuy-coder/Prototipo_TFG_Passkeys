from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Optional
import logging
import secrets
import random
from pydantic import BaseModel
import user_agents

from config import settings
from models import Base, User, Passkey, Device, Session as DBSession, AuditEvent, Policy, RiskEvaluation
from auth.webauthn_handler import WebAuthnHandler
from auth.token_manager import TokenManager
from auth.session_manager import SessionManager
from risk.risk_engine import RiskEngine
from risk.policies import PolicyEngine

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear FastAPI app
app = FastAPI(
    title="Prototipo Autenticación Passkeys + Zero Trust",
    description="Sistema de autenticación passwordless con evaluación de riesgo contextual",
    version="1.0.0"
)

# CORS - Configuración para desarrollo y producción
import os
allowed_origins = [
    settings.ORIGIN,
    "http://localhost:3000",
    "https://localhost:3000",
]

# En producción, agregar dominios de Render
if "onrender.com" in settings.ORIGIN:
    # Permitir todas las URLs de Render del proyecto
    allowed_origins.extend([
        "https://auth-frontend.onrender.com",
        "https://auth-frontend-*.onrender.com",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.onrender\.com",  # Permitir cualquier subdominio de Render
)

# Database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency para obtener DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar componentes
webauthn_handler = WebAuthnHandler()
token_manager = TokenManager()
session_manager = SessionManager()
risk_engine = RiskEngine()
policy_engine = PolicyEngine()

# Almacenamiento temporal para step-up (en producción usar Redis)
stepup_tokens = {}  # {token: {user_id, email, expires_at, session_data, otp}}

# ============================================
# MODELOS PYDANTIC PARA REQUEST BODIES
# ============================================

class RegisterBeginRequest(BaseModel):
    email: str

class RegisterCompleteRequest(BaseModel):
    email: str
    credential: dict
    device_name: Optional[str] = None

class LoginBeginRequest(BaseModel):
    email: str

class LoginCompleteRequest(BaseModel):
    email: str
    credential: dict

class LoginFailedRequest(BaseModel):
    email: str
    reason: str
    error_message: Optional[str] = None

class StepUpVerifyRequest(BaseModel):
    stepup_token: str
    verification_type: str  # 'biometric', 'otp', 'pin'
    verification_data: Optional[dict] = None

class PolicyCreateRequest(BaseModel):
    name: str
    description: str
    conditions: dict
    action: str  # 'allow', 'stepup', 'deny'
    priority: int
    enabled: bool = True

class PolicyUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[dict] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None

# ============================================
# ENDPOINTS DE SALUD Y INFO
# ============================================

@app.get("/")
async def root():
    return {
        "message": "Prototipo Autenticación Passkeys + Zero Trust",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )

# ============================================
# ENDPOINTS DE REGISTRO (ENROLAMIENTO)
# ============================================

@app.post("/auth/register/begin")
async def register_begin(
    request: Request,
    data: RegisterBeginRequest,
    db: Session = Depends(get_db)
):
    """Inicia el proceso de enrolamiento de Passkeys."""
    try:
        email = data.email
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(email=email, display_name=email.split('@')[0])
            db.add(user)
            db.commit()
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Optional
import logging
import secrets
import random
from pydantic import BaseModel
import user_agents

from config import settings
from models import Base, User, Passkey, Device, Session as DBSession, AuditEvent, Policy, RiskEvaluation
from auth.webauthn_handler import WebAuthnHandler
from auth.token_manager import TokenManager
from auth.session_manager import SessionManager
from risk.risk_engine import RiskEngine
from risk.policies import PolicyEngine

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear FastAPI app
app = FastAPI(
    title="Prototipo Autenticación Passkeys + Zero Trust",
    description="Sistema de autenticación passwordless con evaluación de riesgo contextual",
    version="1.0.0"
)

# CORS - Configuración para desarrollo y producción
import os
allowed_origins = [
    settings.ORIGIN,
    "http://localhost:3000",
    "https://localhost:3000",
]

# En producción, agregar dominios de Render
if "onrender.com" in settings.ORIGIN:
    # Permitir todas las URLs de Render del proyecto
    allowed_origins.extend([
        "https://auth-frontend.onrender.com",
        "https://auth-frontend-*.onrender.com",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.onrender\.com",  # Permitir cualquier subdominio de Render
)

# Database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency para obtener DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar componentes
webauthn_handler = WebAuthnHandler()
token_manager = TokenManager()
session_manager = SessionManager()
risk_engine = RiskEngine()
policy_engine = PolicyEngine()

# Almacenamiento temporal para step-up (en producción usar Redis)
stepup_tokens = {}  # {token: {user_id, email, expires_at, session_data, otp}}

# ============================================
# MODELOS PYDANTIC PARA REQUEST BODIES
# ============================================

class RegisterBeginRequest(BaseModel):
    email: str

class RegisterCompleteRequest(BaseModel):
    email: str
    credential: dict
    device_name: Optional[str] = None

class LoginBeginRequest(BaseModel):

