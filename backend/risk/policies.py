from typing import Dict, Any, List
from sqlalchemy.orm import Session as DBSession
from models import User, Policy
from decimal import Decimal

class PolicyEngine:
    def __init__(self):
        self.default_policies = [
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
    
    def evaluate_policies(
        self,
        user: User,
        risk_score: Decimal,
        context: Dict[str, Any],
        db: DBSession
    ) -> Dict[str, Any]:
        """Evalúa las políticas aplicables y retorna la acción a tomar."""
        
        policies = db.query(Policy).filter(
            Policy.enabled == True
        ).order_by(Policy.priority.asc()).all()
        
        if not policies:
            policies = self._create_default_policies(db)
        
        risk_score_float = float(risk_score)
        
        for policy in policies:
            if self._policy_matches(policy, risk_score_float, context):
                return {
                    'action': policy.action,
                    'policy_name': policy.name,
                    'policy_description': policy.description,
                    'matched': True
                }
        
        return {
            'action': 'allow',
            'policy_name': 'default',
            'policy_description': 'Política por defecto',
            'matched': False
        }
    
    def _policy_matches(
        self,
        policy: Policy,
        risk_score: float,
        context: Dict[str, Any]
    ) -> bool:
        """Verifica si una política coincide con el contexto actual."""
        
        conditions = policy.conditions
        
        if 'min_risk_score' in conditions:
            if risk_score < conditions['min_risk_score']:
                return False
        
        if 'max_risk_score' in conditions:
            if risk_score > conditions['max_risk_score']:
                return False
        
        if 'required_location' in conditions:
            if context.get('location') != conditions['required_location']:
                return False
        
        if 'allowed_devices' in conditions:
            if context.get('device_type') not in conditions['allowed_devices']:
                return False
        
        if 'business_hours_only' in conditions and conditions['business_hours_only']:
            if not context.get('is_business_hours', False):
                return False
        
        return True
    
    def _create_default_policies(self, db: DBSession) -> List[Policy]:
        """Crea políticas por defecto en la base de datos."""
        
        policies = []
        
        for policy_data in self.default_policies:
            policy = Policy(
                name=policy_data['name'],
                description=policy_data['description'],
                conditions=policy_data['conditions'],
                action=policy_data['action'],
                priority=policy_data['priority'],
                enabled=True
            )
            db.add(policy)
            policies.append(policy)
        
        db.commit()
        
        return policies
    
    def create_custom_policy(
        self,
        name: str,
        description: str,
        conditions: Dict[str, Any],
        action: str,
        priority: int,
        db: DBSession
    ) -> Policy:
        """Crea una política personalizada."""
        
        policy = Policy(
            name=name,
            description=description,
            conditions=conditions,
            action=action,
            priority=priority,
            enabled=True
        )
        
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        return policy
    
    def update_policy(
        self,
        policy_id: str,
        updates: Dict[str, Any],
        db: DBSession
    ) -> Policy:
        """Actualiza una política existente."""
        
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        
        if not policy:
            raise ValueError(f"Política {policy_id} no encontrada")
        
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        db.commit()
        db.refresh(policy)
        
        return policy
    
    def delete_policy(self, policy_id: str, db: DBSession) -> bool:
        """Elimina una política."""
        
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        
        if not policy:
            return False
        
        db.delete(policy)
        db.commit()
        
        return True