from sqlalchemy.orm import Session
from app.models.cognitive import PromptMapping
from app.models.automation import SystemPrompt
from datetime import datetime
import json
import uuid

class CognitiveService:
    @staticmethod
    async def learn_mapping(db: Session, prompt: str, stage: str, tags: list = None):
        # Normalize prompt for basic matching (lowercase, stripped)
        norm_prompt = prompt.lower().strip()
        
        mapping = db.query(PromptMapping).filter(
            PromptMapping.user_prompt == norm_prompt,
            PromptMapping.predicted_stage == stage
        ).first()

        if mapping:
            mapping.usage_count += 1
            mapping.success_score += 0.5
            mapping.last_used = datetime.utcnow()
        else:
            mapping = PromptMapping(
                user_prompt=norm_prompt,
                predicted_stage=stage,
                context_tags=tags or [],
                success_score=1.0,
                usage_count=1
            )
            db.add(mapping)
        
        # NEURAL PROMOTION: If this pattern is strong, promote it to a System Template
        if mapping.success_score >= 5.0:
            existing_template = db.query(SystemPrompt).filter(SystemPrompt.content == prompt).first()
            if not existing_template:
                new_template = SystemPrompt(
                    id=str(uuid.uuid4()),
                    name=f"Learned Path: {stage.upper()}",
                    content=prompt,
                    description=f"Neuraly promoted pattern based on {mapping.usage_count} successful deployments."
                )
                db.add(new_template)
        
        db.commit()
        return mapping

    @staticmethod
    async def get_recommendations(db: Session, current_prompt: str, limit: int = 3):
        norm_prompt = current_prompt.lower().strip()
        
        # Simple similarity: Contains or starts with
        mappings = db.query(PromptMapping).filter(
            PromptMapping.user_prompt.contains(norm_prompt)
        ).order_by(PromptMapping.success_score.desc()).limit(limit).all()

        return [
            {
                "stage": m.predicted_stage,
                "score": m.success_score,
                "confidence": min(100, (m.usage_count * 10))
            } for m in mappings
        ]

    @staticmethod
    async def get_next_logical_stages(db: Session, last_stage: str):
        # This builds a chain: "What usually comes after X?"
        # We look for prompts that contain the last_stage and see what they mapped to
        mappings = db.query(PromptMapping).filter(
            PromptMapping.user_prompt.contains(last_stage.lower())
        ).order_by(PromptMapping.success_score.desc()).limit(3).all()
        
        return [m.predicted_stage for m in mappings if m.predicted_stage != last_stage]
