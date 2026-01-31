import wikipedia


class Researcher:
    """Fetches concise research summaries for a topic using the wikipedia package.

    This is a simple stand-in for a more advanced research agent that might query multiple
    sources, scrape pages, and produce structured notes.
    """

    def research(self, topic, sentences=5):
        try:
            summary = wikipedia.summary(topic, sentences=sentences, auto_suggest=True)
            return {"topic": topic, "summary": summary}
        except Exception:
            return {"topic": topic, "summary": ""}
