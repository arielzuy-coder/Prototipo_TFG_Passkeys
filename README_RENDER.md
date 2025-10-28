# ⚡ RESUMEN RÁPIDO - Deploy en Render

## 🎯 Lo que hice por ti

✅ Actualicé tu proyecto con:
1. `render.yaml` - Configuración de deploy
2. `backend/init_db.py` - Inicialización automática de base de datos
3. CORS actualizado en `backend/app.py` para Render
4. `INSTRUCCIONES_DEPLOY.md` - Guía paso a paso completa

---

## 🚀 Pasos Ultra-Rápidos

### 1. Subir a GitHub (5 min)

```bash
cd Prototipo_TFG
git init
git add .
git commit -m "Preparado para deploy en Render"
git remote add origin https://github.com/TU-USUARIO/prototipo-tfg-auth.git
git push -u origin main
```

### 2. Deploy en Render (5 min)

1. Ir a https://render.com
2. Registrarse con GitHub
3. New + → Blueprint
4. Seleccionar tu repositorio
5. Apply
6. ¡Esperar 5-10 minutos!

### 3. Configurar Variables (2 min)

Una vez desplegado:

**auth-backend:**
- `RP_ID` = `auth-backend.onrender.com`
- `ORIGIN` = `https://auth-frontend.onrender.com`

**auth-frontend:**
- `REACT_APP_API_URL` = `https://auth-backend.onrender.com`

### 4. ¡Probar!

Abrir: `https://auth-frontend.onrender.com`

---

## 📁 Archivos Importantes

- **INSTRUCCIONES_DEPLOY.md** - Guía completa paso a paso con screenshots y troubleshooting
- **render.yaml** - Configuración de Render (ya en tu proyecto)
- **backend/init_db.py** - Script de inicialización (ya en tu proyecto)

---

## ⚠️ IMPORTANTE

Después del deploy, DEBES configurar las variables:

1. `RP_ID` en backend = dominio del backend (SIN https://)
2. `ORIGIN` en backend = URL completa del frontend (CON https://)
3. `REACT_APP_API_URL` en frontend = URL completa del backend

**Sin esto, WebAuthn NO funcionará.**

---

## ✅ URLs Finales

Después del deploy tendrás:

- **Frontend:** `https://auth-frontend.onrender.com`
- **Backend:** `https://auth-backend.onrender.com`
- **API Docs:** `https://auth-backend.onrender.com/docs`

---

## 🆘 Problemas Comunes

**502 Bad Gateway:** Espera 30 seg, el servicio está despertando

**CORS Error:** Verifica `ORIGIN` y `RP_ID` en variables de entorno

**WebAuthn no funciona:** `RP_ID` debe ser el dominio del backend sin https://

**Más ayuda:** Lee `INSTRUCCIONES_DEPLOY.md`

---

## 🎓 Para tu TFG

Antes de presentar:
- Abre la app 10 min antes (para "despertarla")
- Haz un login de prueba
- Verifica que todo funciona

Durante la presentación:
- Menciona "desplegado en Render.com"
- Menciona "SSL automático con Let's Encrypt"
- Menciona "PostgreSQL en la nube"
- Menciona "WebAuthn/FIDO2 en producción"

---

## 💰 Costo

**$0 - Completamente GRATIS**

(Con limitación de que se duerme tras 15 min sin uso)

---

**¡TODO LISTO! Lee INSTRUCCIONES_DEPLOY.md para detalles completos.**

🎉 ¡Éxito con tu TFG!
