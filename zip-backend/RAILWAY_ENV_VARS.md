# Railway Backend Environment Variables

Add ALL of these in Railway dashboard → Service → Variables

```
DEBUG=false
ALLOWED_ORIGINS=["https://your-frontend-url.railway.app","https://your-custom-domain.com"]
NEWSAPI_KEY=your_key
YOUTUBE_API_KEY=your_key
LISTENNOTES_API_KEY=your_key
SPOTIFY_CLIENT_ID=your_key
SPOTIFY_CLIENT_SECRET=your_key
SERPAPI_KEY=your_key
FACEBOOK_APP_ID=your_key
FACEBOOK_APP_SECRET=your_key
REDIS_URL=your_railway_redis_url
PINATA_API_KEY=
PINATA_SECRET_KEY=
```

**Note:** Replace `your_key` with actual API keys. For REDIS_URL, use the connection string from your Railway Redis service.
