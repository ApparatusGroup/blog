from datetime import datetime
from .llm_adapter import LLMAdapter


class Drafter:
    """Creates a markdown draft from research notes.

    If an OpenRouter API key is present, the adapter will be used to produce
    a higher-quality markdown article. Otherwise a simple local template is used.
    """

    def __init__(self):
        self.llm = LLMAdapter()

    def draft(self, topic, research):
        title = f"{topic} — {datetime.utcnow().strftime('%Y-%m-%d') }"
        summary = research.get("summary", "")

        if self.llm.available():
            prompt = (
                f"You are a helpful blog writer. Produce a polished Markdown article titled '{title}'. "
                "Include a short intro, sensible section headings, and a conclusion. Use the research notes below as source material; do not invent facts.\n\n"
                f"Research notes:\n{summary}\n\nReturn only valid Markdown."
            )
            content = self.llm.generate(prompt, max_tokens=800)
            if content:
                return {"title": title, "markdown": content}

        # Fallback simple template
        body = self._expand(summary)
        md = """---
title: "{title}"
date: {date}
---

## {topic}

{summary}

{body}
""".format(title=title, date=datetime.utcnow().isoformat(), topic=topic, summary=summary or "(no summary)", body=body)
        return {"title": title, "markdown": md}

    def _expand(self, summary):
        if not summary:
            return "Further research needed."
        sentences = summary.split('. ')
        paragraphs = []
        for i, s in enumerate(sentences):
            if not s.strip():
                continue
            paragraphs.append(s.strip() + '.')
            if i % 2 == 1:
                paragraphs.append("This context highlights the main implications and open questions.")
        return "\n\n".join(paragraphs)
