import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  url: string
  readyState: number = 0
  addEventListener = vi.fn()
  removeEventListener = vi.fn()
  send = vi.fn()
  close = vi.fn()

  constructor(url: string) {
    this.url = url
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = 1
      const event = new Event('open')
      this.addEventListener.mock.calls
        .filter((call: any[]) => call[0] === 'open')
        .forEach((call: any[]) => call[1](event))
    }, 0)
  }
}

global.WebSocket = MockWebSocket as any

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
} as any

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any

// Suppress console errors in tests (unless explicitly needed)
global.console = {
  ...console,
  error: vi.fn(),
  warn: vi.fn(),
  debug: vi.fn(),
}
