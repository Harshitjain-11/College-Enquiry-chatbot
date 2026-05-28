import sys
import os

# Ensure project root is on sys.path for imports when running tests directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from chatbot.nlp_engine import NLPEngine
from chatbot.intent_classifier import IntentClassifier
from chatbot.response_generator import ResponseGenerator
from chatbot.context_manager import ContextManager
from chatbot.entity_extractor import EntityExtractor


def run():
    nlp = NLPEngine()
    ic = IntentClassifier(nlp)
    rg = ResponseGenerator()
    cm = ContextManager()
    ee = EntityExtractor()

    tests = []

    # Test 1: short aiml query
    text = "aiml"
    c = ic.classify(text, session_id="s1")
    print('INPUT:', text, '->', c)
    if c['intent'] not in ('specializations','courses_offered'):
        print('FAIL: aiml intent')
        return 2

    # Test 2: hinglish placement
    text = 'placement ratio kya hai'
    c = ic.classify(text, session_id='s2')
    print('INPUT:', text, '->', c)
    if 'placement' not in c['intent']:
        print('FAIL: placement intent')
        return 3

    # Test 3: follow-up fees
    session = 's3'
    first = 'tell me about aiml'
    c1 = ic.classify(first, session_id=session)
    entities1 = ee.extract(first)
    cm.update(session, first, '', c1['intent'], entities1)
    second = 'fees?'
    c2 = ic.classify(second, session_id=session)
    print('FOLLOWUP:', second, '->', c2)

    print('All smoke tests passed.')
    return 0

if __name__ == '__main__':
    sys.exit(run())
