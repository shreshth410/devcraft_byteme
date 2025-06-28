"""
NLP Processor for Campus Copilot
"""

import logging
from typing import Dict, Any, List
import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Handles natural language processing for Campus Copilot"""
    
    def __init__(self):
        """Initialize NLP models"""
        try:
            # Load SpaCy model for entity recognition and dependency parsing
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("SpaCy model loaded successfully.")
        except OSError:
            logger.warning("SpaCy model 'en_core_web_sm' not found. Downloading...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("SpaCy model downloaded and loaded.")
            
        # Initialize a pre-trained model for intent classification (e.g., zero-shot classification)
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        logger.info("Zero-shot classification model loaded.")
        
        # Initialize a sentence transformer for semantic search/similarity
        self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Sentence Transformer model loaded.")
        
        # Define possible intents and their keywords/phrases
        self.intents = {
            "get_schedule": ["schedule", "my classes", "timetable", "my next class", "what am i doing today"],
            "get_events": ["events", "upcoming events", "what's happening", "campus activities", "events this week"],
            "create_reminder": ["remind me", "set a reminder", "add reminder", "new reminder"],
            "get_deadlines": ["deadlines", "assignments due", "when is this due", "submission dates"],
            "find_location": ["where is", "find", "locate", "directions to", "how to get to"],
            "get_faculty_info": ["faculty", "professor", "teacher", "contact professor"],
            "get_club_info": ["clubs", "student organizations", "club activities"],
            "summarize_text": ["summarize", "condense", "shorten", "give me a summary"],
            "generate_poster": ["create poster", "make poster", "design poster", "event poster"],
            "general_greeting": ["hi", "hello", "hey", "greetings"],
            "general_thanks": ["thank you", "thanks", "appreciate it"],
            "general_unclear": ["i don't understand", "what can you do", "help me"],
        }
        
        # Pre-compute embeddings for intent phrases
        self.intent_embeddings = {intent: self.sentence_model.encode(phrases) for intent, phrases in self.intents.items()}
        
    def classify_intent(self, text: str) -> str:
        """Classify the user's intent based on their input"""
        text_embedding = self.sentence_model.encode([text])
        
        max_similarity = -1
        predicted_intent = "general_unclear"
        
        for intent, embeddings in self.intent_embeddings.items():
            similarity = cosine_similarity(text_embedding, embeddings).mean()
            if similarity > max_similarity:
                max_similarity = similarity
                predicted_intent = intent
                
        # Use zero-shot classification as a fallback or for fine-grained classification
        # This can be more robust for intents not explicitly covered by keywords
        candidate_labels = list(self.intents.keys())
        if max_similarity < 0.5: # Threshold for keyword-based similarity
            zero_shot_result = self.classifier(text, candidate_labels)
            predicted_intent = zero_shot_result["labels"][0]
            logger.info(f"Zero-shot classification result: {zero_shot_result}")
            
        logger.info(f"Classified intent: {predicted_intent} (Similarity: {max_similarity:.2f})")
        return predicted_intent
        
    def extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract entities from the user's input based on the classified intent"""
        doc = self.nlp(text)
        entities = {}
        
        if intent == "find_location" or intent == "get_directions":
            # Look for GPE (Geo-Political Entity), LOC (Location), ORG (Organization) entities
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC", "ORG", "FAC"]: # FAC for facilities
                    entities["location"] = ent.text
                    break
            if not entities.get("location"):
                # Fallback to looking for common location keywords if no named entity
                location_keywords = ["library", "gym", "cafeteria", "building", "hall", "room"]
                for token in doc:
                    if token.text.lower() in location_keywords:
                        entities["location"] = text # Take the whole text as location for now
                        break
                
        elif intent == "create_reminder":
            # Extract time, date, and reminder content
            # This is a simplified example; a real implementation would need a robust date/time parser
            for token in doc:
                if token.like_num and ("hour" in token.nbor().text or "min" in token.nbor().text):
                    entities["duration"] = f"{token.text} {token.nbor().text}"
                if "tomorrow" in token.text.lower():
                    entities["date"] = "tomorrow"
                if "today" in token.text.lower():
                    entities["date"] = "today"
            
            # Simple extraction of reminder text (everything after 


            if "remind me to " in text.lower():
                reminder_text = text.lower().split("remind me to ", 1)[1]
                entities["reminder_text"] = reminder_text
        elif intent == "create_event":
            # Extract event title, date, time, duration, location
            # This is a placeholder; a full implementation would use more advanced parsing
            if "title:" in text:
                entities["title"] = text.split("title:", 1)[1].split("\n")[0].strip()
            if "date:" in text:
                entities["date"] = text.split("date:", 1)[1].split("\n")[0].strip()
            if "time:" in text:
                entities["time"] = text.split("time:", 1)[1].split("\n")[0].strip()
            if "duration:" in text:
                entities["duration"] = text.split("duration:", 1)[1].split("\n")[0].strip()
            if "location:" in text:
                entities["location"] = text.split("location:", 1)[1].split("\n")[0].strip()
            if "description:" in text:
                entities["description"] = text.split("description:", 1)[1].split("\n")[0].strip()
                
        logger.info(f"Extracted entities: {entities}")
        return entities
        
    def process_query(self, text: str) -> Dict[str, Any]:
        """Process a user query to determine intent and extract entities"""
        intent = self.classify_intent(text)
        entities = self.extract_entities(text, intent)
        
        return {
            "intent": intent,
            "entities": entities,
            "original_text": text
        }


# Example Usage (for testing)
if __name__ == "__main__":
    nlp_processor = NLPProcessor()
    
    queries = [
        "What is my schedule for tomorrow?",
        "Show me upcoming events this week",
        "Remind me to submit my essay at 5 PM today",
        "Where is the main library?",
        "How do I get to the computer science building?",
        "Summarize this article for me",
        "Create a poster for the spring festival",
        "Hello bot",
        "Thanks for your help",
        "I need help with something else"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = nlp_processor.process_query(query)
        print("Intent: {}".format(result["intent"]))
        print("Entities: {}".format(result["entities"]))


