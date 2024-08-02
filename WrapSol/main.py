import asyncio
from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionInstruction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.system_program import SYS_PROGRAM_ID
from spl.token.instructions import TransferCheckedParams, transfer_checked
from spl.token.constants import TOKEN_PROGRAM_ID
from pyserum.market import Market
from pyserum.connection import conn

solana_client = Client("https://api.mainnet-beta.solana.com")
wallet = "2jtw6dA7QJBfRKGKqVPDLicVvSq1W2EHEgP5hfSzK6QMSdNgW1z3va5eYsg8cb2wRowjtJcVPha2hSaxLmtViPJH"
destination_wallet = PublicKey("8bRMeNz8wffa8RBcBWPTDpwP7QR4taawK5L8bPkAX8kq")

def swap_tokens(from_token_pubkey, to_token_pubkey, amount, fee_percentage, fee_wallet_pubkey):
    # Load market
    connection = conn("https://api.devnet.solana.com")
    market_address = PublicKey("market_address")
    market = Market.load(connection, market_address)

    # Calculate fee
    fee = amount * fee_percentage
    net_amount = amount - fee

    # Create transactions
    transaction = Transaction()
    
    # Transfer tokens to fee wallet
    fee_transfer = transfer_checked(
        TransferCheckedParams(
            program_id=TOKEN_PROGRAM_ID,
            source=from_token_pubkey,
            mint=from_token_pubkey,
            dest=fee_wallet_pubkey,
            owner=wallet.public_key(),
            amount=fee,
            decimals=9  # Number of decimal places for the token
        )
    )
    
    # Transfer net amount to swap pool
    swap_transfer = transfer_checked(
        TransferCheckedParams(
            program_id=TOKEN_PROGRAM_ID,
            source=from_token_pubkey,
            mint=from_token_pubkey,
            dest=market_address,
            owner=wallet.public_key(),
            amount=net_amount,
            decimals=9
        )
    )

    transaction.add(fee_transfer)
    transaction.add(swap_transfer)

    # Send transaction
    response = solana_client.send_transaction(transaction, wallet, opts=TxOpts(skip_confirmation=False))
    return response


async def main():
    from_token_pubkey = "So11111111111111111111111111111111111111112"
    to_token_pubkey = "ABnabotWUvmDFCpmsUCv1EcmaAEc3ZoaTZiDvvngRAHV"
    amount = 1000
    fee_percentage = 0.01
    fee_wallet_pubkey = "8bRMeNz8wffa8RBcBWPTDpwP7QR4taawK5L8bPkAX8kq"
    
    await swap_tokens(from_token_pubkey, to_token_pubkey, amount, fee_percentage, fee_wallet_pubkey)


asyncio.run(main())