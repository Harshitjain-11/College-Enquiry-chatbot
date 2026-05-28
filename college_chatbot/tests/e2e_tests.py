import time
import json
import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:5000'
HEADERS = {'Content-Type': 'application/json'}

TESTS = [
    {"input": "tell me about your college", "must": ["about", "naac", "college"]},
    {"input": "is itm good", "must": ["naac", "grade", "good"]},
    {"input": "where is itm located", "must": ["gwalior", "address", "map"]},

    {"input": "do you have aiml", "must": ["aiml", "artificial intelligence", "ai"]},
    {"input": "tell me about ds", "must": ["data science", "data"]},
    {"input": "coding branch", "must": ["cse", "coding"]},
    {"input": "best branch for placement", "must": ["placement", "recommend"]},

    {"input": "how many semesters in btech", "must": ["8", "semesters", "4 years"]},
    {"input": "duration of mba", "must": ["2 years", "duration"]},
    {"input": "semesters in mca", "must": ["2 years", "semesters"]},

    {"input": "fees of aiml", "must": ["fee", "₹", "rupee", "fees"]},
    {"input": "hostel fee", "must": ["hostel", "fee", "mess"]},

    {"input": "highest package", "must": ["highest", "package", "lpa"]},
    {"input": "girls hostel", "must": ["girls hostel", "girls", "warden"]},

    {"input": "i want ai career", "must": ["recommend", "ai", "career"]},

    {"input": "aimlll", "must": ["aiml", "artificial"]},
    {"input": "ds branch hai?", "must": ["data", "science"]},
    {"input": "hello bhai", "must": ["hello", "welcome", "namaste"]},
]


def post_chat(msg, session_id="e2e-session"):
    data = json.dumps({"message": msg, "session_id": session_id}).encode("utf-8")
    req = urllib.request.Request(BASE + '/chat', data=data, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('HTTP error', e.code, e.read().decode())
        return None
    except Exception as e:
        print('Request error', e)
        return None


def wait_for_server(timeout=45):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(BASE + '/health', timeout=5) as r:
                data = json.loads(r.read().decode())
                if data.get('status') == 'ok' and data.get('model_loaded'):
                    print('Server healthy')
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def run_tests():
    if not wait_for_server():
        print('Server failed to become healthy within timeout')
        return 2

    failures = []

    # Run individual tests
    for idx, t in enumerate(TESTS):
        sid = f"e2e-session-{idx}"
        out = post_chat(t['input'], session_id=sid)
        if not out:
            failures.append((t['input'], 'no response'))
            print('NO RESPONSE for', t['input'])
            continue
        reply = (out.get('reply') or '').lower()
        intent = (out.get('intent') or '').lower()
        passed = False
        for kw in t['must']:
            if kw.lower() in reply or kw.lower() in intent:
                passed = True
                break
        print('INPUT:', t['input'], '=> intent=', intent, ' reply=', (reply[:140] + '...') if len(reply) > 140 else reply)
        if not passed:
            failures.append((t['input'], reply, intent))

    # Follow-up test: ensure context carries course
    session = 'followup-session'
    r1 = post_chat('tell me about aiml', session_id=session)
    time.sleep(0.4)
    r2 = post_chat('fees?', session_id=session)
    print('\nFOLLOW-UP check:')
    print('First reply:', (r1 or {}).get('reply', '')[:120])
    print('Follow-up reply:', (r2 or {}).get('reply', '')[:120])
    if r2 and ('fee' not in (r2.get('reply') or '').lower()):
        failures.append(('followup fees', r2))

    if failures:
        print('\nE2E TESTS: FAILED', len(failures), 'cases')
        for f in failures:
            print(' -', f)
        return 3

    print('\nE2E TESTS: ALL PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(run_tests())
