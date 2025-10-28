#!/bin/bash

# Script de instalacion automatizada del prototipo
# Prototipo de Autenticacion Passkeys + Zero Trust
# Autor: Zuy, Ariel Hernan

set -e

echo "========================================"
echo "  Instalacion del Prototipo"
echo "  Autenticacion Passkeys + Zero Trust"
echo "========================================"
echo ""

# Verificar Docker
echo "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no esta instalado"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "OK: Docker encontrado: $(docker --version)"

# Verificar Docker Compose
echo "Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose no esta instalado"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "OK: Docker Compose encontrado: $(docker-compose --version)"

# Copiar .env si no existe
if [ ! -f .env ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "OK: Archivo .env creado"
else
    echo "INFO: Archivo .env ya existe, omitiendo..."
fi

# Generar certificados SSL
echo "Generando certificados SSL autofirmados..."
cd nginx/ssl
if [ ! -f cert.pem ] || [ ! -f key.pem ]; then
    docker run --rm -v $(pwd):/certs alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/key.pem -out /certs/cert.pem -subj "/C=AR/ST=BuenosAires/L=Lanus/O=UniversidadSiglo21/CN=localhost"
    echo "OK: Certificados SSL generados"
else
    echo "INFO: Certificados SSL ya existen, omitiendo..."
fi
cd ../..

# Construir imagenes
echo "Construyendo imagenes Docker..."
docker-compose build
echo "OK: Imagenes construidas"

# Levantar servicios
echo "Levantando servicios..."
docker-compose up -d
echo "OK: Servicios iniciados"

# Esperar a que PostgreSQL este listo
echo "Esperando a que PostgreSQL este listo..."
sleep 15

# Verificar estado
echo "Verificando estado de servicios..."
docker-compose ps

echo ""
echo "========================================"
echo "  Instalacion completada!"
echo "========================================"
echo ""
echo "Accesos:"
echo "  - Frontend:  https://localhost"
echo "  - Backend:   https://localhost:8000"
echo "  - API Docs:  https://localhost:8000/docs"
echo ""
echo "NOTA: Tu navegador mostrara advertencia de"
echo "certificado autofirmado. Acepta el riesgo"
echo "para continuar (solo en desarrollo)."
echo ""
echo "Comandos utiles:"
echo "  - Ver logs:     docker-compose logs -f"
echo "  - Detener:      docker-compose down"
echo "  - Reiniciar:    docker-compose restart"
echo ""