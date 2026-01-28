#!/usr/bin/env python3
"""
Dex CRM Newsletter/Junk Contact Cleanup
Archives contacts that look like newsletters, automated senders, or non-human contacts.
"""

import json, urllib.request, os, sys, re, time

API_KEY = os.environ.get('DEX_API_KEY')
if not API_KEY:
    print("ERROR: DEX_API_KEY not set")
    sys.exit(1)

BASE = "https://api.getdex.com/api/rest"
HEADERS = {
    "Content-Type": "application/json",
    "x-hasura-dex-api-key": API_KEY
}

# --- PATTERNS TO MATCH JUNK CONTACTS ---

# Email prefixes that indicate automated/newsletter senders
# Only high-confidence prefixes — avoid false positives on real businesses
JUNK_PREFIXES = [
    'noreply', 'no-reply', 'no_reply', 'donotreply', 'do-not-reply',
    'newsletter', 'newsletters',
    'mailer', 'mailer-daemon', 'postmaster', 'bounce',
    'unsubscribe',
    'automated',
    'noreply-',
]

# Domains known to be bulk email/newsletter platforms (not companies with real employees)
JUNK_DOMAINS = [
    'substack.com', 'substacknote.com',
    'mailchimp.com', 'mail.mailchimp.com', 'mcusercontent.com',
    'mailchimpapp.net',
    'sendgrid.net',
    'mailgun.org',
    'constantcontact.com',
    'klaviyomail.com',
    'mailerlite.com', 'convertkit.com', 'beehiiv.com',
    'amazonses.com',
    'createsend.com', 'cmail19.com', 'cmail20.com',
    'intercom-mail.com',
    'postmarkapp.com',
    'sparkpostmail.com',
    'mandrillapp.com',
    'sendinblue.com', 'brevo.com',
    'e.squarespace.com',
    'shopifyemail.com',
    'facebookmail.com',
    'calendar.google.com',
    'resource.calendar.google.com',
]

# Name patterns that indicate non-human contacts
JUNK_NAME_PATTERNS = [
    r'^(the\s)?\w+\s(newsletter|digest|update|weekly|daily|report)s?$',
    r'^(noreply|no-reply|info|hello|team|support|admin|billing)$',
    r'unsubscribe',
    r'^[\w\s]*(notifications?)$',
]

DRY_RUN = '--dry-run' in sys.argv
VERBOSE = '--verbose' in sys.argv or '-v' in sys.argv

def api_get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def api_put(path, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=HEADERS, method="PUT")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def is_junk_email(email):
    email = email.lower().strip()
    local, _, domain = email.partition('@')
    
    # Check domain
    for jd in JUNK_DOMAINS:
        if domain == jd or domain.endswith('.' + jd):
            return f"junk domain: {domain}"
    
    # Check prefix
    # Strip numbers/dots from local part for matching
    local_clean = re.sub(r'[\d._+-]+$', '', local)
    for prefix in JUNK_PREFIXES:
        if local_clean == prefix or local.startswith(prefix + '@') or local.startswith(prefix + '+'):
            return f"junk prefix: {local}"
    
    # Check for UUID/hash-like local parts (automated systems)
    if re.match(r'^[0-9a-f]{8,}[-_]?', local) and len(local) > 20:
        return f"hash-like address: {local}"
    
    return None

def is_junk_name(first_name, last_name):
    full = f"{first_name} {last_name}".strip().lower()
    if not full:
        return "empty name"
    
    for pattern in JUNK_NAME_PATTERNS:
        if re.match(pattern, full, re.IGNORECASE):
            return f"junk name pattern: {full}"
    
    return None

def main():
    print(f"{'DRY RUN - ' if DRY_RUN else ''}Dex Newsletter/Junk Contact Cleanup")
    print("=" * 50)
    
    # Fetch all contacts
    all_contacts = []
    offset = 0
    while True:
        data = api_get(f"/contacts?limit=100&offset={offset}")
        contacts = data.get('contacts', [])
        if not contacts:
            break
        all_contacts.extend(contacts)
        offset += 100
        if len(contacts) < 100:
            break
    
    print(f"Total contacts: {len(all_contacts)}")
    
    # Filter out already archived
    active = [c for c in all_contacts if not c.get('is_archived', False)]
    print(f"Active (non-archived): {len(active)}")
    
    # Find junk contacts
    junk = []
    for c in active:
        emails = [e['email'] for e in c.get('emails', [])]
        first = c.get('first_name', '') or ''
        last = c.get('last_name', '') or ''
        
        reason = None
        
        # Check emails — only flag if ALL emails are junk
        # (contacts with both a junk and real email are real people)
        if emails:
            junk_reasons = []
            for email in emails:
                r = is_junk_email(email)
                if r:
                    junk_reasons.append(r)
            if junk_reasons and len(junk_reasons) == len(emails):
                reason = junk_reasons[0]
        
        # Skip empty-name check — too many false positives
        # (real people imported without names from calendar/email)
        
        if reason:
            junk.append({
                'id': c['id'],
                'name': f"{first} {last}".strip(),
                'emails': emails,
                'reason': reason
            })
    
    print(f"Junk contacts found: {len(junk)}")
    print()
    
    if VERBOSE or DRY_RUN:
        for j in sorted(junk, key=lambda x: x['reason']):
            print(f"  [{j['reason']}] {j['name']} | {', '.join(j['emails'])}")
        print()
    
    if DRY_RUN:
        print(f"DRY RUN complete. Would archive {len(junk)} contacts.")
        return
    
    # Archive junk contacts
    archived = 0
    errors = 0
    for i, j in enumerate(junk):
        try:
            api_put(f"/contacts/{j['id']}", {
                "changes": {"is_archived": True}
            })
            archived += 1
        except Exception as e:
            errors += 1
            if VERBOSE:
                print(f"  ERROR archiving {j['name']}: {e}")
        
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(junk)} archived")
        
        time.sleep(0.1)
    
    print(f"\nDone! Archived: {archived}, Errors: {errors}")
    
    # Output summary as JSON for cron consumption
    summary = {
        "total_contacts": len(all_contacts),
        "active_contacts": len(active),
        "junk_found": len(junk),
        "archived": archived,
        "errors": errors
    }
    print(f"\nSummary: {json.dumps(summary)}")

if __name__ == '__main__':
    main()
