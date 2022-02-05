from pydantic import Field

from node.blockchain.inner_models import AccountState
from node.blockchain.inner_models.signed_change_request import CoinTransferSignedChangeRequest
from node.core.exceptions import ValidationError

from ...types import AccountNumber, Type
from .base import BlockMessage, BlockMessageUpdate


class CoinTransferBlockMessage(BlockMessage):
    type: Type = Field(default=Type.COIN_TRANSFER, const=True)  # noqa: A003
    request: CoinTransferSignedChangeRequest

    @classmethod
    def make_block_message_update(cls, request: CoinTransferSignedChangeRequest) -> BlockMessageUpdate:
        return BlockMessageUpdate(
            accounts={
                **cls._make_sender_account_state(request),
                **cls._make_recipients_account_states(request),
            }
        )

    @classmethod
    def _make_sender_account_state(cls, request) -> dict[AccountNumber, AccountState]:
        from node.blockchain.facade import BlockchainFacade

        sender_account = request.signer
        sender_balance = BlockchainFacade.get_instance().get_account_balance(sender_account)
        if (amount := sum(tx.amount for tx in request.message.txs)) > sender_balance:
            raise ValidationError(f'Sender account {sender_account} balance is not enough to send {amount} coins')

        return {sender_account: AccountState(balance=sender_balance - amount, account_lock=request.make_hash())}

    @classmethod
    def _make_recipients_account_states(cls, request) -> dict[AccountNumber, AccountState]:
        from node.blockchain.facade import BlockchainFacade
        blockchain_facade = BlockchainFacade.get_instance()

        updated_amounts: dict[AccountNumber, int] = {}
        for transaction in request.message.txs:
            if (recipient := transaction.recipient) not in updated_amounts:
                updated_amounts[recipient] = blockchain_facade.get_account_balance(recipient)
            updated_amounts[recipient] += transaction.amount

        updated_account_states = {
            account_number: AccountState(balance=amount) for account_number, amount in updated_amounts.items()
        }
        return updated_account_states

    def validate_business_logic(self):
        super().validate_business_logic()
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-217

    def validate_blockchain_state_dependent(self, blockchain_facade):
        super().validate_blockchain_state_dependent(blockchain_facade)
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-217
