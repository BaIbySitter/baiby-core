from typing import Dict
import asyncio

class WarningManager:
    def __init__(self):
        self.warnings: Dict[str, dict] = {}

    async def process_warning(self, data: dict):
        tx_hash = data.get("transaction_hash")
        if tx_hash:
            self.warnings[tx_hash] = data
            # Notify the transaction that is waiting
            from app.routes import active_transactions
            event = active_transactions.get(tx_hash)
            if event:
                event.set()

    def get_warning(self, tx_hash: str) -> dict:
        return self.warnings.get(tx_hash)

    def clear_warning(self, tx_hash: str):
        self.warnings.pop(tx_hash, None)

warning_manager = WarningManager() 