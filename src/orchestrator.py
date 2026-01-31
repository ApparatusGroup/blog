import random
from agents.researcher import Researcher
from agents.drafter import Drafter
from agents.editor import Editor
from publisher import Publisher


class Orchestrator:
    """Runs a single pipeline pass: research -> draft -> edit -> publish."""

    def __init__(self, topics_file="config/topics.txt"):
        self.topics_file = topics_file
        self.researcher = Researcher()
        self.drafter = Drafter()
        self.editor = Editor()
        self.publisher = Publisher()

    def _load_topics(self):
        try:
            with open(self.topics_file, "r", encoding="utf-8") as f:
                topics = [line.strip() for line in f if line.strip()]
            return topics
        except FileNotFoundError:
            return ["Artificial intelligence", "Climate change", "Quantum computing"]

    def choose_topic(self):
        topics = self._load_topics()
        return random.choice(topics) if topics else None

    def run_once(self):
        topic = self.choose_topic()
        if not topic:
            return None

        research = self.researcher.research(topic)
        draft = self.drafter.draft(topic, research)
        edited = self.editor.edit(draft)
        path = self.publisher.publish(edited)
        return path
