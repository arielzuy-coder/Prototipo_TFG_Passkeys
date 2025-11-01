#!/usr/bin/env python3
"""
Script para agregar política de geolocalización al sistema Zero Trust.

Este script agrega una política de alta prioridad que requiere step-up
para accesos desde fuera de Argentina.

Uso:
    python add_geolocation_policy.py --diagnose    # Ver estado actual
    python add_geolocation_policy.py --add         # Agregar política
    python add_geolocation_policy.py --verify      # Verificar implementación

Autor: TFG - Sistema de Autenticación Adaptativa
Fecha: 2025-10-31
"""

import sys
import os
import argparse
from datetime import datetime

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from models import Policy
    from config import settings
    from sqlalchemy.exc import SQLAlchemyError
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de ejecutar este script desde el directorio backend/")
    sys.exit(1)

# Configuración de la nueva política
GEOLOCATION_POLICY = {
    'name': 'foreign_country_stepup',
    'description': 'Requiere step-up para accesos desde fuera de Argentina',
    'conditions': {'allowed_countries': ['AR']},
    'action': 'stepup',
    'priority': 0
}

def print_header(text):
    """Imprime un header formateado."""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80 + "\n")

def diagnose_policies(db):
    """Muestra el estado actual de las políticas."""
    
    print_header("🔍 DIAGNÓSTICO: Estado Actual de las Políticas")
    
    policies = db.query(Policy).order_by(Policy.priority.asc()).all()
    
    if not policies:
        print("⚠️  NO HAY POLÍTICAS EN LA BASE DE DATOS\n")
        return False
    
    print(f"📊 Total de políticas: {len(policies)}\n")
    
    # Verificar si existe la política de geolocalización
    geo_policy = db.query(Policy).filter(
        Policy.name == GEOLOCATION_POLICY['name']
    ).first()
    
    if geo_policy:
        print("✅ La política de geolocalización YA EXISTE:")
        print(f"   • Nombre: {geo_policy.name}")
        print(f"   • Prioridad: {geo_policy.priority}")
        print(f"   • Condiciones: {geo_policy.conditions}")
        print(f"   • Acción: {geo_policy.action}")
        print(f"   • Habilitada: {geo_policy.enabled}\n")
    else:
        print("⚠️  La política de geolocalización NO EXISTE\n")
    
    # Mostrar todas las políticas
    print("📋 Políticas actuales:\n")
    for i, policy in enumerate(policies, 1):
        status = "✅" if policy.enabled else "❌"
        print(f"[{policy.priority}] {status} {policy.name}")
        print(f"    └─ Acción: {policy.action.upper()}")
        print(f"    └─ Condiciones: {policy.conditions}")
        print()
    
    # Simulación de caso de uso
    print_header("🧪 SIMULACIÓN: Acceso desde USA")
    
    print("Contexto:")
    print("  • Usuario: usuario@ejemplo.com")
    print("  • IP: 169.197.85.172 (USA)")
    print("  • Dispositivo: CASA (conocido)")
    print("  • Score de riesgo: 11.75")
    print()
    
    if geo_policy and geo_policy.enabled:
        print("✅ Resultado ACTUAL:")
        print("   [0] foreign_country_stepup → País US no está en ['AR']")
        print("   → Acción: STEPUP ✅")
        print("   → Nivel de Riesgo: HIGH")
        print("   → Verificación adicional requerida\n")
    else:
        print("❌ Resultado ACTUAL:")
        print("   [3] low_risk_allow → Score 11.75 ≤ 39")
        print("   → Acción: ALLOW ❌")
        print("   → Nivel de Riesgo: LOW")
        print("   → Acceso directo (INCORRECTO)\n")
        print("⚠️  NECESITAS agregar la política de geolocalización")
    
    return geo_policy is not None

def add_geolocation_policy(db):
    """Agrega la política de geolocalización."""
    
    print_header("✨ AGREGANDO POLÍTICA DE GEOLOCALIZACIÓN")
    
    try:
        # 1. Verificar si ya existe
        existing = db.query(Policy).filter(
            Policy.name == GEOLOCATION_POLICY['name']
        ).first()
        
        if existing:
            print(f"⚠️  La política '{GEOLOCATION_POLICY['name']}' ya existe.")
            print(f"   Prioridad actual: {existing.priority}")
            
            response = input("\n¿Deseas eliminarla y recrearla? (s/n): ")
            if response.lower() not in ['s', 'si', 'y', 'yes']:
                print("\n❌ Operación cancelada.\n")
                return False
            
            print(f"\n🗑️  Eliminando política existente...")
            db.delete(existing)
            db.commit()
            print("✅ Política eliminada.\n")
        
        # 2. Ajustar prioridades de políticas existentes
        print("🔄 Ajustando prioridades de políticas existentes...")
        policies_to_update = db.query(Policy).filter(
            Policy.priority >= 0
        ).all()
        
        updated_count = 0
        for policy in policies_to_update:
            old_priority = policy.priority
            policy.priority = policy.priority + 1
            print(f"   • {policy.name}: {old_priority} → {policy.priority}")
            updated_count += 1
        
        db.commit()
        print(f"✅ {updated_count} políticas actualizadas.\n")
        
        # 3. Crear nueva política de geolocalización
        print("✨ Creando política de geolocalización...")
        
        new_policy = Policy(
            name=GEOLOCATION_POLICY['name'],
            description=GEOLOCATION_POLICY['description'],
            conditions=GEOLOCATION_POLICY['conditions'],
            action=GEOLOCATION_POLICY['action'],
            priority=GEOLOCATION_POLICY['priority'],
            enabled=True
        )
        
        db.add(new_policy)
        db.commit()
        
        print(f"✅ Política creada:")
        print(f"   • Nombre: {new_policy.name}")
        print(f"   • Prioridad: {new_policy.priority}")
        print(f"   • Condiciones: {new_policy.conditions}")
        print(f"   • Acción: {new_policy.action}\n")
        
        # 4. Verificar
        print("🔍 Verificando creación...")
        policies = db.query(Policy).order_by(Policy.priority.asc()).all()
        
        print(f"   Total de políticas: {len(policies)}")
        
        geo_policy = policies[0] if policies else None
        if geo_policy and geo_policy.name == GEOLOCATION_POLICY['name']:
            print(f"   ✅ Política de geolocalización en prioridad 0\n")
            return True
        else:
            print(f"   ⚠️  Advertencia: La política no está en prioridad 0\n")
            return False
            
    except SQLAlchemyError as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        return False

def verify_implementation(db):
    """Verifica que la implementación sea correcta."""
    
    print_header("✅ VERIFICACIÓN DE IMPLEMENTACIÓN")
    
    policies = db.query(Policy).order_by(Policy.priority.asc()).all()
    
    if not policies:
        print("❌ ERROR: No hay políticas en la base de datos.\n")
        return False
    
    # Verificar política de geolocalización
    geo_policy = policies[0] if policies else None
    
    if not geo_policy or geo_policy.name != GEOLOCATION_POLICY['name']:
        print("❌ ERROR: La política de geolocalización no está en prioridad 0.\n")
        return False
    
    print("📋 Orden de políticas:\n")
    for policy in policies:
        status = "✅" if policy.enabled else "❌"
        print(f"[{policy.priority}] {status} {policy.name}: {policy.action.upper()}")
    
    # Verificar condiciones de la política
    print("\n🔍 Verificando configuración de geolocalización...")
    
    checks = [
        (geo_policy.conditions == GEOLOCATION_POLICY['conditions'], "Condiciones"),
        (geo_policy.action == GEOLOCATION_POLICY['action'], "Acción"),
        (geo_policy.priority == GEOLOCATION_POLICY['priority'], "Prioridad"),
        (geo_policy.enabled == True, "Habilitada")
    ]
    
    all_ok = True
    for is_ok, field in checks:
        if is_ok:
            print(f"   ✅ {field}: correcto")
        else:
            print(f"   ❌ {field}: incorrecto")
            all_ok = False
    
    if all_ok:
        print("\n" + "="*80)
        print(" ✅ VERIFICACIÓN EXITOSA")
        print("="*80)
        print("\n🎯 RESULTADO:")
        print("   • Política de geolocalización instalada correctamente")
        print("   • Accesos desde fuera de Argentina requerirán step-up")
        print("   • Accesos desde Argentina se evaluarán por score\n")
        
        print("🧪 PRÓXIMAS PRUEBAS:")
        print("   1. Accede desde USA → Debería mostrar HIGH + step-up")
        print("   2. Accede desde Argentina → Evaluación normal por score\n")
    else:
        print("\n" + "="*80)
        print(" ❌ VERIFICACIÓN FALLIDA")
        print("="*80)
        print("\nAlgunos campos no están configurados correctamente.")
        print("Intenta ejecutar el script con --add nuevamente.\n")
    
    return all_ok

def main():
    """Función principal."""
    
    parser = argparse.ArgumentParser(
        description='Agregar política de geolocalización al sistema'
    )
    parser.add_argument(
        '--diagnose',
        action='store_true',
        help='Ver estado actual de las políticas'
    )
    parser.add_argument(
        '--add',
        action='store_true',
        help='Agregar política de geolocalización'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verificar que la política esté correctamente instalada'
    )
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna acción, mostrar ayuda
    if not (args.diagnose or args.add or args.verify):
        parser.print_help()
        print("\n💡 SUGERENCIA: Comienza con --diagnose para ver el estado actual\n")
        return
    
    # Conectar a la base de datos
    print("\n🔌 Conectando a la base de datos...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("✅ Conexión exitosa\n")
    except Exception as e:
        print(f"❌ Error al conectar: {e}\n")
        print("Verifica que:")
        print("  • La base de datos esté accesible")
        print("  • Las credenciales en .env sean correctas")
        print("  • DATABASE_URL esté configurado\n")
        return
    
    try:
        # Ejecutar acción solicitada
        if args.diagnose:
            diagnose_policies(db)
        
        elif args.add:
            # Primero diagnosticar
            exists = diagnose_policies(db)
            
            if exists:
                print("\n⚠️  La política ya existe.")
                print("   Para recrearla, el script te preguntará.\n")
            else:
                print("\n➡️  Procediendo a agregar la política...\n")
            
            success = add_geolocation_policy(db)
            
            if success:
                print("="*80)
                print(" ✅ POLÍTICA AGREGADA EXITOSAMENTE")
                print("="*80)
                print("\n📝 PRÓXIMOS PASOS:")
                print("   1. El sistema aplicará los cambios inmediatamente")
                print("   2. No necesitas reiniciar el backend en Render")
                print("   3. Prueba accediendo desde USA")
                print("   4. Ejecuta: python add_geolocation_policy.py --verify\n")
            else:
                print("❌ La operación falló. Revisa los errores.\n")
        
        elif args.verify:
            verify_implementation(db)
    
    finally:
        db.close()
        print("🔌 Conexión cerrada\n")

if __name__ == "__main__":
    main()
