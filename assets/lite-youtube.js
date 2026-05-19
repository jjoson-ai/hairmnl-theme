/**
 * lite-youtube-embed custom element
 *
 * Replaces eager YouTube iframes with a lightweight thumbnail + play button.
 * The real iframe (and ~2.2 MB of YouTube JS) only loads on user click.
 *
 * Based on paulirish/lite-youtube (MIT License)
 * https://github.com/paulirish/lite-youtube-embed
 *
 * Attributes:
 *   videoid  — YouTube video ID (required)
 *   params   — Extra query params for the iframe URL, e.g. "rel=0&modestbranding=1"
 */

class LiteYT extends HTMLElement {
  /** @type {boolean} Whether the real iframe has been activated. */
  #activated = false;

  static get observedAttributes() {
    return ['videoid', 'params'];
  }

  /** @returns {string} YouTube video ID. */
  get videoid() {
    return this.getAttribute('videoid') || '';
  }

  /** @returns {string} Extra iframe URL params. */
  get params() {
    return this.getAttribute('params') || '';
  }

  connectedCallback() {
    this.#render();
  }

  // ---- Private helpers ------------------------------------------------

  /** Build the shadow (light DOM) markup and inject styles once. */
  #render() {
    // Already rendered? Skip.
    if (this.querySelector('.lyt-wrapper')) return;

    const vid = this.videoid;
    if (!vid) return;

    const posterUrl = `https://i.ytimg.com/vi/${vid}/hqdefault.jpg`;

    // Build the wrapper
    const wrapper = document.createElement('div');
    wrapper.classList.add('lyt-wrapper');
    wrapper.setAttribute('role', 'button');
    wrapper.setAttribute('aria-label', 'Play YouTube video');
    wrapper.setAttribute('tabindex', '0');

    // Poster background
    wrapper.style.backgroundImage = `url('${posterUrl}')`;

    // Play button
    const playBtn = document.createElement('div');
    playBtn.classList.add('lyt-playbtn');
    playBtn.innerHTML = this.#playBtnSVG();

    wrapper.appendChild(playBtn);

    // Click / key handler
    wrapper.addEventListener('click', () => this.#activate());
    wrapper.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.#activate();
      }
    });

    this.appendChild(wrapper);

    // Inject styles once per document
    if (!document.getElementById('lyt-styles')) {
      const style = document.createElement('style');
      style.id = 'lyt-styles';
      style.textContent = this.#css;
      document.head.appendChild(style);
    }
  }

  /** Swap in the real YouTube iframe. */
  #activate() {
    if (this.#activated) return;
    this.#activated = true;

    const vid = this.videoid;
    const params = this.params ? `&${this.params}` : '';
    const src = `https://www.youtube.com/embed/${vid}?autoplay=1${params}`;

    const iframe = document.createElement('iframe');
    iframe.setAttribute('width', '100%');
    iframe.setAttribute('height', '100%');
    iframe.setAttribute('src', src);
    iframe.setAttribute('allow', 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture');
    iframe.setAttribute('allowfullscreen', '');
    iframe.setAttribute('title', 'YouTube video');

    // Replace the wrapper with the iframe
    const wrapper = this.querySelector('.lyt-wrapper');
    if (wrapper) {
      wrapper.replaceWith(iframe);
    } else {
      this.appendChild(iframe);
    }
  }

  /** @returns {string} Play button SVG markup. */
  #playBtnSVG() {
    return '<svg viewBox="0 0 68 48" width="68" height="48"><path d="M66.52 7.74c-.78-2.93-2.49-5.41-5.42-6.19C55.79.13 34 0 34 0S12.21.13 6.9 1.55c-2.93.78-4.63 3.26-5.42 6.19C.07 13.05 0 24 0 24s.07 10.95 1.48 16.26c.78 2.93 2.49 5.41 5.42 6.19C12.21 47.87 34 48 34 48s21.79-.13 27.1-1.55c2.93-.78 4.64-3.26 5.42-6.19C67.93 34.95 68 24 68 24s-.07-10.95-1.48-16.26z" fill="red"/><path d="M45 24 27 14v20" fill="#fff"/></svg>';
  }

  /** @returns {string} Scoped CSS for the component. */
  get #css() {
    return `
lite-youtube {
  display: block;
  contain: content;
  position: relative;
  width: 100%;
  height: 100%;
}

.lyt-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lyt-playbtn {
  width: 68px;
  height: 48px;
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.lyt-wrapper:hover .lyt-playbtn,
.lyt-wrapper:focus .lyt-playbtn {
  opacity: 1;
}

lite-youtube iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
`;
  }
}

// Register the custom element
customElements.define('lite-youtube', LiteYT);