from .base_sentinel import BaseSentinel
import logging
from web3 import Web3
import os

logger = logging.getLogger(__name__)

RPC_URL = os.getenv('RPC_URL')
w3 = Web3(Web3.HTTPProvider(RPC_URL))

class WalletDrainSentinel(BaseSentinel):
    def __init__(self):
        super().__init__()
        self.name = "wallet-drain-sentinel"

    async def analyze(self, data: dict) -> dict:
        try:
            safewallet = data.get("safewallet")
            transactions = data.get("transactions", [])
            
            if not safewallet:
                return {
                    "status": "error",
                    "message": "No safewallet provided"
                }

            current_balance = await self.get_native_balance(safewallet)
            
            for tx in transactions:
                value = self.parse_value(tx.get("value", "0"))
                
                if value > current_balance * 0.99 and value > 0:
                    return {
                        "status": "warning",
                        "message": f"⚠️ Possible wallet drain detected! Transaction uses all native balance ({value} wei)",
                        "current_balance": str(current_balance),
                        "tx_value": str(value)
                    }
            
            return {
                "status": "success",
                "message": "Analysis completed successfully"
            }
        except Exception as e:
            logger.error(f"Error analyzing in {self.name}: {e}")
            return {"status": "error", "message": str(e)}

    async def get_native_balance(self, address: str) -> int:
        try:
            if not w3.is_address(address):
                logger.error(f"❌ Invalid address: {address}")
                return 0
                
            balance = w3.eth.get_balance(address)
            return balance
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return 0

    def parse_value(self, value_str):
        try:
            clean_value = value_str.split('.')[0]
            
            if clean_value.startswith("0x"):
                return int(clean_value, 16)
            else:
                return int(clean_value)
        except Exception as e:
            logger.error(f"Error parsing value {value_str}: {e}")
            return 0