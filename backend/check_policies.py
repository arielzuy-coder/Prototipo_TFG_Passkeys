"""
Script de diagnóstico para verificar políticas de riesgo en la base de datos.
Ejecutar desde el directorio backend: python check_policies.py
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Policy
from config import SessionLocal

def check_policies():
    """Verifica las políticas activas en la base de datos."""
    
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("🔍 DIAGNÓSTICO DE POLÍTICAS DE RIESGO")
        print("="*70 + "\n")
        
        # Consultar políticas activas
        policies = db.query(Policy).filter(Policy.enabled == True).order_by(Policy.priority.asc()).all()
        
        print(f"📊 Total de políticas activas: {len(policies)}\n")
        
        if not policies:
            print("⚠️  NO HAY POLÍTICAS EN LA BASE DE DATOS")
            print("   El sistema debería crear políticas por defecto automáticamente.\n")
            print("🔧 Políticas por defecto esperadas:")
            print("   1. high_risk_deny (score ≥ 75) → DENY")
            print("   2. medium_risk_stepup (score 40-74) → STEPUP")
            print("   3. low_risk_allow (score ≤ 39) → ALLOW\n")
        else:
            print("📋 POLÍTICAS ENCONTRADAS:\n")
            
            for i, p in enumerate(policies, 1):
                print(f"--- Política {i} ---")
                print(f"  Nombre: {p.name}")
                print(f"  Descripción: {p.description}")
                print(f"  Condiciones: {p.conditions}")
                print(f"  Acción: {p.action}")
                print(f"  Prioridad: {p.priority}")
                print(f"  Habilitada: {p.enabled}")
                print()
                
                # Análisis de la política
                conditions = p.conditions
                if 'min_risk_score' in conditions and 'max_risk_score' in conditions:
                    print(f"  📊 Rango: {conditions['min_risk_score']} - {conditions['max_risk_score']}")
                elif 'min_risk_score' in conditions:
                    print(f"  📊 Mínimo: {conditions['min_risk_score']} (sin máximo)")
                elif 'max_risk_score' in conditions:
                    print(f"  📊 Máximo: {conditions['max_risk_score']} (sin mínimo)")
                    
                print("-" * 50 + "\n")
        
        # Análisis del problema reportado
        print("\n" + "="*70)
        print("🐛 ANÁLISIS DEL PROBLEMA REPORTADO")
        print("="*70 + "\n")
        
        print("Situación:")
        print("  • Score de riesgo detectado: 11/100")
        print("  • Nivel: LOW")
        print("  • Comportamiento actual: Pide STEP-UP")
        print("  • Comportamiento esperado: Debería PERMITIR acceso directamente\n")
        
        print("Verificación de políticas:")
        
        score_test = 11
        matched_policy = None
        
        for p in policies:
            conditions = p.conditions
            matches = True
            
            if 'min_risk_score' in conditions:
                if score_test < conditions['min_risk_score']:
                    matches = False
                    
            if 'max_risk_score' in conditions:
                if score_test > conditions['max_risk_score']:
                    matches = False
                    
            if matches:
                matched_policy = p
                break
        
        if matched_policy:
            print(f"  ✅ Política que debería aplicarse: {matched_policy.name}")
            print(f"  ⚙️  Acción configurada: {matched_policy.action.upper()}")
            
            if matched_policy.action == 'allow':
                print("  ✅ ¡CORRECTO! La política permite el acceso directo.")
            elif matched_policy.action == 'stepup':
                print("  ❌ ¡ERROR! La política pide step-up cuando NO debería.")
                print("     Con score de 11, debería ser 'allow', no 'stepup'.")
            elif matched_policy.action == 'deny':
                print("  ❌ ¡ERROR CRÍTICO! La política deniega el acceso.")
        else:
            print("  ⚠️  Ninguna política matchea con score=11")
            print("     Esto causaría que se use la política por defecto (allow)")
        
        # Recomendaciones
        print("\n" + "="*70)
        print("💡 RECOMENDACIONES")
        print("="*70 + "\n")
        
        if not policies:
            print("1. Reiniciar la aplicación para que cree las políticas por defecto")
            print("2. O ejecutar el script reset_policies.sql\n")
        elif matched_policy and matched_policy.action != 'allow':
            print("1. Ejecutar el script reset_policies.sql para resetear las políticas")
            print("2. Verificar que no hay políticas personalizadas incorrectas")
            print("3. Revisar los logs del backend para ver qué política se está aplicando\n")
        else:
            print("Las políticas parecen correctas. El problema podría estar en:")
            print("1. La lógica de evaluación de políticas")
            print("2. El contexto enviado al motor de riesgo")
            print("3. Variables de entorno en Render\n")
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error al consultar la base de datos: {str(e)}\n")
        print("Verifica que:")
        print("  • La base de datos esté accesible")
        print("  • Las credenciales sean correctas")
        print("  • La tabla 'policies' exista\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_policies()
