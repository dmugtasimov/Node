from node.core.exceptions import ValidationError

from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest


class CoinTransferSignedChangeRequest(SignedChangeRequest):
    message: CoinTransferSignedChangeRequestMessage

    def validate_business_logic(self):
        super().validate_business_logic()
        self.validate_circular_transactions()

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        self.validate_amount()

    def validate_circular_transactions(self):
        recipients = (tx.recipient for tx in self.message.txs)
        if self.signer in recipients:
            raise ValidationError('Circular transactions detected')

    def validate_amount(self):
        from node.blockchain.facade import BlockchainFacade
        blockchain_facade = BlockchainFacade.get_instance()

        if blockchain_facade.get_account_balance(self.signer) < self.message.get_total_amount():
            raise ValidationError('Signer balance mast be greater than total amount')
