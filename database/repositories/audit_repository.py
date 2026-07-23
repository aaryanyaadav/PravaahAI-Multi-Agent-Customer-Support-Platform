from sqlalchemy import text
from database.connections import SessionLocal
class AuditRepository:
    def log_action(
        self,
        account_id: str,
        action_type: str,
        agent: str,
        payload: dict
    ):
        with SessionLocal() as session:

            session.execute(
                text(
                    """
                    INSERT INTO audit_log
                    (
                        account_id,
                        action_type,
                        agent,
                        payload
                    )
                    VALUES
                    (
                        :account_id,
                        :action_type,
                        :agent,
                        CAST(:payload AS JSONB)
                    )
                    """
                ),
                {
                    "account_id": account_id,
                    "action_type": action_type,
                    "agent": agent,
                    "payload": str(payload)
                }
            )
            session.commit()