# 🔐 Prototipo de Autenticación Passwordless con Evaluación de Riesgo Zero Trust

## 📋 Información del Proyecto

**Trabajo Final de Grado (TFG)**  
**Universidad:** Universidad Siglo 21  
**Carrera:** Licenciatura en Seguridad Informática  
**Alumno:** Zuy, Ariel Hernán  
**Legajo:** VLSI002384  
**Año:** 2025

---

## 🎯 Descripción

Sistema de autenticación sin contraseñas (passwordless) basado en el estándar FIDO2/WebAuthn, integrado con un motor de evaluación de riesgo continuo bajo el paradigma Zero Trust. El sistema implementa autenticación adaptativa (step-up) según el nivel de riesgo detectado y proporciona un panel de administración para gestionar políticas de seguridad.

### **Características Principales:**

✅ **Autenticación Passwordless:** Uso de Passkeys (FIDO2/WebAuthn)  
✅ **Evaluación de Riesgo Continua:** Motor que analiza múltiples factores en cada acceso  
✅ **Autenticación Adaptativa (Step-up):** Verificación adicional según nivel de riesgo  
✅ **Panel de Administración:** Gestión de políticas de acceso y umbrales de riesgo  
✅ **Auditoría Completa:** Registro de todos los eventos de seguridad  
✅ **Dashboard con Métricas:** Visualización de estadísticas en tiempo real  

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                │
│                    HTTPS + Certificados SSL             │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌───────▼──────────────────────────┐
│   Frontend   │  │          Backend                 │
│   React      │  │          FastAPI                 │
│   (Port 3000)│  │          (Port 8000)             │
│              │  │                                   │
│  Components: │  │  • Autenticación FIDO2           │
│  - Login     │  │  • Motor de evaluación riesgo    │
│  - Dashboard │  │  • Políticas de seguridad        │
│  - Admin     │  │  • Auditoría                     │
│  - Step-up   │  │  • APIs RESTful                  │
└──────────────┘  └──────────┬───────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   PostgreSQL     │
                    │   (Port 5432)    │
                    │                  │
                    │  • Usuarios      │
                    │  • Passkeys      │
                    │  • Políticas     │
                    │  • Eventos       │
                    └──────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

### **Backend:**
- Python 3.10
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL 14
- WebAuthn (py_webauthn)
- JWT (python-jose)
- Uvicorn

### **Frontend:**
- React 18
- React Router
- Axios
- CSS3

### **Infraestructura:**
- Docker & Docker Compose
- NGINX (Reverse Proxy + SSL)

---

## 📦 Requisitos Previos

- **Docker Desktop** (Windows/Mac) o **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **Puerto 80, 443, 3000, 5432, 8000** disponibles
- Navegador web compatible con WebAuthn:
  - Chrome/Edge 67+
  - Firefox 60+
  - Safari 13+

---

## 🚀 Instalación

### **1. Clonar o descargar el repositorio**

```bash
# Si está en un repositorio Git
git clone <repository-url>
cd Prototipo_TFG

# O descomprimir el ZIP
unzip Prototipo_TFG.zip
cd Prototipo_TFG
```

### **2. Verificar estructura de archivos**

```
Prototipo_TFG/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── risk/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── database/
│   ├── init.sql
│   └── seed_data.sql
└── docker-compose.yml
```

### **3. Configurar variables de entorno (opcional)**

Crear archivo `.env` en la raíz (opcional, tiene valores por defecto):

```env
# Base de datos
POSTGRES_USER=authuser
POSTGRES_PASSWORD=authpass123
POSTGRES_DB=authdb

# Backend
JWT_SECRET_KEY=tu_clave_secreta_super_segura_cambiar_en_produccion
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend
REACT_APP_API_URL=https://localhost
```

### **4. Levantar el sistema con Docker**

#### **Windows (PowerShell):**

```powershell
# Ir a la carpeta del proyecto
cd C:\Prototipo_TFG

# Levantar todos los servicios
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps
```

#### **Linux/Mac (Terminal):**

```bash
# Ir a la carpeta del proyecto
cd ~/Prototipo_TFG

# Levantar todos los servicios
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps
```

**Resultado esperado:**

```
NAME            STATUS
auth_backend    Up
auth_frontend   Up
auth_nginx      Up
auth_postgres   Up (healthy)
```

### **5. Acceder al sistema**

Abrir navegador y navegar a:

```
https://localhost
```

**Nota:** El navegador mostrará advertencia de certificado (porque es autofirmado). Hacer click en "Avanzado" → "Continuar de todos modos".

---

## 👤 Usuarios de Prueba

### **Usuario Demo (pre-creado):**

```
Email: demo@prototipo.local
```

**Nota:** Este usuario ya está registrado en el sistema. En el primer acceso necesitarás registrar una Passkey nueva con tu dispositivo biométrico.

### **Crear nuevo usuario:**

1. Ir a `/enroll` en el navegador
2. Ingresar email
3. Registrar Passkey con huella/Face ID
4. ¡Listo para usar!

---

## 🎮 Uso del Sistema

### **1. Registro de Passkey**

```
https://localhost/enroll
```

- Ingresar email
- Click en "Registrar Passkey"
- Usar huella digital, Face ID o PIN del dispositivo
- Sistema crea usuario y registra credencial

### **2. Inicio de Sesión**

```
https://localhost/login
```

- Ingresar email
- Click en "Iniciar Sesión"
- Autenticar con dispositivo biométrico
- Evaluación de riesgo automática
- Acceso al Dashboard (si riesgo bajo/medio)

### **3. Dashboard**

```
https://localhost/dashboard
```

**Funcionalidades:**
- 📊 Métricas de autenticación
- 🔑 Gestión de Passkeys
- 📋 Historial de accesos
- 📈 Estadísticas de auditoría

### **4. Panel de Administración**

```
https://localhost/admin
```

**Funcionalidades:**
- Listar todas las políticas de seguridad
- Crear nueva política
- Editar política existente
- Eliminar política
- Activar/desactivar política
- Configurar umbrales de riesgo

**Tipos de acciones en políticas:**
- **Allow:** Permitir acceso directo
- **Step-up:** Requerir verificación adicional
- **Deny:** Denegar acceso

---

## 📊 Casos de Uso Implementados

| ID | Caso de Uso | Estado | Descripción |
|----|-------------|--------|-------------|
| UC-01 | Enrolar Passkey | ✅ 100% | Registro de credencial FIDO2 |
| UC-02 | Login Passwordless | ✅ 100% | Autenticación sin contraseña |
| UC-03 | Verificación Continua | ✅ 75% | Evaluación de riesgo en tiempo real |
| UC-04 | Step-up Authentication | ✅ 90% | Autenticación adaptativa por riesgo |
| UC-05 | Administrar Políticas | ✅ 100% | CRUD de políticas de seguridad |
| UC-06 | Auditoría de Eventos | ✅ 70% | Registro y visualización de eventos |

---

## 🔧 Configuración Avanzada

### **Ajustar umbrales de riesgo**

Editar `backend/risk/policies.py`:

```python
# Ejemplo: Cambiar umbrales
{
    'name': 'high_risk_deny',
    'conditions': {'min_risk_score': 80},  # Cambiar de 75 a 80
    'action': 'deny',
    'priority': 1
}
```

Luego reconstruir:

```bash
docker-compose down
docker-compose build backend
docker-compose up -d
```

### **Configurar factores de riesgo**

Editar `backend/risk/risk_engine.py` para ajustar pesos:

```python
# Ejemplo: Aumentar peso del horario
if not context.get('is_business_hours', True):
    factors['unusual_time'] = 25  # Era 15
```

### **Ver logs en tiempo real**

```bash
# Todos los logs
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

---

## 🧪 Testing

### **Probar endpoints del backend**

Documentación Swagger disponible en:

```
http://localhost:8000/docs
```

Todas las APIs están documentadas con ejemplos de uso.

### **Probar evaluación de riesgo**

1. Login en horario laboral (9-18hs) → Riesgo bajo
2. Login fuera de horario → Riesgo medio
3. Login desde nueva ubicación → Riesgo incrementado
4. Varios intentos fallidos → Riesgo alto

### **Probar step-up authentication**

El sistema dispara step-up cuando el score de riesgo está entre 40-74.

Para forzarlo (testing):
1. Modificar políticas en el panel de admin
2. O editar `backend/risk/policies.py` temporalmente

---

## 🐛 Troubleshooting

### **Error: Puerto ya en uso**

```bash
# Ver qué está usando el puerto
netstat -ano | findstr :80    # Windows
lsof -i :80                   # Linux/Mac

# Parar servicios
docker-compose down
```

### **Error: Certificado SSL no confiable**

Es normal en desarrollo. En el navegador:
- Chrome/Edge: Click en "Avanzado" → "Continuar"
- Firefox: Click en "Avanzado" → "Aceptar riesgo"

### **Error: Base de datos no inicializada**

```bash
# Resetear base de datos
docker-compose down
docker volume rm prototipo_tfg_postgres_data
docker-compose up -d
```

### **Error: Frontend no carga**

```bash
# Reconstruir frontend
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### **Error: Passkey no funciona**

Verificar:
- Navegador compatible con WebAuthn
- HTTPS habilitado (localhost está permitido)
- Dispositivo biométrico configurado

---

## 📚 Documentación de API

### **Principales endpoints:**

#### **Autenticación:**
```
POST /auth/register/begin       - Iniciar registro
POST /auth/register/complete    - Completar registro
POST /auth/login/begin          - Iniciar login
POST /auth/login/complete       - Completar login
POST /auth/stepup/verify        - Verificar step-up
```

#### **Administración:**
```
GET    /admin/policies          - Listar políticas
POST   /admin/policies          - Crear política
PUT    /admin/policies/{id}     - Actualizar política
DELETE /admin/policies/{id}     - Eliminar política
PUT    /admin/policies/{id}/toggle - Activar/desactivar
```

#### **Auditoría:**
```
GET /audit/events               - Listar eventos
GET /audit/stats                - Estadísticas
```

#### **Gestión de Passkeys:**
```
GET    /passkeys/{email}        - Listar passkeys
DELETE /passkeys/{id}           - Revocar passkey
```

Ver documentación completa en: `http://localhost:8000/docs`

---

## 🔒 Consideraciones de Seguridad

### **En Desarrollo:**
- ✅ Certificados SSL autofirmados
- ✅ Claves JWT por defecto
- ✅ CORS habilitado para localhost

### **En Producción (TODO):**
- [ ] Certificados SSL de CA confiable (Let's Encrypt)
- [ ] JWT_SECRET_KEY aleatorio y seguro
- [ ] CORS restringido a dominios específicos
- [ ] Rate limiting
- [ ] Logs centralizados
- [ ] Backup de base de datos
- [ ] Monitoreo y alertas

---

## 📖 Referencias

- **FIDO Alliance:** https://fidoalliance.org/
- **WebAuthn Spec:** https://www.w3.org/TR/webauthn-2/
- **Zero Trust NIST:** https://www.nist.gov/publications/zero-trust-architecture
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/

---

## 📞 Contacto

**Autor:** Zuy, Ariel Hernán  
**Email:** [tu-email@ejemplo.com]  
**Universidad:** Universidad Siglo 21  
**Legajo:** VLSI002384  

---

## 📄 Licencia

Este proyecto es un Trabajo Final de Grado con fines académicos.

---

## ✅ Checklist de Instalación Exitosa

- [ ] Docker Desktop instalado y corriendo
- [ ] Todos los puertos disponibles (80, 443, 3000, 5432, 8000)
- [ ] `docker-compose up -d` ejecutado sin errores
- [ ] Todos los servicios "Up" en `docker-compose ps`
- [ ] `https://localhost` accesible en el navegador
- [ ] Usuario demo puede hacer login con passkey
- [ ] Panel de administración accesible en `/admin`
- [ ] Swagger docs accesible en `http://localhost:8000/docs`

---

**🎉 ¡Sistema listo para usar y demostrar!**
