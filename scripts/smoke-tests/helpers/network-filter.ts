/**
 * Network request collection helper.
 *
 * Attaches a listener to the page that records every network request
 * matching an optional filter. Used by most smoke tests to assert on
 * what loaded, what didn't, and timing.
 */

import { Page, Request, Response } from '@playwright/test';

export type RecordedRequest = {
  url: string;
  method: string;
  resourceType: string;
  status: number | null;
  fromCache: boolean;
  startTime: number;
  endTime: number | null;
  size: number | null;
};

export class NetworkRecorder {
  private requests: RecordedRequest[] = [];
  private requestStartTimes = new Map<Request, number>();
  private origin: number;

  constructor(private page: Page) {
    this.origin = Date.now();
    page.on('request', (req) => {
      this.requestStartTimes.set(req, Date.now() - this.origin);
    });
    page.on('response', async (res) => {
      const req = res.request();
      const startTime = this.requestStartTimes.get(req) ?? 0;
      const endTime = Date.now() - this.origin;
      let size: number | null = null;
      try {
        const buf = await res.body();
        size = buf.length;
      } catch {
        // Response bodies for cached or aborted requests may not be available
      }
      this.requests.push({
        url: req.url(),
        method: req.method(),
        resourceType: req.resourceType(),
        status: res.status(),
        fromCache: res.fromServiceWorker(),
        startTime,
        endTime,
        size,
      });
    });
    page.on('requestfailed', (req) => {
      const startTime = this.requestStartTimes.get(req) ?? 0;
      this.requests.push({
        url: req.url(),
        method: req.method(),
        resourceType: req.resourceType(),
        status: null,
        fromCache: false,
        startTime,
        endTime: null,
        size: null,
      });
    });
  }

  /** All recorded requests, optionally filtered by url-contains substring. */
  all(urlSubstring?: string): RecordedRequest[] {
    if (!urlSubstring) return [...this.requests];
    return this.requests.filter((r) => r.url.includes(urlSubstring));
  }

  /** Count requests matching a url-contains substring. */
  count(urlSubstring: string): number {
    return this.all(urlSubstring).length;
  }

  /** Has any request matching this substring loaded. */
  hasLoaded(urlSubstring: string): boolean {
    return this.requests.some(
      (r) => r.url.includes(urlSubstring) && r.status !== null && r.status < 400
    );
  }

  /** Reset to start fresh. */
  clear(): void {
    this.requests = [];
    this.requestStartTimes.clear();
    this.origin = Date.now();
  }

  /** Bytes received for matching requests. */
  totalBytes(urlSubstring: string): number {
    return this.all(urlSubstring).reduce((sum, r) => sum + (r.size ?? 0), 0);
  }

  /** Pretty-print for debug output. */
  describe(urlSubstring: string): string {
    const matches = this.all(urlSubstring);
    if (!matches.length) return `(no requests matching '${urlSubstring}')`;
    return matches
      .map((r) =>
        `  ${String(r.status ?? 'fail').padStart(3)} ${r.method.padEnd(6)} ${(r.size ?? 0).toString().padStart(7)}B  ${r.url.split('?')[0].slice(-80)}`
      )
      .join('\n');
  }
}

export function recordNetwork(page: Page): NetworkRecorder {
  return new NetworkRecorder(page);
}
