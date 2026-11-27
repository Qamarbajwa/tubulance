import os

for f in ['SHORT_EMAIL_TO_PROFESSOR_ENGLISH.txt', 'SHORT_EMAIL_TO_PROFESSOR_GERMAN.txt']:
    p = os.path.join(r'd:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK', f)
    with open(p, 'r', encoding='utf-8') as fp:
        t = fp.read()
    print(f, 'hash:', '#' in t, 'em-dash:', chr(8212) in t or chr(8211) in t, 'carbon:', 'Google Carbon' in t, 'gemini:', 'Gemini' in t)
