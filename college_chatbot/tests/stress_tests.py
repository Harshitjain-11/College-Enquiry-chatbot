import json
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:5000'
HEADERS = {'Content-Type': 'application/json'}

CASES = [
    ('hinglish', {'message': 'bhai coding wali branch ka scene kya hai', 'session_id': 'stress-1'}),
    ('typo', {'message': 'aimlll fees', 'session_id': 'stress-2'}),
    ('short_followup_1', {'message': 'tell me about aiml', 'session_id': 'stress-3'}),
    ('short_followup_2', {'message': 'fees?', 'session_id': 'stress-3'}),
    ('rapid_1', {'message': 'hello bhai', 'session_id': 'stress-4'}),
    ('rapid_2', {'message': 'placement ratio kya hai', 'session_id': 'stress-4'}),
    ('rapid_3', {'message': 'hostel fee', 'session_id': 'stress-4'}),
]


def post_chat(payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + '/chat', data=data, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main():
    results = []
    for name, payload in CASES:
        out = post_chat(payload)
        results.append((name, out.get('intent'), (out.get('reply') or '')[:120].replace('\n', ' ')))

    empty_status = None
    try:
        post_chat({'message': '', 'session_id': 'stress-empty'})
    except urllib.error.HTTPError as exc:
        empty_status = exc.code

    malformed_status = None
    try:
        req = urllib.request.Request(BASE + '/chat', data=b'not-json', headers=HEADERS)
        urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as exc:
        malformed_status = exc.code

    print('STRESS RESULTS:')
    for row in results:
        print(row)
    print('empty_status=', empty_status)
    print('malformed_status=', malformed_status)


if __name__ == '__main__':
    main()
