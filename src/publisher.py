import os
from pathlib import Path
import frontmatter
import markdown
import shutil


class Publisher:
    """Publishes markdown articles into `public/posts` and updates `public/index.html`."""

    def __init__(self, public_dir="public"):
        self.public_dir = Path(public_dir)
        self.posts_dir = self.public_dir / "posts"
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self._copy_static_assets()

    def _slugify(self, title):
        slug = title.lower().strip().replace(' ', '-')
        return ''.join(ch for ch in slug if ch.isalnum() or ch == '-')

    def _copy_static_assets(self):
        """Copy CSS and static assets to public directory."""
        static_dir = Path(__file__).parent.parent / "static"
        if static_dir.exists():
            for item in static_dir.glob('*'):
                if item.is_file():
                    shutil.copy2(item, self.public_dir / item.name)

    def publish(self, edited):
        title = edited.get("title", "untitled")
        md_text = edited.get("markdown", "")
        post = frontmatter.loads(md_text) if md_text.strip().startswith('---') else frontmatter.Post(md_text)
        slug = self._slugify(title)
        md_filename = f"{slug}.md"
        md_filepath = self.posts_dir / md_filename
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(md_text)

        html_filename = f"{slug}.html"
        html_filepath = self.posts_dir / html_filename
        html = self._render_post_html(post, title)
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html)

        self._update_index()
        return str(html_filepath)

    def _list_posts(self):
        files = sorted(self.posts_dir.glob('*.md'), reverse=True)
        posts = []
        for p in files:
            try:
                with open(p, 'r', encoding='utf-8') as fh:
                    fm = frontmatter.load(fh)
                    title = fm.get('title') or p.stem
                    date = fm.get('date') or ''
                    content = (fm.content or '').strip()
                    excerpt = (content[:220] + '...') if len(content) > 220 else content
            except Exception:
                title = p.stem
                date = ''
                excerpt = ''
            posts.append({
                'title': title,
                'date': str(date),
                'excerpt': excerpt,
                'file': f"posts/{p.stem}.html",
            })
        return posts

    def _update_index(self):
        posts = self._list_posts()
        html_items = "\n".join([
            """
            <article class="post-card">
              <div class="post-meta">{date}</div>
              <h2><a href="{file}">{title}</a></h2>
              <p>{excerpt}</p>
              <a class="read-more" href="{file}">Read article →</a>
            </article>
            """.format(date=p['date'], file=p['file'], title=p['title'], excerpt=p['excerpt'])
            for p in posts
        ])

        html = self._render_index_html(html_items)
        with open(self.public_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def _render_index_html(self, items_html):
        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>AI Agents Blog</title>
  <link rel=\"stylesheet\" href=\"/styles.css\">
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">
</head>
<body>
  <header class=\"hero\">
    <div class=\"container\">
      <div class=\"pill\">Autonomous Research • Daily Publishing</div>
      <h1>AI Agents Blog</h1>
      <p class=\"subtitle\">Research‑backed articles produced by a pipeline of AI agents: researcher → writer → editor → publisher.</p>
      <div class=\"hero-actions\">
        <a class=\"btn primary\" href=\"#latest\">Browse Latest</a>
        <a class=\"btn ghost\" href=\"/posts\">Post Archive</a>
      </div>
    </div>
  </header>

  <main class=\"container\" id=\"latest\">
    <section class=\"section\">
      <div class=\"section-head\">
        <h2>Latest articles</h2>
        <span class=\"muted\">Updated daily</span>
      </div>
      <div class=\"post-grid\">
        {items_html}
      </div>
    </section>
  </main>

  <footer class=\"footer\">
    <div class=\"container\">
      <p>© {self._current_year()} AI Agents Blog • Built for continuous research and publishing.</p>
    </div>
  </footer>
</body>
</html>"""

    def _render_post_html(self, post, title):
        body = markdown.markdown(post.content or "", extensions=["fenced_code", "tables"])
        date = post.get('date') or ''
        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title} • AI Agents Blog</title>
  <link rel=\"stylesheet\" href=\"/styles.css\">
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">
</head>
<body>
  <header class=\"post-hero\">
    <div class=\"container\">
      <a class=\"back-link\" href=\"/\">← Back to home</a>
      <h1>{title}</h1>
      <div class=\"post-meta\">{date}</div>
    </div>
  </header>

  <main class=\"container post-body\">
    {body}
  </main>

  <footer class=\"footer\">
    <div class=\"container\">
      <p>© {self._current_year()} AI Agents Blog</p>
    </div>
  </footer>
</body>
</html>"""

    def _current_year(self):
        from datetime import datetime
        return datetime.utcnow().year
