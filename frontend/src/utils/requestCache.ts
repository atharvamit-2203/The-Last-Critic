// Simple request deduplication and caching system
class RequestCache {
  private cache = new Map<string, any>()
  private pendingRequests = new Map<string, Promise<any>>()

  async get<T>(key: string, fetcher: () => Promise<T>, ttl: number = 300000): Promise<T> {
    // Check cache first
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < ttl) {
      console.log(`✓ Cache hit: ${key}`)
      return cached.data
    }

    // Check if request is already pending
    const pending = this.pendingRequests.get(key)
    if (pending) {
      console.log(`⏳ Request pending: ${key}`)
      return pending
    }

    // Make new request
    console.log(`🔄 New request: ${key}`)
    const promise = fetcher()
    this.pendingRequests.set(key, promise)

    try {
      const data = await promise
      this.cache.set(key, { data, timestamp: Date.now() })
      return data
    } finally {
      this.pendingRequests.delete(key)
    }
  }

  clear(pattern?: string) {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key)
        }
      }
    } else {
      this.cache.clear()
    }
  }
}

export const requestCache = new RequestCache()