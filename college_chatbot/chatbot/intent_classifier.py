"""
Intent Classifier for the College Enquiry Chatbot.

Implements a hybrid classification approach:
1. Exact pattern matching
2. TF-IDF cosine similarity (via NLPEngine)
3. Keyword fallback rules
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

from chatbot.nlp_engine import NLPEngine

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = Path(os.environ.get(
    "ITM_CHATBOT_RUNTIME_DIR",
    Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "itm_chatbot",
))
LOG_DIR = RUNTIME_ROOT / "logs"
LOG_FILE = LOG_DIR / "chat_log.txt"
INTENTS_PATH = BASE_DIR / "data" / "intents.json"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)


class IntentClassifier:
    """
    Hybrid intent classifier combining exact match, TF-IDF cosine similarity,
    and keyword-based fallback rules.
    """

    def __init__(self, nlp_engine: NLPEngine):
        """
        Initialize the classifier.

        Args:
            nlp_engine: An initialized NLPEngine instance.
        """
        self.nlp = nlp_engine
        self.exact_patterns = self._build_exact_patterns()
        logger.info("IntentClassifier initialized with %d exact patterns.", len(self.exact_patterns))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, text: str, session_id: str = "unknown") -> dict:
        """
        Classify user input into an intent using the hybrid approach.

        Args:
            text: Raw user message.
            session_id: Session identifier for logging.

        Returns:
            Dict with keys: intent, confidence, matched_keywords, tokens, method.
        """
        tokens, cleaned = self.nlp.preprocess(text)
        text_lower = text.lower().strip()

        percent_match = re.search(r'(\d{1,3})\s*%|(\d{1,3})\s*percent|(\d{1,3})\s*marks', text_lower)
        eligibility_words = ["eligible", "admission", "milega", "le sakta", "apply", "qualify", "le skta", "lena hai"]
        if percent_match and any(word in text_lower for word in eligibility_words):
            percentage = next((group for group in percent_match.groups() if group), None)
            result = {
                "intent": "eligibility_check",
                "confidence": 0.95,
                "matched_keywords": [percent_match.group()],
                "tokens": tokens,
                "method": "regex_percentage",
                "percentage": int(percentage) if percentage else None,
            }
            self._log(session_id, text, result)
            return result

        # Step 0: High-confidence rule-based routing for common conversational phrases
        rule_intent = self._rule_based_intent(text_lower)
        if rule_intent:
            result = {
                "intent": rule_intent,
                "confidence": 0.98,
                "matched_keywords": [],
                "tokens": tokens,
                "method": "rule_based",
            }
            self._log(session_id, text, result)
            return result

        # Step 1: Exact pattern match
        exact_result = self._exact_match(text_lower)
        if exact_result:
            result = {
                "intent": exact_result,
                "confidence": 1.0,
                "matched_keywords": [],
                "tokens": tokens,
                "method": "exact_match",
            }
            self._log(session_id, text, result)
            return result

        # Step 1.5: Keyword boost for short or high-signal queries
        kw_boost = self.nlp.keyword_boost(text_lower)
        if kw_boost:
            result = {
                "intent": kw_boost,
                "confidence": 0.75,
                "matched_keywords": [],
                "tokens": tokens,
                "method": "keyword_boost",
            }
            self._log(session_id, text, result)
            return result

        # Step 2: TF-IDF cosine similarity
        intent, confidence = self.nlp.predict_intent(text)

        # Step 3: Keyword fallback if TF-IDF gives low confidence
        if intent == "fallback" or confidence < 0.25:
            kw_intent = self._keyword_fallback(tokens)
            if kw_intent:
                intent = kw_intent
                confidence = 0.45

        # Detect angry/frustrated user
        if self._is_angry(tokens):
            intent = "angry_user"
            confidence = 0.99

        kw_matches = self.nlp.get_keyword_matches(tokens)

        result = {
            "intent": intent,
            "confidence": round(confidence, 4),
            "matched_keywords": kw_matches.get(intent, []),
            "tokens": tokens,
            "method": "tfidf_cosine" if intent != "fallback" else "fallback",
        }
        self._log(session_id, text, result)
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_exact_patterns(self) -> dict[str, str]:
        """
        Build a dict mapping lowercase pattern strings to their intent tags.

        Returns:
            Dict of {pattern_string: intent_tag}.
        """
        mapping: dict[str, str] = {}
        with open(INTENTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                mapping[pattern.lower().strip()] = intent["tag"]
        return mapping

    def _exact_match(self, text_lower: str) -> str | None:
        """
        Check whether the user text exactly matches a known pattern.

        Args:
            text_lower: Lowercased user input.

        Returns:
            Intent tag if matched, else None.
        """
        return self.exact_patterns.get(text_lower)

    def _keyword_fallback(self, tokens: list[str]) -> str | None:
        """
        Use keyword presence to guess intent when TF-IDF confidence is low.

        Args:
            tokens: Preprocessed tokens.

        Returns:
            Intent tag if a keyword is found, else None.
        """
        kw_matches = self.nlp.get_keyword_matches(tokens)
        if not kw_matches:
            return None
        # Return intent with most keyword matches
        return max(kw_matches, key=lambda k: len(kw_matches[k]))

    def _rule_based_intent(self, text_lower: str) -> str | None:
        """Fast path for high-value conversational queries and greetings."""
        greeting_phrases = {
            "hello", "hi", "hii", "hey", "hello bhai", "kya scene hai",
            "namaste", "namaskar", "good morning", "good afternoon", "good evening",
        }
        if text_lower in greeting_phrases:
            return "greeting"

        about_college_phrases = {
            "tell me about your college", "tell me about the college", "about itm",
            "is itm good", "itm good", "college kaisa hai", "tell me about itm",
        }
        if text_lower in about_college_phrases:
            return "college_overview"

        if text_lower in {"where is itm located", "where is itm", "itm located", "kahan hai college"}:
            return "contact_info"

        if text_lower in {"tell me about ds", "ds branch hai", "ds branch", "data science", "data science branch"}:
            return "specializations"

        return None

    def _is_angry(self, tokens: list[str]) -> bool:
        """
        Detect frustrated or angry user messages.

        Args:
            tokens: Preprocessed tokens.

        Returns:
            True if anger indicators detected.
        """
        anger_words = {
            "useless", "worst", "pathetic", "terrible", "horrible",
            "stupid", "idiot", "waste", "rubbish", "garbage", "hate",
            "disgusting", "awful", "ridiculous", "nonsense",
            "bakwas", "bekar", "kuch nahi aata", "stupid bot"
        }
        token_set = set(tokens)
        text_str = " ".join(tokens)
        if anger_words.intersection(token_set):
            return True
        # Check multi-word anger phrases
        for phrase in ("kuch nahi aata", "stupid bot", "bakwas", "bekar"):
            if phrase in text_str:
                return True
        return False

    def classify_compound(self, message: str) -> list[tuple[str, float]] | None:
        """
        Detect multiple intents in a single message.

        Splits on 'aur', 'and', 'bhi', 'also', 'plus', 'saath mein'
        and classifies each part separately.

        Args:
            message: Raw user message.

        Returns:
            List of (intent, confidence) tuples if multiple intents found,
            else None (caller should use normal single-intent flow).
        """
        SPLIT_WORDS = [
            " aur ", " and ", " bhi ", " also ",
            " plus ", " saath ", " ke saath ", " with "
        ]
        parts = [message]
        for sw in SPLIT_WORDS:
            new_parts = []
            for p in parts:
                new_parts.extend(p.split(sw))
            parts = new_parts

        parts = [p.strip() for p in parts if len(p.strip()) > 3]

        if len(parts) <= 1:
            return None

        results = []
        for part in parts:
            result = self.classify(part)
            intent = result["intent"]
            conf = result["confidence"]
            if conf > 0.2 and intent != "fallback":
                results.append((intent, conf))

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[tuple[str, float]] = []
        for intent, conf in results:
            if intent not in seen:
                seen.add(intent)
                unique.append((intent, conf))

        return unique if len(unique) > 1 else None

    def _log(self, session_id: str, user_text: str, result: dict) -> None:
        """
        Append classification result to the chat log file.

        Args:
            session_id: Session identifier.
            user_text: Original user input.
            result: Classification result dict.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = (
            f"[{timestamp}] session={session_id} | "
            f"intent={result['intent']} | "
            f"confidence={result['confidence']:.4f} | "
            f"method={result['method']} | "
            f"text={user_text!r}\n"
        )
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_line)
        except OSError as exc:
            logger.error("Failed to write to chat log: %s", exc)
