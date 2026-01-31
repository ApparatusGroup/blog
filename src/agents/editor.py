class Editor:
    """Performs lightweight editing on markdown text.

    Swap this for an LLM-based editor or an external grammar/fact-checking tool.
    """

    def edit(self, draft):
        md = draft.get("markdown", "")
        md = self._fix_whitespace(md)
        md = self._ensure_newlines(md)
        # Try LLM-based polishing if available
        try:
            from .llm_adapter import LLMAdapter
            llm = LLMAdapter()
            if llm.available():
                prompt = (
                    "You are a markdown editor. Improve clarity, grammar, and style of the following Markdown. "
                    "Do not add factual claims. Return only the improved Markdown.\n\n" + md
                )
                out = llm.generate(prompt, max_tokens=500)
                if out:
                    md = out
        except Exception:
            pass

        return {"title": draft.get("title", "untitled"), "markdown": md}

    def _fix_whitespace(self, text):
        return "\n".join(line.rstrip() for line in text.splitlines())

    def _ensure_newlines(self, text):
        # ensure two newlines between paragraphs
        return text.replace('\n\n\n', '\n\n')
