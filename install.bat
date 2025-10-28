@echo off
REM Script de instalacion automatizada para Windows
REM Prototipo de Autenticacion Passkeys + Zero Trust
REM Autor: Zuy, Ariel Hernan

echo ========================================
echo   Instalacion del Prototipo
echo   Autenticacion Passkeys + Zero Trust
echo ========================================
echo.

REM Verificar Docker
echo Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta instalado
    echo Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo OK: Docker encontrado

REM Verificar Docker Compose
echo Verificando Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose no esta instalado
    pause
    exit /b 1
)
echo OK: Docker Compose encontrado

REM Copiar .env
if not exist .env (
    echo Creando archivo .env...
    copy .env.example .env
    echo OK: Archivo .env creado
) else (
    echo INFO: Archivo .env ya existe
)

REM Generar certificados SSL
echo Generando certificados SSL...
cd nginx\ssl
if not exist cert.pem (
    echo Ejecutando generacion de certificados...
    docker run --rm -v %cd%:/certs alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/key.pem -out /certs/cert.pem -subj "/C=AR/ST=BuenosAires/L=Lanus/O=UniversidadSiglo21/CN=localhost"
    echo OK: Certificados SSL generados
) else (
    echo INFO: Certificados SSL ya existen
)
cd ..\..

REM Construir imagenes
echo Construyendo imagenes Docker...
docker-compose build
echo OK: Imagenes construidas

REM Levantar servicios
echo Levantando servicios...
docker-compose up -d
echo OK: Servicios iniciados

REM Esperar
echo Esperando a que los servicios esten listos...
timeout /t 15 /nobreak

REM Verificar estado
echo Verificando estado..