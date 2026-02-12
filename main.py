import re
import difflib
import random
import datetime

ABBREVIATIONS = {
    "u": "you", "r": "are", "im": "i am", "idk": "i don't know",
    "pls": "please", "thx": "thanks", "ty": "thank you", "cuz": "because",
    "msg": "message", "b4": "before", "gr8": "great", "btw": "by the way",
    "asap": "as soon as possible"
}

RESPONSES = {
    "hello": ["Hi there!", "Hello!", "Hey! How can I help you today?"],
    "hi": ["Hi!", "Hello!", "Hey there! What can I do for you?"],
    "hey": ["Hey!", "Hi! What can I do for you?"],
    "how are you": ["I'm doing well, thanks for asking! How about you?"],
    "who are you": ["I'm your smart assistant. Ask me anything!"],
    "what can you do": ["I can chat, give facts, offer advice, and help you with tech trouble!"],
    "what is ai": ["AI stands for Artificial Intelligence. It's like teaching computers to think."],
    "machine learning": ["ML is part of AI where computers learn patterns from data."],
    "cloud computing": ["Storing and accessing data via the internet, like Google Drive."],
    "teach me": ["Did you know? Honey never spoils.", "Fun fact: Bananas are berries, strawberries aren't!"],
    "give advice": ["Keep learning and never stop exploring.", "Take breaks and stay healthy!"],
    "current time": [lambda: f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}"],
    "current date": [lambda: f"Today's date is {datetime.date.today().strftime('%Y-%m-%d')}"],
    "help": ["I'm here to assist. What seems to be the problem?"],
    "troubleshooting": ["Try restarting the app. Still not working? Let me know more details."],
    "thank you": ["You're welcome!", "Glad to help!"],
    "bye": ["Goodbye!", "See you later!", "Take care!"],
    "i am sad": [
        "I’m sorry you're feeling that way. Want to talk about it?",
        "It’s okay to feel sad sometimes. I’m here with you.",
        "Want to hear a fun fact or joke to cheer up?"
    ],
    "i am happy": [
        "Yay! I love hearing that!",
        "Happiness is contagious — thanks for sharing!"
    ],
    "great": [
        "That's awesome to hear! What’s making your day great?",
        "Glad you're feeling great! Anything exciting going on?",
        "Great! Let me know if you want to learn something new today."
    ],

    "fine": [
        "Alright, I’m here if you want to talk or learn something new.",
        "Good to hear you’re fine. What would you like to do next?"
    ],
    "joke": [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I told my computer I needed a break, and it said 'No problem, I'll go to sleep.'"
    ],
    "name": [
        "I don't think I know your name yet! What should I call you?",
        "I'd love to know your name! What's your name?"
    ],
    "default": [
        "I'm not sure I understand. Can you rephrase or ask something else?",
        "Sorry, I didn't get that. Maybe try asking about AI, machine learning, or just say 'teach me'.",
        "Can you tell me more or ask a different question?"
    ],
    "what did we talk about": [
        "I remember we talked about {topics}.",
        "Earlier, you mentioned {topics}."
    ]
}

# Sorted by length desc for better fuzzy matching
RECOGNIZED_PHRASES = sorted(RESPONSES.keys(), key=len, reverse=True)

class Chatbot:
    def __init__(self):
        self.last_intent = None
        self.memory = []  # conversation history
        self.user_name = None
        self.topics = set()

        # Precompile regex for name extraction once
        self.name_regex = re.compile(r"\bmy name is (\w+)\b", re.I)

        # Define emotion keywords for quick lookup
        self.sad_words = {"sad", "unhappy", "depressed", "down", "miserable"}
        self.happy_words = {"happy", "glad", "joy", "great", "good", "fine"}

    def preprocess(self, text):
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        return [ABBREVIATIONS.get(w, w) for w in words]

    def fuzzy_match(self, words):
        sentence = " ".join(words)
        # Direct close matches first
        match = difflib.get_close_matches(sentence, RECOGNIZED_PHRASES, n=1, cutoff=0.6)
        if match:
            return match[0]
        # Check if all phrase words approximately appear in input words
        for phrase in RECOGNIZED_PHRASES:
            if all(any(difflib.SequenceMatcher(None, pw, uw).ratio() > 0.6 for uw in words) for pw in phrase.split()):
                return phrase
        # Single word approximate match fallback
        for w in words:
            match = difflib.get_close_matches(w, RECOGNIZED_PHRASES, n=1, cutoff=0.6)
            if match:
                return match[0]
        return None

    def detect_emotion(self, user_input):
        words = set(self.preprocess(user_input))
        if words & self.sad_words:
            return "i am sad"
        if words & self.happy_words:
            return "i am happy"
        return None

    def extract_name(self, user_input):
        match = self.name_regex.search(user_input)
        if match:
            return match.group(1).capitalize()
        return None

    def get_response(self, user_input):
        self.memory.append(user_input)

        # Extract and save user name if not known
        if not self.user_name:
            name = self.extract_name(user_input)
            if name:
                self.user_name = name
                return f"Nice to meet you, {self.user_name}! How can I assist you today?"

        # Check for emotions first
        emotion = self.detect_emotion(user_input)
        if emotion:
            self.last_intent = emotion
            return random.choice(RESPONSES[emotion])

        # Check for conversation history query
        if "what did we talk about" in user_input.lower():
            if self.topics:
                topics_str = ", ".join(sorted(self.topics))
                return random.choice(RESPONSES["what did we talk about"]).format(topics=topics_str)
            else:
                return "We haven't talked about much yet. What would you like to discuss?"

        # Match intent via fuzzy matching
        words = self.preprocess(user_input)
        intent = self.fuzzy_match(words)

        if intent:
            self.last_intent = intent
            # Track topics discussed excluding common small talk phrases
            if intent not in {"hello", "hi", "hey", "bye", "thank you", "thanks", "default", "help"}:
                self.topics.add(intent)

            response = RESPONSES[intent]

            # If first item in response list is callable (time/date)
            if callable(response[0]):
                return response[0]()

            # Special case for asking name if user hasn't provided it
            if intent == "name" and not self.user_name:
                return random.choice(RESPONSES["name"])

            # Small talk jokes
            if intent == "joke":
                return random.choice(RESPONSES["joke"])

            return random.choice(response)

        # Handle vague questions by repeating last intent response
        vague_triggers = {"how", "why", "tell me more", "like what", "can you explain"}
        if any(trigger in user_input.lower() for trigger in vague_triggers):
            if self.last_intent and self.last_intent in RESPONSES:
                response = RESPONSES[self.last_intent]
                return response[0]() if callable(response[0]) else random.choice(response)
            return "Could you please specify what you'd like me to explain?"

        # Default fallback with suggestions
        fallback = random.choice(RESPONSES["default"])
        suggestions = [
            "Try asking about AI, machine learning, or just say 'teach me'.",
            "You can ask for advice or the current time.",
            "If you want, I can tell you a joke or a fun fact."
        ]
        return f"{fallback} {random.choice(suggestions)}"


def main():
    bot = Chatbot()
    print("Chatbot: Hello! I'm your smart assistant. Type 'quit' to exit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {'quit', 'exit', 'bye'}:
            print("Chatbot: Goodbye! Talk to you soon.")
            break
        print("Chatbot:", bot.get_response(user_input))


if __name__ == "__main__":
    main()
