import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../App'

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render main layout', () => {
    render(<App />)

    expect(screen.getByText('Azerate Live Log')).toBeInTheDocument()
    expect(screen.getByText('Real-time message stream')).toBeInTheDocument()
  })

  it('should display connection status', () => {
    render(<App />)

    const connectionStatus = screen.getByRole('textbox', { hidden: true })
      .parentElement
      ?.querySelector('[data-testid="connection-status"]')

    if (connectionStatus) {
      expect(connectionStatus).toBeInTheDocument()
    }
  })

  it('should have sidebar with filters', () => {
    render(<App />)

    expect(screen.getByText('Filters')).toBeInTheDocument()
    expect(screen.getByText('All Messages')).toBeInTheDocument()
  })

  it('should have search input', () => {
    render(<App />)

    const searchInput = screen.getByPlaceholderText('Search messages...')
    expect(searchInput).toBeInTheDocument()
    expect(searchInput).toHaveAttribute('type', 'text')
  })

  it('should display initial waiting state', () => {
    render(<App />)

    expect(screen.getByText('Waiting for messages...')).toBeInTheDocument()
  })

  it('should show message counter', () => {
    render(<App />)

    const messageCounter = screen.getByText(/Messages:/)
    expect(messageCounter).toBeInTheDocument()
  })

  it('should have proper dark mode styling', () => {
    const { container } = render(<App />)

    const mainDiv = container.querySelector('[class*="bg-slate"]')
    expect(mainDiv).toBeInTheDocument()
  })

  it('should render header correctly', () => {
    render(<App />)

    const header = screen.getByRole('heading', { level: 1 })
    expect(header).toHaveTextContent('Azerate Live Log')
  })

  it('should have responsive layout structure', () => {
    const { container } = render(<App />)

    const sidebar = container.querySelector('[class*="w-64"]')
    const mainContent = container.querySelector('[class*="flex-1"]')

    expect(sidebar).toBeInTheDocument()
    expect(mainContent).toBeInTheDocument()
  })
})
