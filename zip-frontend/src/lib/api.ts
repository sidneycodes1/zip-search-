const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RequestOptions {
  method?: string
  headers?: Record<string, string>
  body?: FormData | string
}

export const api = {
  async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    const headers = options.headers || {}

    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers,
        body: options.body,
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      throw error
    }
  },

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint)
  },

  post<T>(
    endpoint: string,
    body: FormData | Record<string, unknown>,
    customHeaders?: Record<string, string>
  ): Promise<T> {
    const headers: Record<string, string> = customHeaders || {}

    let requestBody: FormData | string
    if (body instanceof FormData) {
      requestBody = body
    } else {
      headers['Content-Type'] = 'application/json'
      requestBody = JSON.stringify(body)
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      headers,
      body: requestBody,
    })
  },
}
