import json, glob

files = glob.glob('raw_data/s230_validated_*.json')
latest = max(files)
print(f'Loading: {latest}')

with open(latest) as f:
    data = json.load(f)

# Case-level metadata overrides
# Format: cluster_id -> {field: value}
OVERRIDES = {
    # Gonzalez — § 230(c)(1) question presented but not resolved
    10049690: {'holding_status': 'qualified', 'primary_basis': 's230c_immunity'},
    # Enigma 2019 — § 230(c)(2)(B) Good Samaritan blocking
    4660480:  {'primary_basis': 's230c2_immunity'},
    # Enigma 2023 — § 230(c)(2)(B) downstream
    9403767:  {'primary_basis': 's230c2_immunity'},
    # Woodhull — § 230(e)(5) FOSTA
    4720971:  {'primary_basis': 's230e_fosta'},
    # M.H. v. Omegle — § 230(c)(1) and § 230(e)(5)
    10290467: {'primary_basis': 's230e_fosta'},
    # Lemmon v. Snap — scope boundary, circuit split
    4880016:  {'holding_status': 'definitive', 'primary_basis': 's230c_immunity'},
    # G.G. v. Salesforce — FOSTA interface, controversial
    9417992:  {'primary_basis': 's230e_fosta'},
    # Doe v. Snap CA5 — circuit split, internal dissent
    9453171:  {'holding_status': 'definitive', 'primary_basis': 's230c_immunity'},
    # Anderson v. TikTok — circuit split creator
    10082197: {'holding_status': 'definitive', 'primary_basis': 's230c_immunity'},
    # A.B. v. Salesforce — FOSTA interface
    10298359: {'primary_basis': 's230e_fosta'},
    # M.P. v. Meta — Zeran reaffirmation
    10327795: {'holding_status': 'definitive', 'primary_basis': 's230c_immunity'},
    # Doe v. Grindr — dual subsection, cert pending
    10334609: {'holding_status': 'qualified', 'primary_basis': 's230e_fosta'},
    # U.S. v. EZ Lynk — scope boundary, non-speech enforcement
    10657265: {'holding_status': 'definitive', 'primary_basis': 's230c_immunity'},
}

updated = 0
for case in data['results']:
    cid = case.get('cluster_id')

    # Set defaults
    if 'primary_basis' not in case:
        case['primary_basis'] = 's230c_immunity'
    if 'holding_status' not in case:
        case['holding_status'] = 'definitive'
    if 'publication_status' not in case:
        case['publication_status'] = 'published'

    # Apply overrides
    if cid in OVERRIDES:
        for field, value in OVERRIDES[cid].items():
            case[field] = value
        updated += 1

with open(latest, 'w') as f:
    json.dump(data, f, indent=2)

print(f'Metadata added to all {len(data["results"])} cases.')
print(f'Overrides applied to {updated} cases.')

# Print summary
from collections import Counter
pb = Counter(c.get('primary_basis') for c in data['results'])
hs = Counter(c.get('holding_status') for c in data['results'])
print(f'\nprimary_basis distribution: {dict(pb)}')
print(f'holding_status distribution: {dict(hs)}')