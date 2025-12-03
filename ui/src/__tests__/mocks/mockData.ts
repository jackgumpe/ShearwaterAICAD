import { faker } from '@faker-js/faker'

export interface MockMessage {
  id: string
  type: 'user' | 'system' | 'dm' | 'raid' | 'party' | 'guild'
  timestamp: string
  user_id?: string
  username?: string
  user_avatar?: string
  user_badge?: string
  content: string
  metadata?: Record<string, any>
}

export interface MockUser {
  id: string
  username: string
  email: string
  avatar_url: string
  badge: 'admin' | 'moderator' | 'vip' | 'standard'
  level: number
  experience: number
}

export interface MockRaid {
  id: string
  name: string
  boss_name: string
  difficulty: 'normal' | 'hard' | 'mythic'
  status: 'preparing' | 'in_progress' | 'wipe' | 'victory'
  health_percentage: number
  participants: Array<{
    user_id: string
    username: string
    role: 'tank' | 'dps' | 'healer'
    class: string
  }>
}

export class MockDataFactory {
  static createUser(overrides?: Partial<MockUser>): MockUser {
    return {
      id: faker.string.uuid(),
      username: faker.internet.userName(),
      email: faker.internet.email(),
      avatar_url: faker.image.avatarGitHub(),
      badge: faker.helpers.arrayElement(['admin', 'moderator', 'vip', 'standard']),
      level: faker.number.int({ min: 1, max: 120 }),
      experience: faker.number.int({ min: 0, max: 1000000 }),
      ...overrides,
    }
  }

  static createUserMessage(overrides?: Partial<MockMessage>): MockMessage {
    const user = this.createUser()
    return {
      id: faker.string.uuid(),
      type: 'user',
      timestamp: faker.date.recent().toISOString(),
      user_id: user.id,
      username: user.username,
      user_avatar: user.avatar_url,
      user_badge: user.badge,
      content: faker.lorem.sentence(),
      metadata: {
        server: 'main',
        channel: 'general',
        level: user.level,
      },
      ...overrides,
    }
  }

  static createSystemMessage(overrides?: Partial<MockMessage>): MockMessage {
    return {
      id: faker.string.uuid(),
      type: 'system',
      timestamp: faker.date.recent().toISOString(),
      content: 'System event',
      metadata: {
        event: faker.helpers.arrayElement([
          'user_joined',
          'user_left',
          'user_leveled_up',
          'raid_started',
          'server_maintenance',
        ]),
      },
      ...overrides,
    }
  }

  static createRaidMessage(overrides?: Partial<MockMessage>): MockMessage {
    return {
      id: faker.string.uuid(),
      type: 'raid',
      timestamp: faker.date.recent().toISOString(),
      content: '',
      metadata: {
        raid_id: faker.string.uuid(),
        raid_name: faker.lorem.word(),
        boss_name: faker.lorem.word(),
        difficulty: faker.helpers.arrayElement(['normal', 'hard', 'mythic']),
        status: faker.helpers.arrayElement(['preparing', 'in_progress', 'wipe', 'victory']),
        health_percentage: faker.number.int({ min: 0, max: 100 }),
      },
      ...overrides,
    }
  }

  static createPartyMessage(overrides?: Partial<MockMessage>): MockMessage {
    return {
      id: faker.string.uuid(),
      type: 'party',
      timestamp: faker.date.recent().toISOString(),
      content: '',
      metadata: {
        party_id: faker.string.uuid(),
        event: faker.helpers.arrayElement(['member_joined', 'member_left', 'disbanded']),
        member_count: faker.number.int({ min: 1, max: 5 }),
      },
      ...overrides,
    }
  }

  static createGuildMessage(overrides?: Partial<MockMessage>): MockMessage {
    return {
      id: faker.string.uuid(),
      type: 'guild',
      timestamp: faker.date.recent().toISOString(),
      content: '',
      metadata: {
        guild_id: faker.string.uuid(),
        guild_name: faker.company.name(),
        guild_level: faker.number.int({ min: 1, max: 50 }),
        event: faker.helpers.arrayElement([
          'member_joined',
          'conquest_complete',
          'war_declared',
        ]),
      },
      ...overrides,
    }
  }

  static createDirectMessage(overrides?: Partial<MockMessage>): MockMessage {
    const fromUser = this.createUser()
    const toUser = this.createUser()
    return {
      id: faker.string.uuid(),
      type: 'dm',
      timestamp: faker.date.recent().toISOString(),
      content: faker.lorem.sentence(),
      metadata: {
        from_user_id: fromUser.id,
        from_username: fromUser.username,
        to_user_id: toUser.id,
        read: faker.datatype.boolean(),
      },
      ...overrides,
    }
  }

  static createRaid(overrides?: Partial<MockRaid>): MockRaid {
    const participantCount = faker.number.int({ min: 5, max: 20 })
    return {
      id: faker.string.uuid(),
      name: faker.lorem.word(),
      boss_name: faker.lorem.word(),
      difficulty: faker.helpers.arrayElement(['normal', 'hard', 'mythic']),
      status: faker.helpers.arrayElement(['preparing', 'in_progress', 'wipe', 'victory']),
      health_percentage: faker.number.int({ min: 0, max: 100 }),
      participants: Array.from({ length: participantCount }, () => {
        const user = this.createUser()
        return {
          user_id: user.id,
          username: user.username,
          role: faker.helpers.arrayElement(['tank', 'dps', 'healer']),
          class: faker.helpers.arrayElement(['warrior', 'mage', 'rogue', 'paladin']),
        }
      }),
      ...overrides,
    }
  }

  static createMessages(count: number, type?: MockMessage['type']): MockMessage[] {
    return Array.from({ length: count }, () => {
      const messageType = type || faker.helpers.arrayElement(['user', 'system', 'raid', 'party', 'guild', 'dm'])

      switch (messageType) {
        case 'user':
          return this.createUserMessage()
        case 'system':
          return this.createSystemMessage()
        case 'raid':
          return this.createRaidMessage()
        case 'party':
          return this.createPartyMessage()
        case 'guild':
          return this.createGuildMessage()
        case 'dm':
          return this.createDirectMessage()
        default:
          return this.createUserMessage()
      }
    })
  }
}

// Helper to mock WebSocket messages
export function createWebSocketEvent(message: MockMessage): MessageEvent {
  return new MessageEvent('message', {
    data: JSON.stringify(message),
  })
}

// Helper to create multiple WebSocket messages
export function createWebSocketEvents(messages: MockMessage[]): MessageEvent[] {
  return messages.map(createWebSocketEvent)
}
