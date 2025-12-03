# Testing Framework & Infrastructure

## Testing Strategy

Comprehensive testing across three layers:
- **Unit Tests** (React components, utilities, hooks)
- **Integration Tests** (WebSocket flow, state management)
- **E2E Tests** (Full user workflows)

Target: **100+ tests** with **95%+ code coverage**

---

## Unit Testing with Vitest

### Setup

```bash
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom
```

### Test Structure
```
ui/src/
├── components/
│   ├── MessageList.tsx
│   └── __tests__/
│       └── MessageList.test.tsx
├── hooks/
│   ├── useWebSocket.ts
│   └── __tests__/
│       └── useWebSocket.test.ts
└── __tests__/
    └── App.test.tsx
```

### Vitest Config

```typescript
// ui/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { getViteConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/__tests__/',
        '**/*.test.ts',
        '**/*.test.tsx'
      ]
    }
  }
})
```

### Test Setup File

```typescript
// src/__tests__/setup.ts
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock WebSocket
global.WebSocket = vi.fn()

// Mock console methods
global.console = {
  ...console,
  error: vi.fn(),
  warn: vi.fn(),
  debug: vi.fn()
}
```

### Example: useWebSocket Hook Test

```typescript
// src/hooks/__tests__/useWebSocket.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useWebSocket } from '../useWebSocket'

describe('useWebSocket', () => {
  let mockWebSocket

  beforeEach(() => {
    mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }

    global.WebSocket = vi.fn(() => mockWebSocket)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should establish connection', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    expect(global.WebSocket).toHaveBeenCalledWith(
      'ws://localhost:8000/ws/live-log'
    )
  })

  it('should handle incoming messages', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    const testMessage = { type: 'user', content: 'Hello' }

    act(() => {
      const onMessageHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'message')[1]

      onMessageHandler({
        data: JSON.stringify(testMessage)
      })
    })

    await waitFor(() => {
      expect(result.current.messages).toContain(testMessage)
    })
  })

  it('should reconnect with exponential backoff', async () => {
    vi.useFakeTimers()

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    // Simulate connection failure
    const onErrorHandler = mockWebSocket.addEventListener.mock.calls
      .find(call => call[0] === 'error')[1]

    onErrorHandler()

    // First retry at 1 second
    vi.advanceTimersByTime(1000)
    expect(global.WebSocket).toHaveBeenCalledTimes(2)

    // Second retry at 3 seconds
    vi.advanceTimersByTime(2000)
    expect(global.WebSocket).toHaveBeenCalledTimes(3)

    // Third retry at 7 seconds
    vi.advanceTimersByTime(4000)
    expect(global.WebSocket).toHaveBeenCalledTimes(4)

    vi.useRealTimers()
  })

  it('should buffer messages when disconnected', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    // Simulate disconnection
    const onCloseHandler = mockWebSocket.addEventListener.mock.calls
      .find(call => call[0] === 'close')[1]

    onCloseHandler()

    // Try to send while disconnected
    act(() => {
      result.current.send({ type: 'user', content: 'Test' })
    })

    // Message should be buffered
    expect(result.current.messageBuffer.length).toBe(1)

    // Reconnect
    act(() => {
      const onOpenHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'open')[1]

      onOpenHandler()
    })

    // Buffered messages should be sent
    expect(mockWebSocket.send).toHaveBeenCalled()
  })

  it('should handle heartbeat', async () => {
    vi.useFakeTimers()

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log', { heartbeat: true })
    )

    // Advance 30 seconds (heartbeat interval)
    vi.advanceTimersByTime(30000)

    expect(mockWebSocket.send).toHaveBeenCalledWith(
      JSON.stringify({ action: 'ping' })
    )

    vi.useRealTimers()
  })

  it('should cleanup on unmount', () => {
    const { unmount } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    unmount()

    expect(mockWebSocket.close).toHaveBeenCalled()
    expect(mockWebSocket.removeEventListener).toHaveBeenCalled()
  })
})
```

### Example: MessageList Component Test

```typescript
// src/components/__tests__/MessageList.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MessageList from '../MessageList'

describe('MessageList', () => {
  const mockMessages = [
    {
      id: '1',
      type: 'user',
      username: 'TestUser',
      content: 'Hello',
      timestamp: '2025-12-03T12:00:00Z'
    },
    {
      id: '2',
      type: 'user',
      username: 'TestUser2',
      content: 'Hi there',
      timestamp: '2025-12-03T12:01:00Z'
    }
  ]

  it('should render messages', () => {
    render(<MessageList messages={mockMessages} />)

    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Hi there')).toBeInTheDocument()
  })

  it('should display username and avatar', () => {
    render(<MessageList messages={mockMessages} />)

    expect(screen.getByText('TestUser')).toBeInTheDocument()
    expect(screen.getByText('TestUser2')).toBeInTheDocument()
  })

  it('should format timestamps', () => {
    render(<MessageList messages={mockMessages} />)

    // Check for relative time format (e.g., "2 minutes ago")
    const timestamps = screen.getAllByText(/ago/)
    expect(timestamps.length).toBeGreaterThan(0)
  })

  it('should handle empty message list', () => {
    render(<MessageList messages={[]} />)

    expect(screen.getByText(/No messages/i)).toBeInTheDocument()
  })

  it('should virtualize long lists', () => {
    const manyMessages = Array.from({ length: 1000 }, (_, i) => ({
      id: `${i}`,
      type: 'user',
      username: `User${i}`,
      content: `Message ${i}`,
      timestamp: new Date(Date.now() - i * 1000).toISOString()
    }))

    const { container } = render(<MessageList messages={manyMessages} />)

    // Only first ~50 messages should be rendered (virtual scrolling)
    const messageElements = container.querySelectorAll('[data-message-id]')
    expect(messageElements.length).toBeLessThan(100)
  })

  it('should handle message updates', () => {
    const { rerender } = render(<MessageList messages={mockMessages} />)

    const updatedMessages = [
      ...mockMessages,
      {
        id: '3',
        type: 'user',
        username: 'TestUser3',
        content: 'New message',
        timestamp: '2025-12-03T12:02:00Z'
      }
    ]

    rerender(<MessageList messages={updatedMessages} />)

    expect(screen.getByText('New message')).toBeInTheDocument()
  })
})
```

---

## Integration Testing

### WebSocket Integration Test

```typescript
// src/__tests__/integration/WebSocketIntegration.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useWebSocket } from '../../hooks/useWebSocket'

describe('WebSocket Integration', () => {
  it('should handle full message flow', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    // Wait for connection
    await waitFor(() => {
      expect(result.current.connected).toBe(true)
    })

    // Subscribe to messages
    act(() => {
      result.current.send({
        action: 'subscribe',
        message_types: ['user', 'raid']
      })
    })

    // Wait for subscription confirmation
    await waitFor(() => {
      expect(result.current.subscribed).toContain('user')
    })

    // Verify buffer is empty
    expect(result.current.messageBuffer).toHaveLength(0)
  })

  it('should handle reconnection and message recovery', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/live-log')
    )

    await waitFor(() => {
      expect(result.current.connected).toBe(true)
    })

    // Store initial connection count
    const initialConnections = result.current.connectionAttempts

    // Simulate connection loss
    act(() => {
      result.current.simulateDisconnect()
    })

    expect(result.current.connected).toBe(false)

    // Should reconnect automatically
    await waitFor(() => {
      expect(result.current.connected).toBe(true)
      expect(result.current.connectionAttempts).toBeGreaterThan(initialConnections)
    }, { timeout: 5000 })
  })
})
```

---

## E2E Testing with Playwright

### Installation

```bash
npm install -D @playwright/test
npx playwright install
```

### Playwright Config

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './src/__tests__/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5176',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    }
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5176',
    reuseExistingServer: !process.env.CI
  }
})
```

### E2E Test Example

```typescript
// src/__tests__/e2e/live-log.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Live Log', () => {
  test('should display messages from server', async ({ page }) => {
    await page.goto('/')

    // Wait for connection status
    const connectionStatus = page.locator('[data-testid="connection-status"]')
    await expect(connectionStatus).toContainText('connected', { timeout: 5000 })

    // Wait for first message
    const firstMessage = page.locator('[data-testid="message-item"]').first()
    await expect(firstMessage).toBeVisible({ timeout: 10000 })

    // Verify message content
    await expect(firstMessage).toContainText(/.*/)
  })

  test('should search messages', async ({ page }) => {
    await page.goto('/')

    // Wait for connection
    await page.locator('[data-testid="connection-status"]').waitFor()

    // Type search query
    await page.fill('[data-testid="search-input"]', 'dragon')

    // Wait for results
    const results = page.locator('[data-testid="message-item"]')
    const count = await results.count()

    expect(count).toBeGreaterThan(0)

    // Verify all results contain search term
    for (let i = 0; i < count; i++) {
      const text = await results.nth(i).textContent()
      expect(text.toLowerCase()).toContain('dragon')
    }
  })

  test('should filter by message type', async ({ page }) => {
    await page.goto('/')

    // Click raid filter
    await page.click('[data-testid="filter-raid"]')

    // All visible messages should be raid type
    const messages = page.locator('[data-testid="message-item"]')
    const count = await messages.count()

    for (let i = 0; i < count; i++) {
      const type = await messages.nth(i).getAttribute('data-type')
      expect(type).toBe('raid')
    }
  })

  test('should auto-scroll on new message', async ({ page }) => {
    await page.goto('/')

    // Get initial scroll position
    const messageList = page.locator('[data-testid="message-list"]')
    const initialScroll = await messageList.evaluate(el => el.scrollTop)

    // Wait for new message
    await page.waitForTimeout(2000)

    // Scroll position should be at bottom
    const newScroll = await messageList.evaluate(el => el.scrollTop)
    expect(newScroll).toBeGreaterThan(initialScroll)
  })

  test('should handle message latency <100ms', async ({ page }) => {
    await page.goto('/')

    const startTime = Date.now()
    const messageList = page.locator('[data-testid="message-item"]')

    await page.waitForTimeout(1000)

    const messageCount = await messageList.count()
    const endTime = Date.now()

    if (messageCount > 0) {
      const latency = (endTime - startTime) / messageCount
      expect(latency).toBeLessThan(100)
    }
  })
})
```

---

## Running Tests

### Commands

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run unit tests with coverage
npm run test:unit:coverage

# Run E2E tests
npm run test:e2e

# Watch mode for development
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run",
    "test:unit:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:debug": "playwright test --debug",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest run --coverage && open coverage/index.html"
  }
}
```

---

## Coverage Requirements

- **Overall**: 95%+
- **Statements**: 95%+
- **Branches**: 90%+
- **Functions**: 95%+
- **Lines**: 95%+

### Coverage Report

HTML reports generated in `coverage/` directory. Track coverage over time to prevent regression.

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - run: npm ci
      - run: npm run test:unit:coverage
      - run: npm run test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## Test Checklist

- [ ] All components have unit tests
- [ ] All hooks have unit tests
- [ ] All utilities have unit tests
- [ ] WebSocket integration tests pass
- [ ] E2E user workflows tested
- [ ] Coverage at 95%+
- [ ] No console errors in tests
- [ ] Tests run in < 60 seconds
- [ ] CI/CD pipeline passes
- [ ] Manual QA sign-off
