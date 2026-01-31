import shutil
from pathlib import Path
import markdown
import frontmatter
from datetime import datetime

class Publisher:
    def __init__(self):
        self.public_dir = Path('public')
        self.posts_dir = self.public_dir / 'posts'
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self._copy_static_assets()

    def _copy_static_assets(self):
        static_dir = Path('static')
        if static_dir.exists():
            for item in static_dir.iterdir():
                dest = self.public_dir / item.name
                if item.is_file():
                    shutil.copy2(item, dest)

    def publish(self, edited_data):
        # edited_data is a dict with 'title' and 'markdown'
        title = edited_data.get('title', 'Untitled')
        content = edited_data.get('markdown', '')
        
        # Create frontmatter content
        date_str = datetime.now().strftime('%Y-%m-%d')
        full_content = f"""---
title: {title}
date: {date_str}
---

{content}
"""
        
        slug = self._slugify(title)
        
        md_filename = f"{slug}.md"
        html_filename = f"{slug}.html"
        
        md_filepath = self.posts_dir / md_filename
        html_filepath = self.posts_dir / html_filename
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        html_content = self._render_post_html(content, title, date_str)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self._update_index()
        print(f"Published: {html_filepath}")
        return html_filepath

    def _slugify(self, title):
        import re
        slug = title.lower().strip()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def _excerpt(self, text, length=150):
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + '...'

    def _list_posts(self):
        posts = []
        for p in sorted(self.posts_dir.glob('*.md'), reverse=True):
            with open(p, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                posts.append({
                    'title': post.get('title', 'Untitled'),
                    'date': post.get('date', ''),
                    'excerpt': self._excerpt(post.content or ''),
                    'file': f"posts/{p.stem}.html",
                })
        return posts

    def _update_index(self):
        posts = self._list_posts()
        
        # Featured article (first post)
        featured_html = ""
        if posts:
            feat = posts[0]
            featured_html = f"""
            <div class="featured-article">
              <div class="featured-image">📰</div>
              <div class="category-tag">FEATURED</div>
              <h2><a href="{feat['file']}">{feat['title']}</a></h2>
              <p class="featured-excerpt">{feat['excerpt']}</p>
              <div class="article-meta">
                <span>{feat['date']}</span>
                <span>•</span>
                <span>AI Agents</span>
              </div>
            </div>
            """
        
        # Rest of articles
        remaining_posts = posts[1:] if len(posts) > 1 else []
        html_items = "\n".join([
            """
            <article class="post-card">
              <div class="post-image">📝</div>
              <div class="post-content">
                <div class="post-meta">{date}</div>
                <h2><a href="{file}">{title}</a></h2>
                <p>{excerpt}</p>
                <a class="read-more" href="{file}">Read article →</a>
              </div>
            </article>
            """.format(date=p['date'], file=p['file'], title=p['title'], excerpt=p['excerpt']) 
            for p in remaining_posts
        ])

        html = self._render_index_html(featured_html, html_items)
        with open(self.public_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def _render_index_html(self, featured_html, items_html):
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Agents Blog - Research-Backed Tech News</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav class="navbar">
    <div class="container">
      <div class="nav-content">
        <div class="logo">AI Agents Blog</div>
        <div class="nav-tag">AUTONOMOUS</div>
      </div>
    </div>
  </nav>

  <header class="hero">
    <div class="container">
      <h1>Research-Backed Tech News</h1>
      <p class="subtitle">Daily articles produced by an autonomous pipeline of AI agents: researcher → writer → editor → publisher.</p>
    </div>
  </header>

  <main class="container">
    <section class="section">
      {featured_html}
      
      <div class="section-head">
        <h2>Latest Articles</h2>
      </div>
      <div class="post-grid">
        {items_html}
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="container">
      <p>© {self._current_year()} AI Agents Blog • Continuously researching and publishing</p>
    </div>
  </footer>
</body>
</html>"""

    def _render_post_html(self, content, title, date):
        body = markdown.markdown(content or "", extensions=["fenced_code", "tables"])
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} • AI Agents Blog</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav class="navbar">
    <div class="container">
      <div class="nav-content">
        <div class="logo"><a href="/">AI Agents Blog</a></div>
        <div class="nav-tag">AUTONOMOUS</div>
      </div>
    </div>
  </nav>

  <header class="hero">
    <div class="container">
      <div class="category-tag">ARTICLE</div>
      <h1>{title}</h1>
      <div class="article-meta">
        <span>{date}</span>
        <span>•</span>
        <span>AI Agents</span>
      </div>
    </div>
  </header>

  <main class="container">
    <article class="post-body">
      {body}
    </article>
  </main>

  <footer class="footer">
    <div class="container">
      <p><a href="/">← Back to all articles</a></p>
    </div>
  </footer>
</body>
</html>"""

    def _current_year(self):
        return datetime.now().year
