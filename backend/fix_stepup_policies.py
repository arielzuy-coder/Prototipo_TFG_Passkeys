#!/usr/bin/env python3
"""
Script automatizado para diagnosticar y corregir el problema de step-up authentication.

Uso:
    python fix_stepup_policies.py --diagnose    # Solo diagnóstico
    python fix_stepup_policies.py --fix         # Diagnosticar y corregir
    python fix_stepup_policies.py --verify      # Verificar corrección

Autor: TFG - Sistema de Autenticación Adaptativa
Fecha: 2025-10-29
"""

import sys
import os
import argparse
from datetime import datetime

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.models import Policy
    from backend.config import SessionLocal
    from sqlalchemy.exc import SQLAlchemyError
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de ejecutar este script desde el directorio raíz del proyecto.")
    sys.exit(1)

# Políticas por defecto correctas
DEFAULT_POLICIES = [
    {
        'name': 'high_risk_deny',
        'description': 'Denegar acceso si el riesgo es alto',
        'conditions': {'min_risk_score': 75},
        'action': 'deny',
        'priority': 1
    },
    {
        'name': 'medium_risk_stepup',
        'description': 'Requerir autenticación adicional para riesgo medio',
        'conditions': {'min_risk_score': 40, 'max_risk_score': 74},
        'action': 'stepup',
        'priority': 2
    },
    {
        'name': 'low_risk_allow',
        'description': 'Permitir acceso si el riesgo es bajo',
        'conditions': {'max_risk_score': 39},
        'action': 'allow',
        'priority': 3
    }
]

def print_header(text):
    """Imprime un header formateado."""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70 + "\n")

def diagnose_policies(db):
    """Diagnostica el estado actual de las políticas."""
    
    print_header("🔍 DIAGNÓSTICO DE POLÍTICAS")
    
    policies = db.query(Policy).filter(Policy.enabled == True).order_by(Policy.priority.asc()).all()
    
    print(f"📊 Total de políticas activas: {len(policies)}\n")
    
    if not policies:
        print("⚠️  NO HAY POLÍTICAS EN LA BASE DE DATOS")
        print("   El sistema creará políticas por defecto al primer uso.\n")
        return False
    
    # Mostrar políticas actuales
    print("📋 Políticas encontradas:\n")
    
    policies_correct = True
    
    for i, policy in enumerate(policies, 1):
        print(f"--- Política {i} ---")
        print(f"  Nombre: {policy.name}")
        print(f"  Descripción: {policy.description}")
        print(f"  Condiciones: {policy.conditions}")
        print(f"  Acción: {policy.action}")
        print(f"  Prioridad: {policy.priority}\n")
        
        # Verificar si es correcta
        expected = next((p for p in DEFAULT_POLICIES if p['name'] == policy.name), None)
        
        if expected:
            if (policy.conditions == expected['conditions'] and 
                policy.action == expected['action'] and
                policy.priority == expected['priority']):
                print(f"  ✅ Política correcta\n")
            else:
                print(f"  ❌ Política INCORRECTA")
                print(f"     Esperado: {expected}\n")
                policies_correct = False
        else:
            print(f"  ⚠️  Política personalizada (no está en defaults)\n")
    
    # Verificar caso específico: score=11
    print_header("🧪 PRUEBA: Score de Riesgo = 11")
    
    score = 11
    matched = None
    
    for policy in policies:
        conditions = policy.conditions
        matches = True
        
        if 'min_risk_score' in conditions:
            if score < conditions['min_risk_score']:
                matches = False
                
        if 'max_risk_score' in conditions:
            if score > conditions['max_risk_score']:
                matches = False
                
        if matches:
            matched = policy
            break
    
    if matched:
        print(f"Política que se aplicaría: {matched.name}")
        print(f"Acción: {matched.action.upper()}")
        
        if matched.action == 'allow':
            print("\n✅ CORRECTO: Con score=11, el sistema debería permitir acceso directo")
            print("   NO hay problema con las políticas.")
        elif matched.action == 'stepup':
            print("\n❌ ERROR: Con score=11, el sistema está pidiendo STEP-UP")
            print("   Debería permitir acceso directo (allow)")
            print("   Las políticas están INCORRECTAS.")
            policies_correct = False
        elif matched.action == 'deny':
            print("\n❌ ERROR CRÍTICO: Con score=11, el sistema está DENEGANDO acceso")
            print("   Debería permitir acceso directo (allow)")
            print("   Las políticas están INCORRECTAS.")
            policies_correct = False
    else:
        print("⚠️  Ninguna política matchea con score=11")
        print("   Se usaría la política por defecto (allow)")
    
    return policies_correct

def fix_policies(db):
    """Corrige las políticas resetéandolas a los valores por defecto."""
    
    print_header("🔧 CORRIGIENDO POLÍTICAS")
    
    try:
        # 1. Eliminar políticas existentes
        print("🗑️  Eliminando políticas actuales...")
        deleted_count = db.query(Policy).delete()
        print(f"   Eliminadas: {deleted_count} políticas\n")
        
        # 2. Crear políticas por defecto
        print("✨ Creando políticas por defecto...\n")
        
        for policy_data in DEFAULT_POLICIES:
            policy = Policy(
                name=policy_data['name'],
                description=policy_data['description'],
                conditions=policy_data['conditions'],
                action=policy_data['action'],
                priority=policy_data['priority'],
                enabled=True
            )
            db.add(policy)
            print(f"   ✅ Creada: {policy_data['name']} (acción: {policy_data['action']})")
        
        # 3. Guardar cambios
        db.commit()
        print("\n💾 Políticas guardadas en la base de datos")
        
        # 4. Verificar
        print("\n🔍 Verificando políticas creadas...")
        policies = db.query(Policy).filter(Policy.enabled == True).all()
        print(f"   Total de políticas: {len(policies)}")
        
        if len(policies) == 3:
            print("\n✅ CORRECCIÓN EXITOSA")
            print("   Las políticas se han resetado a los valores por defecto correctos.")
            return True
        else:
            print("\n⚠️  ADVERTENCIA: Se esperaban 3 políticas, pero hay {len(policies)}")
            return False
            
    except SQLAlchemyError as e:
        print(f"\n❌ ERROR al corregir políticas: {e}")
        db.rollback()
        return False

def verify_fix(db):
    """Verifica que la corrección se haya aplicado correctamente."""
    
    print_header("✅ VERIFICACIÓN DE CORRECCIÓN")
    
    policies = db.query(Policy).filter(Policy.enabled == True).order_by(Policy.priority.asc()).all()
    
    if len(policies) != 3:
        print(f"❌ ERROR: Se esperaban 3 políticas, pero hay {len(policies)}")
        return False
    
    print("📋 Verificando cada política...\n")
    
    all_correct = True
    
    for expected in DEFAULT_POLICIES:
        policy = db.query(Policy).filter(Policy.name == expected['name']).first()
        
        if not policy:
            print(f"❌ Política '{expected['name']}' NO ENCONTRADA")
            all_correct = False
            continue
            
        # Verificar cada campo
        checks = [
            (policy.description == expected['description'], "descripción"),
            (policy.conditions == expected['conditions'], "condiciones"),
            (policy.action == expected['action'], "acción"),
            (policy.priority == expected['priority'], "prioridad"),
            (policy.enabled == True, "habilitada")
        ]
        
        policy_ok = all(check[0] for check in checks)
        
        if policy_ok:
            print(f"✅ {policy.name}: CORRECTA")
        else:
            print(f"❌ {policy.name}: INCORRECTA")
            for is_ok, field in checks:
                if not is_ok:
                    print(f"   • {field} no coincide")
            all_correct = False
    
    # Prueba final con score=11
    print("\n🧪 Prueba final: Score=11")
    
    score = 11
    matched = None
    
    for policy in policies:
        conditions = policy.conditions
        matches = True
        
        if 'min_risk_score' in conditions:
            if score < conditions['min_risk_score']:
                matches = False
                
        if 'max_risk_score' in conditions:
            if score > conditions['max_risk_score']:
                matches = False
                
        if matches:
            matched = policy
            break
    
    if matched and matched.action == 'allow':
        print(f"✅ PERFECTO: Score=11 → {matched.name} → {matched.action.upper()}")
        print("   El sistema permitirá acceso directo (sin step-up)")
    else:
        print(f"❌ ERROR: Score=11 no resulta en 'allow'")
        if matched:
            print(f"   Política aplicada: {matched.name} → {matched.action}")
        all_correct = False
    
    print()
    return all_correct

def main():
    """Función principal."""
    
    parser = argparse.ArgumentParser(
        description='Diagnosticar y corregir políticas de step-up authentication'
    )
    parser.add_argument(
        '--diagnose',
        action='store_true',
        help='Solo diagnosticar (no corregir)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Diagnosticar y corregir automáticamente'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verificar que las políticas sean correctas'
    )
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna acción, mostrar ayuda
    if not (args.diagnose or args.fix or args.verify):
        parser.print_help()
        return
    
    # Conectar a la base de datos
    print("\n🔌 Conectando a la base de datos...")
    
    try:
        db = SessionLocal()
        print("✅ Conexión exitosa\n")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        print("\nVerifica que:")
        print("  • La base de datos esté accesible")
        print("  • Las credenciales sean correctas")
        print("  • El archivo .env esté configurado\n")
        return
    
    try:
        # Ejecutar acción solicitada
        if args.diagnose:
            policies_ok = diagnose_policies(db)
            
            if policies_ok:
                print("\n" + "="*70)
                print(" ✅ RESULTADO: Las políticas están CORRECTAS")
                print("="*70 + "\n")
                print("Si el problema persiste, puede estar en:")
                print("  • El frontend (componente StepUpChallenge)")
                print("  • El flujo de autenticación (app.py)")
                print("  • Variables de entorno incorrectas\n")
            else:
                print("\n" + "="*70)
                print(" ❌ RESULTADO: Las políticas están INCORRECTAS")
                print("="*70 + "\n")
                print("Para corregir, ejecuta:")
                print("  python fix_stepup_policies.py --fix\n")
        
        elif args.fix:
            policies_ok = diagnose_policies(db)
            
            if policies_ok:
                print("\n✅ Las políticas ya son correctas, no se necesita corrección.\n")
            else:
                confirm = input("\n¿Deseas corregir las políticas? (s/n): ")
                
                if confirm.lower() in ['s', 'si', 'y', 'yes']:
                    success = fix_policies(db)
                    
                    if success:
                        print("\n✅ Corrección completada")
                        print("\nPróximos pasos:")
                        print("  1. Reiniciar la aplicación en Render")
                        print("  2. Intentar autenticarse nuevamente")
                        print("  3. Verificar que NO pida step-up con score bajo\n")
                    else:
                        print("\n❌ La corrección falló. Revisa los errores anteriores.\n")
                else:
                    print("\n❌ Corrección cancelada.\n")
        
        elif args.verify:
            all_ok = verify_fix(db)
            
            if all_ok:
                print("="*70)
                print(" ✅ VERIFICACIÓN EXITOSA")
                print("="*70)
                print("\nTodas las políticas están configuradas correctamente.")
                print("El sistema debería comportarse según lo esperado.\n")
            else:
                print("="*70)
                print(" ❌ VERIFICACIÓN FALLIDA")
                print("="*70)
                print("\nAlgunas políticas no están configuradas correctamente.")
                print("Ejecuta 'python fix_stepup_policies.py --fix' para corregir.\n")
    
    finally:
        db.close()
        print("🔌 Conexión cerrada\n")

if __name__ == "__main__":
    main()
