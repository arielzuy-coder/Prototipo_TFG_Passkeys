# 🚀 INSTRUCCIONES DE DEPLOY EN RENDER.COM

## ✅ Archivos Preparados

Ya preparé tu proyecto con todo lo necesario:

1. ✅ `render.yaml` - Configuración de Render
2. ✅ `backend/init_db.py` - Script de inicialización de base de datos
3. ✅ CORS actualizado en `backend/app.py` para funcionar con Render
4. ✅ `.gitignore` configurado correctamente

---

## 📝 PASO 1: Subir a GitHub

### 1.1. Abrir terminal en la carpeta del proyecto

**Windows:**
- Abre la carpeta `Prototipo_TFG` en el Explorador
- Click derecho en un espacio vacío
- Selecciona "Abrir en Terminal" o "Git Bash Here"

**Linux/Mac:**
```bash
cd /ruta/a/Prototipo_TFG
```

### 1.2. Inicializar Git

```bash
git init
```

### 1.3. Agregar todos los archivos

```bash
git add .
```

### 1.4. Hacer commit

```bash
git commit -m "Preparado para deploy en Render"
```

### 1.5. Crear repositorio en GitHub

1. Ve a: https://github.com/new
2. Nombre: `prototipo-tfg-auth` (o el que prefieras)
3. Descripción: "Sistema de autenticación passwordless con WebAuthn y Zero Trust"
4. Elige **Público** o **Privado** (tu preferencia)
5. **NO marques** "Initialize this repository with a README"
6. Click en **"Create repository"**

### 1.6. Conectar y subir código

GitHub te mostrará comandos. Usa estos:

```bash
# Conectar con tu repositorio (usa TU URL que aparece en GitHub)
git remote add origin https://github.com/TU-USUARIO/prototipo-tfg-auth.git

# Cambiar branch a main
git branch -M main

# Subir código
git push -u origin main
```

**Si pide autenticación:**
- Usuario: Tu usuario de GitHub
- Contraseña: Usa un **Personal Access Token** (no tu password normal)
  - Crear token: https://github.com/settings/tokens
  - Permisos: Solo marca "repo"

---

## 🌐 PASO 2: Crear Cuenta en Render

1. Ve a: https://render.com
2. Click en **"Get Started for Free"**
3. Elige **"Sign in with GitHub"** (más fácil)
4. Autoriza a Render para acceder a tu GitHub
5. Listo, ya tienes cuenta

---

## 🚀 PASO 3: Deploy con Blueprint

### 3.1. Crear Blueprint

1. En el Dashboard de Render, click en **"New +"** (arriba a la derecha)
2. Selecciona **"Blueprint"**
3. Verás tus repositorios de GitHub
4. Click en **"Connect"** al lado de `prototipo-tfg-auth`
   - Si no aparece, click en "Configure account" y da permisos

### 3.2. Configurar Blueprint

1. Render detectará automáticamente tu `render.yaml`
2. Verás la configuración:
   - ✅ auth-backend (Web Service)
   - ✅ auth-frontend (Web Service)
   - ✅ auth-postgres (Database)
3. Click en **"Apply"**

### 3.3. Esperar el deploy

- Render comenzará a construir y desplegar todo
- Verás 3 servicios en tu Dashboard:
  - 🟡 auth-backend (Building...)
  - 🟡 auth-frontend (Building...)
  - 🟢 auth-postgres (Live)
- El primer deploy toma **5-10 minutos**
- Puedes ver los logs en tiempo real haciendo click en cada servicio

### 3.4. URLs generadas

Una vez que termine (todos en 🟢 Live), tendrás:

- **Backend:** `https://auth-backend.onrender.com`
- **Frontend:** `https://auth-frontend.onrender.com`

**IMPORTANTE:** Anota estas URLs, las necesitarás en el siguiente paso.

---

## ⚙️ PASO 4: Configurar Variables de Entorno

### 4.1. Configurar Backend

1. En el Dashboard, click en **"auth-backend"**
2. En el menú izquierdo, click en **"Environment"**
3. Busca estas variables y **actualízalas**:

**Variables a cambiar:**

```
RP_ID
Valor actual: changeme-backend-url.onrender.com
Nuevo valor: auth-backend.onrender.com
(Usa la URL real de tu backend, sin https://)

ORIGIN
Valor actual: https://changeme-frontend-url.onrender.com
Nuevo valor: https://auth-frontend.onrender.com
(Usa la URL completa de tu frontend)
```

4. Click en **"Save Changes"**
5. Render redesplegará automáticamente el backend (~2 minutos)

### 4.2. Configurar Frontend

1. En el Dashboard, click en **"auth-frontend"**
2. En el menú izquierdo, click en **"Environment"**
3. Verifica/actualiza:

```
REACT_APP_API_URL
Valor debe ser: https://auth-backend.onrender.com
(La URL completa de tu backend)
```

4. Si necesitas cambiarla, click en **"Save Changes"**
5. Render redesplegará el frontend (~2 minutos)

---

## ✅ PASO 5: Verificar que Funciona

### 5.1. Abrir la aplicación

1. En el Dashboard de Render
2. Click en **"auth-frontend"**
3. Arriba verás la URL: `https://auth-frontend.onrender.com`
4. Click en la URL para abrirla en tu navegador

### 5.2. Primera carga

⚠️ **IMPORTANTE:** La primera vez puede tardar ~30 segundos en cargar
- Esto es normal en el plan gratuito
- Los servicios se "duermen" tras 15 min sin uso
- Una vez que carga, funciona normal

### 5.3. Probar Registro

1. Deberías ver la página de login
2. Navega a la página de registro:
   - En la URL agrega `/enroll`
   - Ejemplo: `https://auth-frontend.onrender.com/enroll`
3. Ingresa un email de prueba: `test@ejemplo.com`
4. Click en **"Registrar Passkey"**
5. Tu navegador pedirá usar:
   - Huella digital 👆
   - Face ID 🤳
   - PIN del dispositivo 🔢
6. Acepta y autoriza

### 5.4. Probar Login

1. Ve a la página de login: `https://auth-frontend.onrender.com/login`
2. Ingresa el mismo email: `test@ejemplo.com`
3. Click en **"Iniciar Sesión"**
4. Autoriza con tu dispositivo biométrico
5. Deberías entrar al **Dashboard** ✅

### 5.5. Verificar Dashboard

Si ves el Dashboard con:
- ✅ Tus estadísticas
- ✅ Métricas de acceso
- ✅ Lista de Passkeys
- ✅ Panel de administración accesible

**¡DEPLOY EXITOSO! 🎉**

---

## 🐛 Solución de Problemas Comunes

### Problema 1: "502 Bad Gateway" o "Service Unavailable"

**Causa:** El servicio se está iniciando (despertando del modo sleep)

**Solución:**
- Espera 30-60 segundos
- Recarga la página
- Esto solo pasa después de 15 min sin uso

### Problema 2: Error "Invalid origin" o "CORS error"

**Causa:** Las variables `ORIGIN` o `RP_ID` están mal configuradas

**Solución:**
1. Ve a **auth-backend** → **Environment**
2. Verifica que:
   - `RP_ID` = `auth-backend.onrender.com` (SIN https://)
   - `ORIGIN` = `https://auth-frontend.onrender.com` (CON https://)
3. Si están mal, corrígelas y guarda
4. Espera que redesplegue (~2 min)

### Problema 3: WebAuthn no funciona / No se registra Passkey

**Causa:** `RP_ID` no coincide con el dominio del backend

**Solución:**
1. Ve a **auth-backend** → **Environment**
2. Verifica `RP_ID`
3. Debe ser exactamente: `auth-backend.onrender.com`
4. NO debe tener:
   - ❌ `https://`
   - ❌ Espacios
   - ❌ Barra final `/`
5. Formato correcto: `auth-backend.onrender.com` ✅

### Problema 4: Frontend no carga o muestra página en blanco

**Causa:** Error en el build de React o variables mal configuradas

**Solución:**
1. Ve a **auth-frontend** → **Logs**
2. Busca errores (líneas en rojo)
3. Si dice "REACT_APP_API_URL is undefined":
   - Ve a **Environment**
   - Agrega: `REACT_APP_API_URL` = `https://auth-backend.onrender.com`
   - Guarda y espera redespliegue
4. Si persiste:
   - Click en **"Manual Deploy"** → **"Clear build cache & deploy"**

### Problema 5: Base de datos vacía / No hay políticas

**Causa:** El script `init_db.py` no se ejecutó correctamente

**Solución:**
1. Ve a **auth-backend** → **Logs**
2. Busca líneas que digan:
   - "Creando tablas de base de datos..."
   - "✅ Tablas creadas exitosamente"
3. Si no aparecen o hay errores:
   - Click en **"Manual Deploy"** → **"Deploy latest commit"**
4. Los logs deberían mostrar la inicialización correcta

### Problema 6: "Build failed"

**Causa:** Error en el código o dependencias

**Solución:**
1. Ve al servicio que falló
2. Click en **"Logs"**
3. Lee el error (última línea en rojo)
4. Errores comunes:
   - Falta algún archivo
   - Error de sintaxis
   - Dependencia faltante
5. Corrígelo en tu código local
6. Sube los cambios:
   ```bash
   git add .
   git commit -m "Corregir error de build"
   git push
   ```
7. Render redesplegará automáticamente

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs en Tiempo Real

1. Ve a cualquier servicio
2. Click en **"Logs"** en el menú izquierdo
3. Verás:
   - Requests entrantes
   - Errores
   - Logs de la aplicación

### Ver Métricas

1. En cada servicio
2. Verás gráficos de:
   - CPU usage
   - Memory usage
   - Request rate

### Hacer Actualizaciones

Si haces cambios en tu código:

```bash
cd Prototipo_TFG

# Hacer cambios...

git add .
git commit -m "Descripción de cambios"
git push
```

Render detectará el push automáticamente y redesplegará tu app.

---

## 🎓 Tips para la Presentación de TFG

### Antes de Presentar (10 minutos antes)

1. **"Despertar" la aplicación:**
   - Abre `https://auth-frontend.onrender.com` en tu navegador
   - Haz un login de prueba
   - Navega por el dashboard
   - Esto evita el delay de 30 seg al iniciar

2. **Verificar que todo funciona:**
   - ✅ Login con Passkey
   - ✅ Dashboard carga
   - ✅ Admin panel accesible
   - ✅ Métricas se muestran

3. **Tener datos de ejemplo:**
   - Crea 2-3 usuarios de prueba
   - Registra Passkeys en diferentes dispositivos
   - Genera historial de accesos

### Durante la Presentación

**Puntos a mencionar:**

- "Aplicación desplegada en **Render.com**, una plataforma cloud moderna"
- "**SSL/TLS automático** con certificados de Let's Encrypt"
- "Base de datos **PostgreSQL** en la nube con persistencia de datos"
- "**WebAuthn/FIDO2** funcionando en producción real"
- "Arquitectura de **microservicios** con backend (Python/FastAPI) y frontend (React)"
- "Accesible desde **cualquier dispositivo** con internet"

**Demostración sugerida:**

1. Mostrar página de registro
2. Registrar nueva Passkey en vivo
3. Hacer login con biometría
4. Mostrar dashboard con métricas
5. Demostrar evaluación de riesgo
6. Mostrar admin panel con políticas

### Plan B

Graba un video de la demo por si:
- Falla internet en la presentación
- Render tiene problemas (raro pero posible)
- Tu dispositivo no tiene biometría disponible

---

## 💰 Costos y Planes

### Plan Actual (Gratuito)

✅ Incluye:
- 750 horas/mes de runtime
- SSL automático
- Base de datos PostgreSQL (1GB)
- Deploy automático desde GitHub

⚠️ Limitaciones:
- Servicios se duermen tras 15 min sin uso
- BD se borra tras 90 días de inactividad
- Recursos limitados (512MB RAM por servicio)

### Si Necesitas Más (Opcional)

**Starter Plan ($7/mes por servicio):**
- ✅ No se duerme nunca
- ✅ 2GB RAM
- ✅ Mejor rendimiento

**PostgreSQL Plan ($7/mes):**
- ✅ 50GB almacenamiento
- ✅ No borra datos nunca
- ✅ Backups automáticos

**Para TFG:** El plan gratuito es más que suficiente

---

## 🔗 URLs de Referencia

Guarda estas URLs:

**Tu Aplicación:**
- Frontend: https://auth-frontend.onrender.com
- Backend API: https://auth-backend.onrender.com
- API Docs: https://auth-backend.onrender.com/docs

**Dashboards:**
- Render Dashboard: https://dashboard.render.com
- GitHub Repo: https://github.com/TU-USUARIO/prototipo-tfg-auth

---

## ✅ Checklist Final

Antes de dar por terminado el deploy:

- [ ] Frontend carga en `https://auth-frontend.onrender.com`
- [ ] Backend responde en `https://auth-backend.onrender.com/health`
- [ ] API docs accesible en `https://auth-backend.onrender.com/docs`
- [ ] Puedo registrar una Passkey en `/enroll`
- [ ] Puedo hacer login con la Passkey
- [ ] Dashboard muestra datos
- [ ] Admin panel es accesible
- [ ] SSL funciona (candado verde 🔒 en navegador)
- [ ] Variables `RP_ID` y `ORIGIN` configuradas correctamente

---

## 🎉 ¡Éxito!

Tu aplicación ahora está:
- ✅ Desplegada en la nube
- ✅ Accesible públicamente
- ✅ Con HTTPS funcionando
- ✅ WebAuthn operativo
- ✅ Sin costo
- ✅ Lista para tu TFG

**¡Mucha suerte con tu presentación! 🎓**

---

## 📞 Soporte

Si tienes problemas:

1. Revisa la sección "Solución de Problemas Comunes" arriba
2. Verifica los logs en Render Dashboard
3. Consulta la documentación: https://render.com/docs
4. Render Community: https://community.render.com

---

**Creado:** Octubre 2025  
**Para:** TFG Universidad Siglo 21  
**Versión:** 1.0
