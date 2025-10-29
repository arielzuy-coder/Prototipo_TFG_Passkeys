from typing import Dict, Any, Optional
from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session as DBSession
from models import User, Device, AuditEvent
import user_agents
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self):
        self.weights = {
            'device': 0.30,
            'location': 0.25,
            'time': 0.20,
            'failed_attempts': 0.15,
            'velocity': 0.10
        }
        
        self.business_hours_start = time(8, 0)
        self.business_hours_end = time(18, 0)
    
    def evaluate_risk(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        db: DBSession
    ) -> Dict[str, Any]:
        """Evalúa el riesgo contextual de un intento de autenticación."""
        
        context = self._build_context(user, ip_address, user_agent, db)
        
        factors = {
            'device': self._evaluate_device_risk(context, db),
            'location': self._evaluate_location_risk(context, user, db),
            'time': self._evaluate_time_risk(context),
            'failed_attempts': self._evaluate_failed_attempts(user, db),
            'velocity': self._evaluate_velocity_risk(user, db)
        }
        
        total_score = sum(
            factors[factor]['score'] * self.weights[factor]
            for factor in factors
        )
        
        risk_level = self._calculate_risk_level(total_score)
        
        return {
            'score': Decimal(str(round(total_score, 2))),
            'level': risk_level,
            'factors': factors,
            'context': context
        }
    
    def _build_context(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        db: DBSession
    ) -> Dict[str, Any]:
        """Construye el contexto del intento de autenticación."""
        
        ua = user_agents.parse(user_agent)
        
        location = self._get_location_from_ip(ip_address)
        
        return {
            'user_id': user.id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'browser': ua.browser.family,
            'os': ua.os.family,
            'device_type': 'mobile' if ua.is_mobile else 'desktop',
            'location': location,
            'timestamp': datetime.utcnow()
        }
    
    def _evaluate_device_risk(
        self,
        context: Dict,
        db: DBSession
    ) -> Dict[str, Any]:
        """Evalúa el riesgo basado en el dispositivo."""
        
        # Generar fingerprint usando user_agent en lugar de ip_address
        device_fingerprint = f"{context['browser']}_{context['os']}_{context['user_agent'][:50]}"
        
        # LOG DE DEBUG: Ver qué fingerprint está buscando
        logger.info(f"[RISK ENGINE] Buscando device_fingerprint: {device_fingerprint}")
        
        known_device = db.query(Device).filter(
            Device.device_fingerprint == device_fingerprint
        ).first()
        
        if known_device:
            logger.info(f"[RISK ENGINE] ✅ Dispositivo encontrado: {known_device.device_name}")
            return {
                'score': 0,
                'known': True,
                'message': f"Dispositivo conocido: {known_device.device_name}"
            }
        else:
            logger.info(f"[RISK ENGINE] ❌ Dispositivo NO encontrado en BD")
            return {
                'score': 40,
                'known': False,
                'message': "Dispositivo desconocido - primera vez"
            }
    
    def _evaluate_location_risk(
        self,
        context: Dict,
        user: User,
        db: DBSession
    ) -> Dict[str, Any]:
        """Evalúa el riesgo basado en la ubicación geográfica."""
        
        recent_locations = db.query(Device.last_seen_location).filter(
            Device.user_id == user.id
        ).distinct().all()
        
        recent_locations = [loc[0] for loc in recent_locations if loc[0]]
        
        current_location = context.get('location', 'Unknown')
        
        if not recent_locations:
            return {
                'score': 20,
                'known': False,
                'message': f"Primera ubicación registrada: {current_location}"
            }
        
        if current_location in recent_locations:
            return {
                'score': 0,
                'known': True,
                'message': f"Ubicación conocida: {current_location}"
            }
        else:
            return {
                'score': 35,
                'known': False,
                'message': f"Nueva ubicación: {current_location}"
            }
    
    def _evaluate_time_risk(self, context: Dict) -> Dict[str, Any]:
        """Evalúa el riesgo basado en el horario de acceso."""
        
        current_time = context['timestamp'].time()
        
        is_business_hours = (
            self.business_hours_start <= current_time <= self.business_hours_end
        )
        
        is_weekday = context['timestamp'].weekday() < 5
        
        if is_business_hours and is_weekday:
            return {
                'score': 0,
                'is_business_hours': True,
                'message': "Horario laboral (Lun-Vie 8-18hs)"
            }
        elif is_weekday:
            return {
                'score': 15,
                'is_business_hours': False,
                'message': "Fuera de horario laboral"
            }
        else:
            return {
                'score': 25,
                'is_business_hours': False,
                'message': "Acceso en fin de semana"
            }
    
    def _evaluate_failed_attempts(
        self,
        user: User,
        db: DBSession
    ) -> Dict[str, Any]:
        """Evalúa intentos fallidos recientes."""
        
        recent_failures = db.query(AuditEvent).filter(
            AuditEvent.user_id == user.id,
            AuditEvent.event_type == 'auth_failed',
            AuditEvent.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if recent_failures == 0:
            score = 0
            message = "Sin intentos fallidos recientes"
        elif recent_failures <= 2:
            score = 20
            message = f"{recent_failures} intentos fallidos en la última hora"
        else:
            score = 50
            message = f"ALERTA: {recent_failures} intentos fallidos recientes"
        
        return {
            'score': score,
            'count': recent_failures,
            'message': message
        }
    
    def _evaluate_velocity_risk(
        self,
        user: User,
        db: DBSession
    ) -> Dict[str, Any]:
        """Evalúa la velocidad de intentos de autenticación."""
        
        recent_attempts = db.query(AuditEvent).filter(
            AuditEvent.user_id == user.id,
            AuditEvent.event_type.in_(['auth_success', 'auth_failed']),
            AuditEvent.timestamp >= datetime.utcnow() - timedelta(minutes=5)
        ).count()
        
        if recent_attempts <= 2:
            return {
                'score': 0,
                'attempts': recent_attempts,
                'message': "Velocidad normal de autenticación"
            }
        elif recent_attempts <= 5:
            return {
                'score': 25,
                'attempts': recent_attempts,
                'message': f"Velocidad elevada: {recent_attempts} intentos en 5 min"
            }
        else:
            return {
                'score': 50,
                'attempts': recent_attempts,
                'message': f"ALERTA: Posible ataque - {recent_attempts} intentos en 5 min"
            }
    
    def _calculate_risk_level(self, score: float) -> str:
        """Calcula el nivel de riesgo según el score."""
        
        if score < 40:
            return 'low'
        elif score < 75:
            return 'medium'
        else:
            return 'high'
    
    def _get_location_from_ip(self, ip_address: str) -> str:
        """Obtiene la ubicación aproximada desde la IP."""
        
        if ip_address.startswith('127.') or ip_address == 'localhost':
            return 'Localhost (Desarrollo)'
        
        if ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            return 'Red Local'
        
        return f"IP: {ip_address}"
