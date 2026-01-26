#!/usr/bin/env python3
"""
Pump.fun Token Launch
Usage: python3 pumpfun.py launch --name "Token" --symbol "TKN" --image ./image.png [--buy 0.1]

Commands:
  launch    Launch a new token on pump.fun with optional dev buy
"""

import os
import sys
import asyncio
import argparse
import struct
import json
import mimetypes
from pathlib import Path
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple

try:
    import aiohttp
    import base58
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.instruction import Instruction, AccountMeta
    from solders.system_program import ID as SYSTEM_PROGRAM_ID
    from solders.transaction import VersionedTransaction
    from solders.message import MessageV0
    from solana.rpc.api import Client
    from solana.rpc.commitment import Confirmed
    from solana.rpc.types import TxOpts
    from spl.token.instructions import get_associated_token_address
except ImportError as e:
    print(f"Error: Required packages not installed. Missing: {e.name}")
    print("Run: pip install solana solders base58 aiohttp spl-token")
    sys.exit(1)


# Pump.fun constants
PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
PUMP_EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
TOKEN_2022_PROGRAM_ID = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
MAYHEM_PROGRAM_ID = Pubkey.from_string("MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e")

# Bonding curve constants
LAMPORTS_PER_SOL = 1_000_000_000
TOKEN_DECIMALS = 1_000_000  # 6 decimals
INITIAL_VIRTUAL_SOL = 30.0

# Discriminators
CREATE_V2_DISCRIMINATOR = bytes([214, 144, 76, 236, 95, 139, 49, 180])
BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")

# RPC
NETWORKS = {
    "mainnet": "https://api.mainnet-beta.solana.com",
    "devnet": "https://api.devnet.solana.com",
}


def get_keypair() -> Keypair:
    """Load keypair from environment variable."""
    private_key = os.environ.get("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("Error: SOLANA_PRIVATE_KEY environment variable not set.")
        sys.exit(1)
    try:
        key_bytes = base58.b58decode(private_key)
        return Keypair.from_bytes(key_bytes)
    except Exception as e:
        print(f"Error: Invalid private key format: {e}")
        sys.exit(1)


def get_client(network: str = "mainnet") -> Client:
    """Get Solana RPC client."""
    rpc_url = os.environ.get("SOLANA_RPC_URL") or NETWORKS.get(network, NETWORKS["mainnet"])
    return Client(rpc_url)


def derive_mint_authority() -> Pubkey:
    """Derive mint authority PDA."""
    pda, _ = Pubkey.find_program_address([b"mint-authority"], PUMP_PROGRAM_ID)
    return pda


def derive_bonding_curve(mint: Pubkey) -> Pubkey:
    """Derive bonding curve PDA."""
    pda, _ = Pubkey.find_program_address([b"bonding-curve", bytes(mint)], PUMP_PROGRAM_ID)
    return pda


def derive_associated_bonding_curve(bonding_curve: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive associated bonding curve (ATA for Token-2022)."""
    pda, _ = Pubkey.find_program_address(
        [bytes(bonding_curve), bytes(TOKEN_2022_PROGRAM_ID), bytes(mint)],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )
    return pda


def derive_event_authority() -> Pubkey:
    """Derive event authority PDA."""
    pda, _ = Pubkey.find_program_address([b"__event_authority"], PUMP_PROGRAM_ID)
    return pda


def derive_global_params() -> Pubkey:
    """Derive global params PDA from Mayhem program."""
    pda, _ = Pubkey.find_program_address([b"global-params"], MAYHEM_PROGRAM_ID)
    return pda


def derive_sol_vault() -> Pubkey:
    """Derive SOL vault PDA from Mayhem program."""
    pda, _ = Pubkey.find_program_address([b"sol-vault"], MAYHEM_PROGRAM_ID)
    return pda


def derive_mayhem_state(mint: Pubkey) -> Pubkey:
    """Derive mayhem state PDA."""
    pda, _ = Pubkey.find_program_address([b"mayhem-state", bytes(mint)], MAYHEM_PROGRAM_ID)
    return pda


def derive_mayhem_token_vault(mayhem_state: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive mayhem token vault ATA."""
    pda, _ = Pubkey.find_program_address(
        [bytes(mayhem_state), bytes(TOKEN_2022_PROGRAM_ID), bytes(mint)],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )
    return pda


def derive_user_ata(user: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive user's ATA for Token-2022."""
    pda, _ = Pubkey.find_program_address(
        [bytes(user), bytes(TOKEN_2022_PROGRAM_ID), bytes(mint)],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )
    return pda


def derive_creator_vault(creator: Pubkey) -> Pubkey:
    """Derive creator vault PDA."""
    pda, _ = Pubkey.find_program_address([b"creator-vault", bytes(creator)], PUMP_PROGRAM_ID)
    return pda


def derive_global_volume_accumulator() -> Pubkey:
    """Return global volume accumulator address."""
    return Pubkey.from_string("Hq2wp8uJ9jCPsYgNHex8RtqdvMPfVGoYwjvF1ATiwn2Y")


def derive_user_volume_accumulator(user: Pubkey) -> Pubkey:
    """Derive user volume accumulator PDA."""
    pda, _ = Pubkey.find_program_address([b"user_volume_accumulator", bytes(user)], PUMP_PROGRAM_ID)
    return pda


def derive_fee_config() -> Pubkey:
    """Return fee config address."""
    return Pubkey.from_string("8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt")


def derive_fee_program() -> Pubkey:
    """Return fee program address."""
    return Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")


def encode_string(s: str) -> bytes:
    """Encode string with length prefix (Borsh format)."""
    encoded = s.encode('utf-8')
    return struct.pack('<I', len(encoded)) + encoded


def create_create_v2_instruction(
    mint: Pubkey,
    user: Pubkey,
    name: str,
    symbol: str,
    uri: str,
    is_mayhem_mode: bool = False
) -> Instruction:
    """Create the createV2 instruction."""
    bonding_curve = derive_bonding_curve(mint)
    associated_bonding_curve = derive_associated_bonding_curve(bonding_curve, mint)
    mayhem_state = derive_mayhem_state(mint)
    mayhem_token_vault = derive_mayhem_token_vault(mayhem_state, mint)
    
    accounts = [
        AccountMeta(pubkey=mint, is_signer=True, is_writable=True),
        AccountMeta(pubkey=derive_mint_authority(), is_signer=False, is_writable=False),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=PUMP_GLOBAL, is_signer=False, is_writable=False),
        AccountMeta(pubkey=user, is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_2022_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=MAYHEM_PROGRAM_ID, is_signer=False, is_writable=True),
        AccountMeta(pubkey=derive_global_params(), is_signer=False, is_writable=False),
        AccountMeta(pubkey=derive_sol_vault(), is_signer=False, is_writable=True),
        AccountMeta(pubkey=mayhem_state, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mayhem_token_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=derive_event_authority(), is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    # Build instruction data
    data = bytearray()
    data.extend(CREATE_V2_DISCRIMINATOR)
    data.extend(encode_string(name))
    data.extend(encode_string(symbol))
    data.extend(encode_string(uri))
    data.extend(bytes(user))  # creator pubkey
    data.append(1 if is_mayhem_mode else 0)  # is_mayhem_mode bool
    
    return Instruction(PUMP_PROGRAM_ID, bytes(data), accounts)


def create_ata_instruction(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey
) -> Instruction:
    """Create ATA instruction for Token-2022."""
    ata = derive_user_ata(owner, mint)
    
    accounts = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_2022_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    return Instruction(ASSOCIATED_TOKEN_PROGRAM_ID, bytes(), accounts)


def create_buy_instruction(
    user: Keypair,
    mint: Pubkey,
    amount: int,
    max_sol_cost: int
) -> Instruction:
    """Create buy instruction for dev buy."""
    bonding_curve = derive_bonding_curve(mint)
    associated_bonding_curve = derive_associated_bonding_curve(bonding_curve, mint)
    user_ata = derive_user_ata(user.pubkey(), mint)
    creator_vault = derive_creator_vault(user.pubkey())
    
    accounts = [
        AccountMeta(pubkey=PUMP_GLOBAL, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_FEE_RECIPIENT, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user_ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user.pubkey(), is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_2022_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=creator_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=PUMP_EVENT_AUTHORITY, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=derive_global_volume_accumulator(), is_signer=False, is_writable=True),
        AccountMeta(pubkey=derive_user_volume_accumulator(user.pubkey()), is_signer=False, is_writable=True),
        AccountMeta(pubkey=derive_fee_config(), is_signer=False, is_writable=False),
        AccountMeta(pubkey=derive_fee_program(), is_signer=False, is_writable=False),
    ]
    
    # Build instruction data
    data = bytearray()
    data.extend(BUY_DISCRIMINATOR)
    data.extend(struct.pack('<Q', amount))  # token amount
    data.extend(struct.pack('<Q', max_sol_cost))  # max SOL cost
    
    return Instruction(PUMP_PROGRAM_ID, bytes(data), accounts)


async def upload_to_ipfs(image_path: str, name: str, symbol: str, description: str) -> str:
    """
    Upload image and metadata to IPFS via pump.fun API.
    Returns the metadata URI.
    """
    print("◎ Uploading to IPFS...")
    
    # Read image file
    image_path = Path(image_path)
    if not image_path.exists():
        raise Exception(f"Image file not found: {image_path}")
    
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith('image/'):
        raise Exception(f"Invalid image file type: {mime_type}")
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Get presign URL for image
        print("  Getting presign URL for image...")
        async with session.get("https://pump.fun/api/ipfs-presign") as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get presign URL: {await resp.text()}")
            presign_data = await resp.json()
            image_upload_url = presign_data["data"]
        
        # Step 2: Upload image
        print(f"  Uploading image ({image_path.name})...")
        form = aiohttp.FormData()
        form.add_field('file', image_data, filename=image_path.name, content_type=mime_type)
        form.add_field('network', 'public')
        form.add_field('name', image_path.name)
        
        async with session.post(image_upload_url, data=form, headers={"source": "sdk/file"}) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to upload image: {await resp.text()}")
            image_result = await resp.json()
            image_cid = image_result["data"]["cid"]
            image_ipfs_url = f"https://ipfs.io/ipfs/{image_cid}"
        
        print(f"  Image uploaded: {image_ipfs_url}")
        
        # Step 3: Get presign URL for metadata
        print("  Getting presign URL for metadata...")
        async with session.get("https://pump.fun/api/ipfs-presign") as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get presign URL: {await resp.text()}")
            presign_data = await resp.json()
            metadata_upload_url = presign_data["data"]
        
        # Step 4: Upload metadata JSON
        print("  Uploading metadata...")
        metadata = {
            "name": name,
            "symbol": symbol,
            "description": description,
            "image": image_ipfs_url,
            "showName": True,
            "createdOn": "https://pump.fun"
        }
        metadata_json = json.dumps(metadata)
        
        form = aiohttp.FormData()
        form.add_field('file', metadata_json, filename='data.json', content_type='application/json')
        form.add_field('network', 'public')
        form.add_field('name', 'data.json')
        
        async with session.post(metadata_upload_url, data=form) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to upload metadata: {await resp.text()}")
            metadata_result = await resp.json()
            metadata_cid = metadata_result["data"]["cid"]
            metadata_uri = f"https://ipfs.io/ipfs/{metadata_cid}"
        
        print(f"  Metadata uploaded: {metadata_uri}")
        
    return metadata_uri


def calculate_tokens_for_sol(sol_amount: float) -> int:
    """Calculate expected tokens for SOL amount at initial curve state."""
    # At initial state: virtual_sol = 30, k = 32190005730 * 10^6
    k = 32190005730 * TOKEN_DECIMALS
    initial_tokens = 1073000191 * TOKEN_DECIMALS
    
    current_tokens = initial_tokens - (k / INITIAL_VIRTUAL_SOL)
    new_virtual_sol = INITIAL_VIRTUAL_SOL + sol_amount
    new_tokens = initial_tokens - (k / new_virtual_sol)
    tokens_received = new_tokens - current_tokens
    
    return int(max(0, tokens_received))


def cmd_launch(args):
    """Launch a new token on pump.fun."""
    keypair = get_keypair()
    client = get_client(args.network)
    
    print(f"◎ Pump.fun Token Launch")
    print(f"  Creator: {keypair.pubkey()}")
    print(f"  Name: {args.name}")
    print(f"  Symbol: {args.symbol}")
    print(f"  Image: {args.image}")
    if args.buy:
        print(f"  Dev buy: {args.buy} SOL")
    
    # Upload to IPFS
    try:
        metadata_uri = asyncio.run(upload_to_ipfs(
            args.image,
            args.name,
            args.symbol,
            args.description or ""
        ))
    except Exception as e:
        print(f"\n❌ IPFS upload failed: {e}")
        sys.exit(1)
    
    # Use provided mint key or generate random
    if args.mint_key:
        try:
            mint_keypair = Keypair.from_base58_string(args.mint_key)
            print(f"\n◎ Using custom mint: {mint_keypair.pubkey()}")
        except Exception as e:
            print(f"\n❌ Invalid mint key: {e}")
            sys.exit(1)
    else:
        mint_keypair = Keypair()
        print(f"\n◎ Generated mint: {mint_keypair.pubkey()}")
    
    mint = mint_keypair.pubkey()
    
    # Build instructions
    instructions = []
    
    # Create token instruction
    create_ix = create_create_v2_instruction(
        mint=mint,
        user=keypair.pubkey(),
        name=args.name,
        symbol=args.symbol,
        uri=metadata_uri,
        is_mayhem_mode=False
    )
    instructions.append(create_ix)
    
    # Optional dev buy
    if args.buy and args.buy > 0:
        sol_amount = float(args.buy)
        tokens_expected = calculate_tokens_for_sol(sol_amount)
        max_sol_lamports = int(sol_amount * 1.1 * LAMPORTS_PER_SOL)  # 10% slippage
        
        # Create user's ATA first (required before buy)
        ata_ix = create_ata_instruction(
            payer=keypair.pubkey(),
            owner=keypair.pubkey(),
            mint=mint
        )
        instructions.append(ata_ix)
        
        buy_ix = create_buy_instruction(
            user=keypair,
            mint=mint,
            amount=tokens_expected,
            max_sol_cost=max_sol_lamports
        )
        instructions.append(buy_ix)
        print(f"  Expected tokens: {tokens_expected / TOKEN_DECIMALS:,.0f}")
    
    # Build and send transaction
    print("\n◎ Sending transaction...")
    
    try:
        blockhash_resp = client.get_latest_blockhash(commitment=Confirmed)
        recent_blockhash = blockhash_resp.value.blockhash
        
        msg = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash,
        )
        
        # Sign with both keypairs
        signers = [keypair, mint_keypair]
        tx = VersionedTransaction(msg, signers)
        
        opts = TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
        result = client.send_transaction(tx, opts=opts)
        signature = result.value
        
        print(f"\n✅ Token launched!")
        print(f"◎ Mint: {mint}")
        print(f"◎ Signature: {signature}")
        print(f"◎ Pump.fun: https://pump.fun/coin/{mint}")
        print(f"◎ Explorer: https://solscan.io/tx/{signature}")
        
    except Exception as e:
        print(f"\n❌ Transaction failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Pump.fun Token Launch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pumpfun.py launch --name "My Token" --symbol "MTK" --image ./logo.png
  pumpfun.py launch --name "My Token" --symbol "MTK" --image ./logo.png --buy 0.5
  pumpfun.py launch --name "My Token" --symbol "MTK" --image ./logo.png --mint-key <base58_key>

Use --mint-key with a vanity address ending in 'pump' for more legit-looking tokens.
Generate vanity keys with tools like solana-keygen grind.

Environment variables (required):
  SOLANA_PRIVATE_KEY    Base58 private key
  SOLANA_RPC_URL        Custom RPC endpoint (optional, for faster execution)
        """
    )
    
    parser.add_argument(
        "--network", "-n",
        choices=["mainnet", "devnet"],
        default="mainnet",
        help="Solana network (default: mainnet)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # launch command
    launch_parser = subparsers.add_parser("launch", help="Launch a new token")
    launch_parser.add_argument("--name", required=True, help="Token name")
    launch_parser.add_argument("--symbol", required=True, help="Token symbol")
    launch_parser.add_argument("--image", required=True, help="Path to token image")
    launch_parser.add_argument("--description", "-d", default="", help="Token description")
    launch_parser.add_argument("--buy", "-b", type=float, help="Dev buy amount in SOL (optional)")
    launch_parser.add_argument("--mint-key", "-m", help="Base58 private key for mint (for vanity addresses ending with 'pump')")
    launch_parser.set_defaults(func=cmd_launch)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
