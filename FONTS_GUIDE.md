# 🎨 HubSign Font Guide

Your fonts have been updated to use **modern, professional Google Fonts** that are free and widely used by enterprise SaaS companies.

## ✅ Current Fonts (Updated)

### Display Font (Headings)
**Plus Jakarta Sans** - Modern, geometric sans-serif
- Used by: Notion, Linear, Stripe
- Excellent for headlines and brand text
- Professional yet friendly

### Body Font (Text)
**Inter** - Designed specifically for screens
- Used by: GitHub, Vercel, Mozilla
- Optimized for readability at all sizes
- Clean, professional appearance

## 🎯 Why These Fonts?

| Feature | Plus Jakarta Sans | Inter |
|---------|------------------|-------|
| **Type** | Display/Heading | Body/UI Text |
| **Style** | Slightly rounded, modern | Neutral, highly readable |
| **Best For** | Titles, CTAs, branding | Paragraphs, buttons, forms |
| **Performance** | Loaded from Google CDN | Loaded from Google CDN |

## 🔄 Alternative Font Options

### Option 1: System Fonts (Best Performance)
Use native OS fonts for instant loading:

```css
/* In static/css/main.css */
:root {
    --font-display: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}
```

**Pros:** Instant load, no network requests, native feel  
**Cons:** Less brand personality

### Option 2: Other Modern Google Fonts

#### For Tech/SaaS Look:
```html
<!-- In templates/base.html -->
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```
```css
--font-display: 'Manrope', sans-serif;
--font-body: 'Inter', sans-serif;
```

#### For Premium/Financial Look:
```html
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```
```css
--font-display: 'Sora', sans-serif;
--font-body: 'Work Sans', sans-serif;
```

#### For Clean/Minimalist Look:
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```
```css
--font-display: 'Space Grotesk', sans-serif;
--font-body: 'Inter', sans-serif;
```

### Option 3: Self-Hosted Fonts (Best Privacy)

Download fonts and serve from your server:

1. **Download fonts from Google Fonts** or use tools like [google-webfonts-helper](https://gwfh.mranftl.com/)

2. **Create fonts directory:**
```bash
mkdir -p static/fonts
```

3. **Add font files:**
```
static/fonts/
├── inter-regular.woff2
├── inter-medium.woff2
├── inter-semibold.woff2
├── plus-jakarta-sans-regular.woff2
├── plus-jakarta-sans-semibold.woff2
└── plus-jakarta-sans-bold.woff2
```

4. **Update CSS:**
```css
/* In static/css/main.css - Add at top */
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('../fonts/inter-regular.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('../fonts/inter-semibold.woff2') format('woff2');
}

@font-face {
    font-family: 'Plus Jakarta Sans';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('../fonts/plus-jakarta-sans-semibold.woff2') format('woff2');
}

@font-face {
    font-family: 'Plus Jakarta Sans';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('../fonts/plus-jakarta-sans-bold.woff2') format('woff2');
}
```

5. **Remove Google Fonts link from `templates/base.html`**

**Pros:** Full control, better privacy (GDPR), no external dependencies  
**Cons:** More setup work, you manage updates

## 🎨 Popular SaaS Font Combinations

### Enterprise/Corporate
- **Display:** IBM Plex Sans
- **Body:** IBM Plex Sans
- Used by: IBM, Red Hat

### Modern Tech
- **Display:** Inter
- **Body:** Inter
- Used by: GitHub, Vercel, Figma

### Creative/Friendly
- **Display:** Cabinet Grotesk
- **Body:** Inter
- Used by: Webflow, Framer

### Premium/Luxury
- **Display:** GT America / Graphik
- **Body:** Graphik
- Used by: Stripe (before custom font)

## 📊 Current Implementation

**File:** `templates/base.html`
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

**File:** `static/css/main.css`
```css
:root {
    --font-display: 'Plus Jakarta Sans', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

## 🚀 How to Change Fonts

### Quick Change (Google Fonts):
1. Visit [Google Fonts](https://fonts.google.com/)
2. Select your fonts
3. Copy the `<link>` tag
4. Replace in `templates/base.html` (line 13)
5. Update CSS variables in `static/css/main.css` (lines 49-50)
6. Refresh browser (Django will auto-reload)

### Test in Browser DevTools:
1. Open browser DevTools (F12)
2. Go to Elements tab
3. Edit `:root` CSS variables
4. See changes live
5. Copy what you like to `main.css`

## 💡 Font Loading Best Practices

Current implementation includes:
- ✅ `preconnect` for faster font loading
- ✅ `font-display: swap` to prevent invisible text
- ✅ System font fallbacks
- ✅ Limited font weights (400, 500, 600, 700) for performance

## 🔍 Testing Your Fonts

After changing fonts, test:
- [ ] All headings (h1, h2, h3)
- [ ] Buttons and CTAs
- [ ] Form inputs
- [ ] Modal text
- [ ] Mobile responsiveness
- [ ] Load time (should be < 100ms for fonts)

---

**Your current fonts are production-ready!** Inter + Plus Jakarta Sans is an excellent modern combination used by many successful SaaS companies.

Want to try a different style? Just let me know which option you prefer!
