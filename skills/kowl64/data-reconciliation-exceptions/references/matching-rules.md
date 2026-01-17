# Matching Rules (priority order)

Primary key (best):
1) Pay Number (exact match after trimming spaces)

Secondary keys (only if Pay Number missing/invalid):
2) Driver Card number
3) Driving Licence number
4) Driver Qualification Card number

Name handling (supporting check, not primary join):
- Normalize: trim, collapse spaces, uppercase
- Flag as mismatch if name differs after normalization but key matches
