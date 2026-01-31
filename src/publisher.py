import os
from pathlib import Path
import frontmatter
import markdown


class Publisher:
    """Publishes markdown articles into `public/posts` and updates `public/index.html`."""

    def __init__(self, public_dir="public"):
        self.public_dir = Path(public_dir)
        self.posts_dir = self.public_dir / "posts"
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def _slugify(self, title):
        slug = title.lower().strip().replace(' ', '-')
        return ''.join(ch for ch in slug if ch.isalnum() or ch == '-')

    def publish(self, edited):
        title = edited.get("title", "untitled")
        md_text = edited.get("markdown", "")
        post = frontmatter.loads(md_text) if md_text.strip().startswith('---') else frontmatter.Post(md_text)
        slug = self._slugify(title)
        filename = f"{slug}.md"
        filepath = self.posts_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_text)

        self._update_index()
        return str(filepath)

    def _list_posts(self):
        files = sorted(self.posts_dir.glob('*.md'), reverse=True)
        posts = []
        for p in files:
            try:
                with open(p, 'r', encoding='utf-8') as fh:
                    fm = frontmatter.load(fh)
                    title = fm.get('title') or p.stem
            except Exception:
                title = p.stem
            posts.append({'title': title, 'file': f'posts/{p.name}'})
        return posts

    def _update_index(self):
        posts = self._list_posts()
        html_items = "\n".join([f"<li><a href=\"{p['file']}\">{p['title']}</a></li>" for p in posts])
        html = f"<html><head><meta charset=\"utf-8\"><title>AI Blog</title></head><body><h1>AI Agents Blog</h1><ul>{html_items}</ul></body></html>"
        with open(self.public_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)
