# AI Agents Blog

An autonomous blog where AI agents research, write, and publish tech news articles daily.

## 🚀 Live Site

**Public Blog**: https://blog-mu-opal-43.vercel.app  
**Admin Dashboard**: https://blog-mu-opal-43.vercel.app/admin.html

## ✨ Features

### Public Site
- **Professional TechCrunch-inspired design** with vibrant green accent
- **Featured article** prominently displayed
- **Card-based grid** for additional articles
- **Fully clickable cards** - click anywhere to read
- **Clean excerpts** - no markdown syntax visible
- **Mobile responsive** design
- **10 professional tech articles** covering AI, space, health, and more

### Admin Dashboard 🔒
- **Firebase Authentication** - Secure admin login
- **Research & Generate** - Tell AI what topic to research and publish
- **Upload Research** - Paste your content, AI formats it professionally
- **Schedule Posts** - Queue articles for future publication
- **Manage Articles** - View and delete published posts
- **Real-time stats** - Track total articles, scheduled posts, research queue

## 🤖 AI Pipeline

```
Researcher → Drafter → Editor → Publisher
```

1. **Researcher** - Gathers information from Wikipedia
2. **Drafter** - Creates article using OpenRouter API (optional) or template
3. **Editor** - Polishes content with LLM (optional)
4. **Publisher** - Generates HTML and updates site

## 🛠️ Tech Stack

- **Backend**: Python 3.12
- **AI**: OpenRouter API (optional), Wikipedia API
- **Frontend**: Vanilla JS, Modern CSS
- **Auth**: Firebase Authentication
- **Database**: Firestore
- **Hosting**: Vercel
- **Automation**: GitHub Actions + Vercel Cron

## 📦 Setup

### Quick Start

```bash
# Clone the repo
git clone https://github.com/ApparatusGroup/blog.git
cd blog

# Install Python dependencies
pip install -r requirements.txt

# Generate articles
python -m src.main

# View locally
npm run dev
# Visit http://localhost:8000
```

### Admin Dashboard Setup

See [ADMIN_SETUP.md](ADMIN_SETUP.md) for complete Firebase configuration guide.

**Quick steps:**
1. Create Firebase project at https://console.firebase.google.com
2. Enable Email/Password authentication
3. Create admin user in Firebase console
4. Enable Firestore database
5. Copy Firebase config to `public/admin.html` (line 287)
6. Deploy and access at `/admin.html`

## 🔧 Configuration

### Environment Variables (Optional)

```bash
# .env
OPENROUTER_API_KEY=your_key_here  # For LLM-powered drafting
```

### Topics

Edit `config/topics.txt` to customize research topics:
```
Artificial intelligence
Quantum computing
Space exploration
```

## 📁 Project Structure

```
.
├── api/
│   ├── cron.js              # Daily rebuild trigger
│   ├── generate-article.js  # Admin: generate from topic
│   └── upload-research.js   # Admin: publish from content
├── config/
│   └── topics.txt           # Research topics
├── public/
│   ├── admin.html           # Admin dashboard ⭐
│   ├── index.html           # Homepage
│   ├── styles.css           # Site styles
│   └── posts/               # Generated articles
├── src/
│   ├── agents/
│   │   ├── researcher.py    # Wikipedia research
│   │   ├── drafter.py       # Article generation
│   │   ├── editor.py        # Content polishing
│   │   └── llm_adapter.py   # OpenRouter API
│   ├── orchestrator.py      # Pipeline coordinator
│   ├── publisher.py         # HTML generation
│   ├── scheduler.py         # Scheduling logic
│   └── main.py              # Entry point
├── static/
│   └── styles.css           # Source CSS
├── create_placeholders.py   # Generate demo articles
├── ADMIN_SETUP.md          # Admin setup guide
└── vercel.json              # Vercel config
```

## 🎯 Admin Features

### 1. Research & Generate
Tell AI what to research:
```
Input: "Robotics in Healthcare"
Output: Fully researched and formatted article published to site
```

### 2. Upload Research
Have your own content? Paste it:
```
Title: "My Research Topic"
Content: [Your research notes or article]
Output: AI formats it professionally and publishes
```

### 3. Schedule Posts
Queue articles for future:
```
Topic: "Future of Transportation"
Date: 2026-02-15 at 10:00 AM
Output: Article auto-generates and publishes at scheduled time
```

## 🔐 Security

- Admin dashboard protected by Firebase Authentication
- Only authenticated users can access admin features
- API endpoints verify authentication (in production setup)
- Firestore security rules restrict data access

## 📝 License

MIT

## 🎯 Roadmap

- [x] Professional TechCrunch-inspired design
- [x] Firebase admin authentication
- [x] Research & generate articles
- [x] Upload custom content
- [x] Schedule future posts
- [ ] Add article categories/tags
- [ ] Implement draft/publish workflow
- [ ] Add image generation for articles
- [ ] Create analytics dashboard
- [ ] Support multiple admin roles
- [ ] Add bulk article generation
- [ ] Implement content versioning
- [ ] SEO optimization tools

---

**Built with ❤️ using AI agents**
