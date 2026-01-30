# Sage RPC Endpoints Quick Reference

All 112 endpoints organized by category.

## Authentication & Keys (16)
| Endpoint | Description |
|----------|-------------|
| `login` | Login with fingerprint |
| `logout` | End session |
| `generate_mnemonic` | Generate 12/24-word mnemonic |
| `import_key` | Import wallet |
| `delete_key` | Delete wallet key |
| `rename_key` | Rename wallet |
| `set_wallet_emoji` | Set emoji |
| `get_keys` | List all keys |
| `get_key` | Get specific key |
| `get_secret_key` | Get mnemonic |
| `resync` | Resync wallet |
| `delete_database` | Delete wallet DB |
| `get_user_themes` | List themes |
| `get_user_theme` | Get theme |
| `save_user_theme` | Save theme |
| `delete_user_theme` | Delete theme |

## XCH Transactions (7)
| Endpoint | Description |
|----------|-------------|
| `send_xch` | Send XCH |
| `bulk_send_xch` | Multi-recipient send |
| `multi_send` | Multi-asset send |
| `combine` | Merge coins |
| `split` | Split coin |
| `auto_combine_xch` | Auto-merge |
| `finalize_clawback` | Complete clawback |

## CAT Tokens (9)
| Endpoint | Description |
|----------|-------------|
| `get_cats` | List wallet CATs |
| `get_all_cats` | List all known CATs |
| `get_token` | Get token details |
| `update_cat` | Update metadata |
| `resync_cat` | Resync balance |
| `issue_cat` | Mint new token |
| `send_cat` | Send CAT |
| `bulk_send_cat` | Multi-recipient CAT |
| `auto_combine_cat` | Auto-merge CAT coins |

## NFTs (14)
| Endpoint | Description |
|----------|-------------|
| `get_nfts` | List NFTs |
| `get_nft` | Get NFT details |
| `get_nft_icon` | Get icon |
| `get_nft_thumbnail` | Get thumbnail |
| `get_nft_data` | Get raw data |
| `get_nft_collections` | List collections |
| `get_nft_collection` | Get collection |
| `update_nft` | Update visibility |
| `update_nft_collection` | Update collection |
| `redownload_nft` | Re-fetch data |
| `bulk_mint_nfts` | Mint NFTs |
| `transfer_nfts` | Transfer NFTs |
| `add_nft_uri` | Add URI |
| `assign_nfts_to_did` | Assign to DID |

## DIDs (6)
| Endpoint | Description |
|----------|-------------|
| `get_dids` | List DIDs |
| `get_minter_did_ids` | List minter DIDs |
| `update_did` | Update DID |
| `create_did` | Create DID |
| `transfer_dids` | Transfer DIDs |
| `normalize_dids` | Normalize state |

## Offers (11)
| Endpoint | Description |
|----------|-------------|
| `make_offer` | Create offer |
| `take_offer` | Accept offer |
| `combine_offers` | Merge offers |
| `view_offer` | View offer |
| `import_offer` | Import offer |
| `get_offers` | List offers |
| `get_offers_for_asset` | Filter by asset |
| `get_offer` | Get specific offer |
| `delete_offer` | Delete local |
| `cancel_offer` | Cancel on-chain |
| `cancel_offers` | Bulk cancel |

## Options (5)
| Endpoint | Description |
|----------|-------------|
| `get_options` | List options |
| `get_option` | Get option |
| `update_option` | Update visibility |
| `mint_option` | Mint option |
| `exercise_options` | Exercise |
| `transfer_options` | Transfer |

## Coins & Addresses (8)
| Endpoint | Description |
|----------|-------------|
| `get_coins` | List coins |
| `get_coins_by_ids` | Get specific coins |
| `get_are_coins_spendable` | Check spendability |
| `get_spendable_coin_count` | Count spendable |
| `check_address` | Validate address |
| `get_derivations` | Get derivations |
| `increase_derivation_index` | Generate addresses |
| `is_asset_owned` | Check ownership |

## Transactions (6)
| Endpoint | Description |
|----------|-------------|
| `get_transactions` | List transactions |
| `get_transaction` | Get by height |
| `get_pending_transactions` | List pending |
| `sign_coin_spends` | Sign transaction |
| `view_coin_spends` | Preview |
| `submit_transaction` | Broadcast |

## Network & Peers (12)
| Endpoint | Description |
|----------|-------------|
| `get_peers` | List peers |
| `add_peer` | Add peer |
| `remove_peer` | Remove/ban peer |
| `set_discover_peers` | Toggle discovery |
| `set_target_peers` | Set target count |
| `get_network` | Get current network |
| `get_networks` | List networks |
| `set_network` | Switch network |
| `set_network_override` | Per-wallet override |
| `set_delta_sync` | Toggle delta sync |
| `set_delta_sync_override` | Per-wallet sync |
| `set_change_address` | Set change address |

## System (4)
| Endpoint | Description |
|----------|-------------|
| `get_sync_status` | Sync progress |
| `get_version` | Wallet version |
| `get_database_stats` | DB statistics |
| `perform_database_maintenance` | Optimize DB |

## WalletConnect (5)
| Endpoint | Description |
|----------|-------------|
| `filter_unlocked_coins` | Filter unlocked |
| `get_asset_coins` | Get spendable |
| `sign_message_with_public_key` | Sign with pubkey |
| `sign_message_by_address` | Sign with address |
| `send_transaction_immediately` | Direct broadcast |
