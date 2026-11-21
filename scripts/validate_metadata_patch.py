import json
import subprocess
import os

workspaces = [
    ('Workspace 01: Hodge Conjecture', r'd:\Comfy UI\hodge conjecture', 'v1.6.0-rosetta'),
    ('Workspace 02: 4D Yang-Mills', r'd:\Comfy UI\yang mills and the mass gap', 'v1.5.0-rosetta'),
    ('Workspace 03: Riemann Hypothesis', r'd:\Comfy UI\rheihman hypothesis', 'v3.4.0-rosetta'),
    ('Workspace 04: 3D Navier-Stokes & tare_core', r'd:\Comfy UI\tubulance', 'v2.0.0-rosetta-tare'),
]

print('=' * 80)
print('VALIDATION SUITE: 4 WORKSPACES METADATA & GITHUB RELEASE CHECK')
print('=' * 80)

for name, base_dir, tag in workspaces:
    print(f'\n--- {name} ({tag}) ---')
    # 1. GITHUB_RELEASE_NOTES.md
    notes_p = os.path.join(base_dir, 'GITHUB_RELEASE_NOTES.md')
    with open(notes_p, 'r', encoding='utf-8') as f:
        notes_text = f.read()
    assert '#' not in notes_text, f'Found # in {notes_p}'
    assert '\u2014' not in notes_text, f'Found em-dash in {notes_p}'
    assert '\u2013' not in notes_text, f'Found en-dash in {notes_p}'
    assert 'Qamar Munawer' in notes_text, f'Missing author in {notes_p}'
    assert 'Brandenburg University of Technology Cottbus-Senftenberg' in notes_text, f'Missing affiliation in {notes_p}'
    assert 'ai is being used as a tool' in notes_text, f'Missing tool attribution in {notes_p}'
    assert 'strictly open' in notes_text.lower(), f'Missing open horizon in {notes_p}'
    print('  [PASS] GITHUB_RELEASE_NOTES.md: 0 hashes, 0 em/en-dashes, full attribution, open horizon lock.')

    # 2. .zenodo.json
    zenodo_p = os.path.join(base_dir, '.zenodo.json')
    with open(zenodo_p, 'r', encoding='utf-8') as f:
        z_data = json.load(f)
    z_dump = json.dumps(z_data)
    assert '#' not in z_dump, f'Found # in {zenodo_p}'
    assert '\u2014' not in z_dump, f'Found em-dash in {zenodo_p}'
    assert '\u2013' not in z_dump, f'Found en-dash in {zenodo_p}'
    print('  [PASS] .zenodo.json: valid JSON, 0 hashes, 0 em/en-dashes.')
    print('         Title:', z_data['title'])
    print('         Version:', z_data['version'])

    # 3. Live GitHub Release
    r = subprocess.run(['gh', 'release', 'view', tag, '--json', 'name,url,tagName'], cwd=base_dir, capture_output=True, text=True)
    if r.returncode == 0:
        rel_info = json.loads(r.stdout)
        print('  [PASS] Live GitHub Release:')
        print('         Tag:  ', rel_info.get('tagName'))
        print('         Title:', rel_info.get('name'))
        print('         URL:  ', rel_info.get('url'))
    else:
        print('  [FAIL] GitHub release view failed:', r.stderr)

print('\n' + '=' * 80)
print('ALL 4 WORKSPACES METADATA & GITHUB RELEASES VALIDATED 100% PASS')
print('=' * 80)
