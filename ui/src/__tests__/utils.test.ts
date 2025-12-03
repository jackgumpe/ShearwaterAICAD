import { describe, it, expect } from 'vitest'

// Format relative time (e.g., "2 minutes ago")
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`

  return date.toLocaleDateString()
}

// Format absolute timestamp
export function formatAbsoluteTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// Validate message content
export function validateMessage(content: string): { valid: boolean; error?: string } {
  if (!content) return { valid: false, error: 'Message cannot be empty' }
  if (content.length > 5000) return { valid: false, error: 'Message too long (max 5000 characters)' }
  return { valid: true }
}

// Parse message type
export function getMessageTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    user: 'User Message',
    system: 'System Event',
    dm: 'Direct Message',
    raid: 'Raid Event',
    party: 'Party Event',
    guild: 'Guild Event',
  }
  return labels[type] || 'Unknown'
}

describe('Utility Functions', () => {
  describe('formatRelativeTime', () => {
    it('should format time just now', () => {
      const now = new Date().toISOString()
      const result = formatRelativeTime(now)
      expect(result).toBe('just now')
    })

    it('should format time in minutes', () => {
      const date = new Date(Date.now() - 5 * 60 * 1000).toISOString()
      const result = formatRelativeTime(date)
      expect(result).toMatch(/\d+ minutes ago/)
    })

    it('should format time in hours', () => {
      const date = new Date(Date.now() - 2 * 3600 * 1000).toISOString()
      const result = formatRelativeTime(date)
      expect(result).toMatch(/\d+ hours ago/)
    })

    it('should format time in days', () => {
      const date = new Date(Date.now() - 3 * 86400 * 1000).toISOString()
      const result = formatRelativeTime(date)
      expect(result).toMatch(/\d+ days ago/)
    })
  })

  describe('formatAbsoluteTime', () => {
    it('should format date and time', () => {
      const date = new Date('2025-12-03T12:30:45Z').toISOString()
      const result = formatAbsoluteTime(date)
      expect(result).toMatch(/Dec.*3.*2025/)
    })

    it('should include time component', () => {
      const date = new Date('2025-12-03T14:30:45Z').toISOString()
      const result = formatAbsoluteTime(date)
      expect(result).toMatch(/\d{2}:\d{2}:\d{2}/)
    })
  })

  describe('validateMessage', () => {
    it('should accept valid message', () => {
      const result = validateMessage('Hello world')
      expect(result.valid).toBe(true)
      expect(result.error).toBeUndefined()
    })

    it('should reject empty message', () => {
      const result = validateMessage('')
      expect(result.valid).toBe(false)
      expect(result.error).toBe('Message cannot be empty')
    })

    it('should reject message longer than 5000 chars', () => {
      const longMessage = 'a'.repeat(5001)
      const result = validateMessage(longMessage)
      expect(result.valid).toBe(false)
      expect(result.error).toMatch(/too long/)
    })

    it('should accept message at 5000 char limit', () => {
      const maxMessage = 'a'.repeat(5000)
      const result = validateMessage(maxMessage)
      expect(result.valid).toBe(true)
    })
  })

  describe('getMessageTypeLabel', () => {
    it('should return correct label for user message', () => {
      expect(getMessageTypeLabel('user')).toBe('User Message')
    })

    it('should return correct label for system message', () => {
      expect(getMessageTypeLabel('system')).toBe('System Event')
    })

    it('should return correct label for raid message', () => {
      expect(getMessageTypeLabel('raid')).toBe('Raid Event')
    })

    it('should return unknown for invalid type', () => {
      expect(getMessageTypeLabel('invalid')).toBe('Unknown')
    })
  })
})
