"""
Script de inicialización de base de datos para producción en Render
"""
from sqlalchemy import create_engine, text
from models import Base
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa la base de datos creando tablas y datos iniciales"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # Crear todas las tablas
        logger.info("Creando tablas de base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente")
        
        # Verificar si ya existen políticas
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM policies"))
            count = result.scalar()
            
            if count == 0:
                logger.info("Insertando políticas por defecto...")
                
                # Insertar políticas por defecto
                policies_sql = """
                INSERT INTO policies (name, description, conditions, action, priority, enabled, created_at, updated_at)
                VALUES 
                    ('high_risk_deny', 'Denegar acceso cuando riesgo es alto', 
                     '{"min_risk_score": 75}', 'deny', 1, true, NOW(), NOW()),
                    
                    ('medium_risk_stepup', 'Requerir verificación adicional para riesgo medio', 
                     '{"min_risk_score": 40, "max_risk_score": 74}', 'stepup', 2, true, NOW(), NOW()),
                    
                    ('new_device_stepup', 'Verificar dispositivos nuevos o desconocidos', 
                     '{"new_device": true}', 'stepup', 3, true, NOW(), NOW()),
                    
                    ('unusual_location_stepup', 'Verificar accesos desde ubicaciones inusuales', 
                     '{"unusual_location": true}', 'stepup', 4, true, NOW(), NOW()),
                    
                    ('low_risk_allow', 'Permitir acceso directo para riesgo bajo', 
                     '{"max_risk_score": 39}', 'allow', 5, true, NOW(), NOW());
                """
                conn.execute(text(policies_sql))
                conn.commit()
                logger.info("✅ Políticas por defecto insertadas")
            else:
                logger.info(f"Base de datos ya tiene {count} políticas, omitiendo inserción")
        
        logger.info("✅ Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise

if __name__ == "__main__":
    init_database()
