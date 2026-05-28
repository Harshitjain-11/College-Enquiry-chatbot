import pytest

from chatbot.nlp_engine import NLPEngine
from chatbot.intent_classifier import IntentClassifier
from chatbot.response_generator import ResponseGenerator
from chatbot.context_manager import ContextManager
from chatbot.entity_extractor import EntityExtractor


@pytest.fixture(scope="module")
def components():
    nlp = NLPEngine()
    ic = IntentClassifier(nlp)
    rg = ResponseGenerator()
    cm = ContextManager()
    ee = EntityExtractor()
    return nlp, ic, rg, cm, ee


def test_short_aiml_query(components):
    nlp, ic, rg, cm, ee = components
    session = "test-session-aiml"
    text = "aiml"
    classification = ic.classify(text, session_id=session)
    assert classification["intent"] in ("specializations", "courses_offered"), \
        f"Unexpected intent: {classification}"
    # generate response
    entities = ee.extract(text)
    ctx = cm.get_or_create(session)
    reply, q = rg.generate(classification["intent"], entities, ctx)
    assert "AIML" in reply.upper() or "AI" in reply.upper()


def test_hinglish_placement_query(components):
    nlp, ic, rg, cm, ee = components
    session = "test-session-placement"
    text = "placement ratio kya hai"
    classification = ic.classify(text, session_id=session)
    assert "placement" in classification["intent"], f"Unexpected intent: {classification}"
    entities = ee.extract(text)
    ctx = cm.get_or_create(session)
    reply, q = rg.generate(classification["intent"], entities, ctx)
    assert "PLACEMENT" in reply.upper() or "PACKAGE" in reply.upper()


def test_follow_up_context(components):
    nlp, ic, rg, cm, ee = components
    session = "test-session-followup"
    # user asks about B.Tech AIML
    first = "tell me about aiml"
    c1 = ic.classify(first, session_id=session)
    entities1 = ee.extract(first)
    ctx = cm.get_or_create(session)
    # simulate update
    cm.update(session, first, "", c1["intent"], entities1)
    # follow-up
    second = "fees?"
    c2 = ic.classify(second, session_id=session)
    # when cleaned, intent should resolve to fees_structure or related
    assert c2["intent"] in ("fees_structure", "fees_structure", "course_detail", "fees_structure" )

*** End Patch