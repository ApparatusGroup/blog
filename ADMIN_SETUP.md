# Admin Dashboard Setup Guide

## Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Name it "ai-agents-blog" (or your preferred name)
4. Disable Google Analytics (optional)
5. Click "Create project"

### 2. Enable Authentication

1. In your Firebase project, go to **Build** → **Authentication**
2. Click "Get started"
3. Click "Email/Password" under Sign-in method
4. Enable "Email/Password"
5. Click "Save"

### 3. Create Admin User

1. Go to **Authentication** → **Users** tab
2. Click "Add user"
3. Enter your admin email and password
4. Click "Add user"

### 4. Enable Firestore Database

1. Go to **Build** → **Firestore Database**
2. Click "Create database"
3. Choose "Start in production mode"
4. Select your region (closest to you)
5. Click "Enable"

### 5. Set Firestore Rules

Go to **Firestore** → **Rules** tab and update rules:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated users can read/write
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
    
    // Scheduled posts collection
    match /scheduledPosts/{postId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

Click "Publish"

### 6. Get Firebase Configuration

1. Go to **Project Settings** (gear icon)
2. Scroll down to "Your apps"
3. Click the web icon `</>`
4. Name your app "Admin Dashboard"
5. Click "Register app"
6. Copy the `firebaseConfig` object

### 7. Update Admin Dashboard

Open `public/admin.html` and replace the Firebase config (around line 287):

```javascript
const firebaseConfig = {
  apiKey: "YOUR_ACTUAL_API_KEY",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};
```

## Accessing the Admin Dashboard

### Local Development

```bash
# Install dependencies
npm install

# Start local server
npm run dev
```

Visit: http://localhost:8000/admin.html

### Production

After deploying to Vercel, visit:
https://your-domain.vercel.app/admin.html

## Login Credentials

Use the email and password you created in Firebase Authentication (Step 3).

## Features

### 1. Research & Generate Article
- Enter a topic (e.g., "Robotics in Healthcare")
- AI will research using Wikipedia and generate a professional article
- Article is automatically published

### 2. Upload Research Content
- Paste your own research notes or article draft
- AI will format it into a professional blog post
- Useful for curated content or specific research you've done

### 3. Schedule Future Posts
- Enter a topic and future date/time
- Post will be automatically researched and published at that time
- View and manage all scheduled posts

### 4. Manage Published Articles
- View all published articles
- Quick links to view articles
- Delete articles if needed

## Backend API Endpoints

The admin dashboard calls these API endpoints:

- `POST /api/generate-article` - Generates article from topic
- `POST /api/upload-research` - Publishes article from provided content
- `POST /api/cron` - Checks for scheduled posts (runs daily)

## Security Notes

1. **Never commit your Firebase config with real credentials**
2. Keep your admin email/password secure
3. In production, implement proper Firebase token verification in API routes
4. Consider adding IP whitelisting for admin routes
5. Set up Firestore security rules properly

## Troubleshooting

### "Cannot connect to Firebase"
- Check that your Firebase config is correct
- Verify Firebase project is active
- Check browser console for detailed errors

### "Authentication failed"
- Verify you created a user in Firebase Authentication
- Double-check email and password
- Ensure Email/Password sign-in method is enabled

### "Article generation failed"
- Check Vercel function logs
- Verify Python dependencies are installed
- Check that topics.txt exists in config/

## Next Steps

Consider adding:
- Bulk article generation
- Analytics dashboard
- Content categories/tags
- Image upload for articles
- Draft/publish workflow
- User roles (admin, editor, viewer)
