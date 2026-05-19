# YouTube embed CSS leak — root cause + fix paths

> **TL;DR:** The 921 KB of YouTube player CSS loading on `/collections/davines` is from a YouTube iframe **above-the-fold** in the brand-page hero section. `loading="lazy"` is already set but has no effect — the iframe is in initial viewport. Fix requires a **YouTube Facade pattern** (thumbnail + click-to-load) to defer the iframe load until user interaction.

Date: 2026-05-19
bd: hairmnl-theme-ujg6.41

## Investigation

### What loads
- `youtube.com/s/player/e1bd44b2/www-player.css` — 506 KB
- `youtube.com/s/_/ytembeds/_/ss/k=ytembeds.base.../base.css` — 435 KB
- Total: ~941 KB of CSS for one YouTube embed

### The iframe
Single iframe on the Davines brand page:
```html
<iframe src="https://www.youtube.com/embed/OnrXzZcDxoE?rel=0&hd=1&enablejsapi=1&origin=..."
        frameborder="0"
        loading="lazy"
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
        data-gtm-yt-...>
```

### Why `loading="lazy"` doesn't help
The iframe lives inside the brand-page **hero section** (`custom-content` section type, brick-block-video layout). DOM ancestry confirmed via Playwright:

```
<iframe>
  ↳ <div.video-wrapper>
    ↳ <div.hero__content>
      ↳ <div.hero__content__wrapper>
        ↳ <div.brick__block__video>
          ↳ <div.brick__block>
            ↳ <section.brick__section>
              ↳ <div.wrapper>
                ↳ <div id="shopify-section-template--18751980109923__1c95b66b">  // custom-content section
                  ↳ <main id="MainContent">
```

At a 390×844 viewport (mobile emulation), `iframe.offsetTop = 0` AND `isInViewport = true, distanceFromViewport = 0` — the iframe is in initial viewport from page load. `loading="lazy"` only defers iframes that are >loading-distance below viewport (~3000px for Chromium). Anything above-the-fold loads immediately regardless of the attribute.

### Why this matters
Real users landing on `/collections/davines` (mobile) see ~941 KB of YouTube CSS download before the page settles. That's:
- ~30% of the brand-page CSS budget (941 KB out of 2896 KB total)
- A direct hit to FCP and LCP timing on mobile cold loads
- Plus ~480 KB of additional YouTube *script* payload (`base.js`, `ytembeds.base.en_US...js`)

The browser pre-downloads the YouTube player infrastructure as soon as the iframe element exists in DOM, **before** any user interaction. The video may auto-play but that's a separate concern.

## Fix paths

### Path A — YouTube Facade (RECOMMENDED, ~3 hrs)

Replace the iframe in the rendered HTML with a static thumbnail + play button. On click, swap to the real iframe (or `<iframe-loaded>` element). Industry-standard pattern; saves ~1.4 MB of CSS+JS on initial load.

Implementation outline:
1. Add `snippets/youtube-facade.liquid` that takes a video ID + returns thumbnail markup:
   ```liquid
   <button class="yt-facade" data-yt-id="{{ video_id }}" aria-label="Play video">
     <img src="https://img.youtube.com/vi/{{ video_id }}/maxresdefault.jpg" loading="lazy">
     <svg class="yt-facade-play" ...><path d="M.66... play icon"/></svg>
   </button>
   ```
2. Add JS in `assets/hairmnl-common.js` (~30 LoC):
   ```javascript
   document.addEventListener('click', function(e) {
     const btn = e.target.closest('.yt-facade');
     if (!btn) return;
     e.preventDefault();
     const id = btn.dataset.ytId;
     const iframe = Object.assign(document.createElement('iframe'), {
       src: `https://www.youtube.com/embed/${id}?autoplay=1&rel=0`,
       frameborder: 0,
       allow: 'autoplay; encrypted-media',
       allowFullscreen: true,
     });
     btn.replaceWith(iframe);
   });
   ```
3. Modify `sections/custom-content.liquid` (or wherever the iframe is currently rendered): replace direct iframe render with `{% render 'youtube-facade', video_id: extracted_id %}`. Extract the YouTube ID from the embed URL via regex/split.

Effort: ~3 hrs. Visual change (thumbnail instead of iframe placeholder), needs operator sign-off on the styling. Net savings: ~1.4 MB / cold-load.

### Path B — lite-youtube-embed web component (~1 hr)

Use [lite-youtube-embed](https://github.com/paulirish/lite-youtube-embed) (paulirish, ~1 KB JS). Drop-in replacement that does the facade pattern automatically. Markup becomes:
```html
<lite-youtube videoid="OnrXzZcDxoE"></lite-youtube>
```
Plus include the component's tiny CSS + JS files.

Less control over thumbnail styling than Path A but faster to ship. Same savings (~1.4 MB).

### Path C — operator content edit (~10 min, no code)

Operator opens theme editor → Customize → brand page → Hero section → Block content. Replace the raw `<iframe>` HTML with a thumbnail image + a "Watch video" link to the YouTube URL. The link opens in a new tab when clicked. No JS, no embed, just an outbound link.

Loses the embedded-player UX but eliminates 1.4 MB cost immediately. Operator decision.

### Path D — accept the cost (no fix)

Document that the brand-hero video is intentional and the 921 KB cost is acceptable. Move on. The video adds brand value; mobile users with cheap data plans pay 1 MB extra.

## Recommendation

**Path B (lite-youtube-embed)** for speed-of-shipping; Path A (custom facade) if the operator wants pixel-perfect control over the thumbnail styling. Either delivers the same ~1.4 MB savings.

The change is **not zero-risk** because it changes visible page content (the user sees a thumbnail until they click). Operator must approve the UX change before shipping.

## Verification post-fix

```bash
cd /Users/y9378348c/Projects/hairmnl-theme/scripts/smoke-tests
NODE_OPTIONS="--tls-max-v1.2" node -e "
  // Coverage script — same as in critical-css-coverage-2026-05-19.md
  // After fix: YouTube CSS bytes loaded should drop to 0 on cold-load.
  // Only loads after user clicks the facade.
"
```

Expected post-fix Coverage report:
- Total CSS: ~1950 KB (down from 2896 KB, -946 KB)
- Used %: ~9-10% (up from 6.1%)
- YouTube CSS: 0 KB (loaded only on user interaction)

The single biggest CSS reduction available on the brand page, gating on an operator sign-off for the UX change.
