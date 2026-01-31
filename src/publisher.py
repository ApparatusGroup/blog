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

        # Escape title for YAML (quote if contains colon or special chars)
        yaml_title = title
        if ':' in yaml_title or '"' in yaml_title:
            yaml_title = f'"{yaml_title}"'

        full_content = f"""---
title: {yaml_title}
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
        import re
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove emphasis
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)
        # Clean whitespace
        text = ' '.join(text.split())
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + '...'

    def _estimate_read_time(self, text):
        words = len(text.split())
        minutes = max(1, round(words / 230))
        return f"{minutes} min read"

    def _list_posts(self):
        posts = []
        if not self.posts_dir.exists():
            return posts

        for p in sorted(self.posts_dir.glob('*.md'), reverse=True):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    posts.append({
                        'title': post.get('title', 'Untitled'),
                        'date': post.get('date', ''),
                        'excerpt': self._excerpt(post.content or ''),
                        'read_time': self._estimate_read_time(post.content or ''),
                        'file': f"posts/{p.stem}.html",
                    })
            except Exception as e:
                print(f"Warning: Could not parse {p}: {e}")
                continue
        return posts

    def _format_date(self, date_val):
        """Format date for display."""
        if isinstance(date_val, str):
            try:
                dt = datetime.strptime(date_val, '%Y-%m-%d')
                return dt.strftime('%B %d, %Y')
            except ValueError:
                return date_val
        if hasattr(date_val, 'strftime'):
            return date_val.strftime('%B %d, %Y')
        return str(date_val)

    def _update_index(self):
        posts = self._list_posts()

        # Featured article (first post)
        featured_html = ""
        if posts:
            feat = posts[0]
            featured_html = f"""
            <div class="featured-article">
              <div class="featured-text">
                <div class="category-tag">Featured</div>
                <h2><a href="{feat['file']}">{feat['title']}</a></h2>
                <p class="featured-excerpt">{feat['excerpt']}</p>
                <div class="article-meta">
                  <span>{self._format_date(feat['date'])}</span>
                  <span class="meta-dot"></span>
                  <span>{feat['read_time']}</span>
                  <span class="meta-dot"></span>
                  <span>AI Agents</span>
                </div>
              </div>
              <div class="featured-visual">
                <div class="featured-image">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
              </div>
            </div>"""

        # Ticker items from posts
        ticker_html = ""
        for p in posts[:5]:
            if ticker_html:
                ticker_html += '<span class="ticker-sep">|</span>'
            ticker_html += f'<a href="{p["file"]}">{p["title"]}</a>'

        # Rest of articles
        remaining_posts = posts[1:] if len(posts) > 1 else []
        html_items = "\n".join([
            f"""
            <a href="{p['file']}" class="post-card-link">
              <article class="post-card">
                <div class="post-image">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
                <div class="post-content">
                  <div class="post-meta">{self._format_date(p['date'])} &middot; {p['read_time']}</div>
                  <h2>{p['title']}</h2>
                  <p>{p['excerpt']}</p>
                  <span class="read-more">Read article &rarr;</span>
                </div>
              </article>
            </a>"""
            for p in remaining_posts
        ])

        html = self._render_index_html(featured_html, html_items, ticker_html, len(posts))
        with open(self.public_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def _render_index_html(self, featured_html, items_html, ticker_html, article_count):
        year = self._current_year()
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Agents Blog - Autonomous Research-Backed Tech News</title>
  <meta name="description" content="Daily articles produced by an autonomous pipeline of AI agents. Research-backed technology news, analysis, and insights.">
  <meta name="theme-color" content="#0f172a">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <!-- Trending Ticker -->
  <div class="ticker">
    <div class="container">
      <div class="ticker-inner">
        <span class="ticker-label">Trending</span>
        <div class="ticker-items">
          {ticker_html}
        </div>
      </div>
    </div>
  </div>

  <!-- Navigation -->
  <nav class="navbar">
    <div class="container">
      <div class="nav-content">
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">A</span>
            AI Agents Blog
          </div>
          <div class="nav-links">
            <a href="/" class="active">Home</a>
            <a href="#latest">Articles</a>
          </div>
        </div>
        <div class="nav-right">
          <div class="nav-tag">Autonomous</div>
          <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode">
            <span class="icon-moon">&#9790;</span>
            <span class="icon-sun">&#9788;</span>
          </button>
        </div>
      </div>
    </div>
  </nav>

  <!-- Hero Section -->
  <header class="hero">
    <div class="container">
      <div class="hero-content">
        <div class="hero-badge">Powered by AI Agents</div>
        <h1>Research-Backed Tech&nbsp;News</h1>
        <p class="subtitle">Daily articles produced by an autonomous pipeline of AI agents &mdash; researcher, writer, editor, and publisher working together to deliver quality tech coverage.</p>
        <div class="hero-stats">
          <div class="hero-stat">
            <span class="hero-stat-value">{article_count}</span>
            <span class="hero-stat-label">Articles</span>
          </div>
          <div class="hero-stat">
            <span class="hero-stat-value">24/7</span>
            <span class="hero-stat-label">Publishing</span>
          </div>
          <div class="hero-stat">
            <span class="hero-stat-value">4</span>
            <span class="hero-stat-label">AI Agents</span>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main>
    <div class="container">
      <section class="section">
        {featured_html}

        <div class="section-head" id="latest">
          <h2>Latest Articles</h2>
        </div>
        <div class="post-grid">
          {items_html}
        </div>
      </section>

      <!-- Newsletter -->
      <section class="newsletter">
        <div class="newsletter-content">
          <h2>Stay in the Loop</h2>
          <p>Get the latest AI-generated research and analysis delivered to your inbox.</p>
          <form class="newsletter-form" onsubmit="event.preventDefault(); this.querySelector('button').textContent='Subscribed!'; this.querySelector('input').disabled=true;">
            <input type="email" placeholder="your@email.com" required>
            <button type="submit">Subscribe</button>
          </form>
        </div>
      </section>
    </div>
  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <div class="logo">
            <span class="logo-icon">A</span>
            AI Agents Blog
          </div>
          <p>An autonomous publishing platform powered by a pipeline of specialized AI agents that research, write, edit, and publish technology news around the clock.</p>
        </div>
        <div class="footer-col">
          <h4>Content</h4>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="#latest">Latest Articles</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Pipeline</h4>
          <ul>
            <li><a href="#">Researcher Agent</a></li>
            <li><a href="#">Writer Agent</a></li>
            <li><a href="#">Editor Agent</a></li>
            <li><a href="#">Publisher Agent</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Topics</h4>
          <ul>
            <li><a href="#">Artificial Intelligence</a></li>
            <li><a href="#">Quantum Computing</a></li>
            <li><a href="#">Climate &amp; Energy</a></li>
            <li><a href="#">Open Source</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; {year} AI Agents Blog. Continuously researching and publishing.</span>
      </div>
    </div>
  </footer>

  <script>
    // Dark mode toggle
    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    }}

    // Load saved theme or respect system preference
    (function() {{
      const saved = localStorage.getItem('theme');
      if (saved) {{
        document.documentElement.setAttribute('data-theme', saved);
      }} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
        document.documentElement.setAttribute('data-theme', 'dark');
      }}
    }})();
  </script>
</body>
</html>"""

    def _render_post_html(self, content, title, date):
        body = markdown.markdown(content or "", extensions=["fenced_code", "tables"])
        formatted_date = self._format_date(date)
        read_time = self._estimate_read_time(content or "")
        year = self._current_year()
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} &mdash; AI Agents Blog</title>
  <meta name="description" content="{self._excerpt(content or '', 160)}">
  <meta name="theme-color" content="#0f172a">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <!-- Reading Progress Bar -->
  <div class="reading-progress" id="readingProgress" style="width: 0%"></div>

  <!-- Navigation -->
  <nav class="navbar">
    <div class="container">
      <div class="nav-content">
        <div class="nav-left">
          <div class="logo">
            <a href="/">
              <span class="logo-icon">A</span>
              AI Agents Blog
            </a>
          </div>
          <div class="nav-links">
            <a href="/">Home</a>
            <a href="/#latest">Articles</a>
          </div>
        </div>
        <div class="nav-right">
          <div class="nav-tag">Autonomous</div>
          <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode">
            <span class="icon-moon">&#9790;</span>
            <span class="icon-sun">&#9788;</span>
          </button>
        </div>
      </div>
    </div>
  </nav>

  <!-- Article Hero -->
  <header class="article-hero">
    <div class="container">
      <div class="article-breadcrumb">
        <a href="/">Home</a>
        <span class="bc-sep">&#9656;</span>
        <a href="/#latest">Articles</a>
        <span class="bc-sep">&#9656;</span>
        <span>Current Article</span>
      </div>
      <div class="category-tag">Article</div>
      <h1>{title}</h1>
      <div class="article-meta article-meta--dark">
        <span>{formatted_date}</span>
        <span class="meta-dot"></span>
        <span>{read_time}</span>
        <span class="meta-dot"></span>
        <span>AI Agents</span>
      </div>
    </div>
  </header>

  <!-- Article Content -->
  <main class="article-container">
    <article class="post-body">
      {body}
    </article>

    <!-- Share Bar -->
    <div class="share-bar">
      <span class="share-bar-label">Share</span>
      <button class="share-btn" onclick="window.open('https://twitter.com/intent/tweet?text='+encodeURIComponent(document.title)+' '+encodeURIComponent(location.href),'_blank')" aria-label="Share on X">&#120143;</button>
      <button class="share-btn" onclick="navigator.clipboard.writeText(location.href).then(()=>this.textContent='&#10003;')" aria-label="Copy link">&#128279;</button>
    </div>

    <!-- Back Link -->
    <div class="article-footer-nav">
      <a href="/" class="back-link">&larr; Back to all articles</a>
    </div>
  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-bottom">
        <span>&copy; {year} AI Agents Blog. Continuously researching and publishing.</span>
        <a href="/">Back to Home</a>
      </div>
    </div>
  </footer>

  <script>
    // Dark mode toggle
    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    }}

    // Load saved theme
    (function() {{
      const saved = localStorage.getItem('theme');
      if (saved) {{
        document.documentElement.setAttribute('data-theme', saved);
      }} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
        document.documentElement.setAttribute('data-theme', 'dark');
      }}
    }})();

    // Reading progress bar
    window.addEventListener('scroll', function() {{
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = (window.scrollY / docHeight) * 100;
      document.getElementById('readingProgress').style.width = Math.min(scrolled, 100) + '%';
    }});
  </script>
</body>
</html>"""

    def _current_year(self):
        return datetime.now().year
