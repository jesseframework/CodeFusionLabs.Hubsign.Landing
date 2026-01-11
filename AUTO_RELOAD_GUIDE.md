# Auto-Reload Setup Guide

## What's Installed

**django-browser-reload** - Automatically refreshes your browser when files change (no more manual refresh needed!)

## How It Works

The server now watches for changes in:
- ✅ **Python files** (.py) - templates, views, settings
- ✅ **Static files** (CSS, JavaScript) 
- ✅ **Template files** (.html)

When you save ANY of these files, your browser will **automatically reload** within 1-2 seconds.

## What Was Configured

### 1. Added to `requirements.txt`:
```
django-browser-reload>=1.12.1
```

### 2. Added to `INSTALLED_APPS` in `hubsign/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'django_browser_reload',
    ...
]
```

### 3. Added to `MIDDLEWARE` in `hubsign/settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',  # ← Added this
    ...
]
```

### 4. Added to `hubsign/urls.py`:
```python
if settings.DEBUG:
    urlpatterns = [
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
```

## Testing Auto-Reload

1. **Open your browser** to http://127.0.0.1:8000
2. **Open** `static/js/main.js` in your editor
3. **Make a small change** (add a comment, change a string)
4. **Save the file** (Cmd+S / Ctrl+S)
5. **Watch your browser** - it should refresh automatically within 1-2 seconds! 🎉

## No More Manual Refresh Needed!

You **no longer need** to do:
- ❌ Hard refresh (Cmd+Shift+R)
- ❌ Clear cache
- ❌ Close and reopen browser

Just **save your file** and the browser updates automatically!

## Server Status

✅ **Server is running** at http://127.0.0.1:8000  
✅ **Auto-reload is enabled** (django-browser-reload active)  
✅ **Watching for file changes** with StatReloader

## How to Restart Server

If you need to restart manually:

```bash
cd /Users/jgray/Documents/GitHub/CodeFusionLabs.Hubsign.Landing
./start.sh
```

Or use the shortcut:
```bash
./start.sh
```

---

**Note**: Auto-reload only works in development mode (`DEBUG=True`). In production, this middleware is automatically disabled for security and performance.
