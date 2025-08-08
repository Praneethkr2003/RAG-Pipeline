import { streamText } from "ai"

// Allow streaming responses up to 30 seconds
export const maxDuration = 30

// Get the API base URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()
    
    // Forward the request to our FastAPI backend
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        stream: true
      })
    })

    if (!response.ok) {
      const error = await response.text()
      console.error('Backend API error:', error)
      return new Response(JSON.stringify({ error: 'Error communicating with the API' }), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' }
      })
    }

    // Forward the streaming response from our backend
    const { readable, writable } = new TransformStream()
    response.body?.pipeTo(writable)
    
    return new Response(readable, {
      headers: { 'Content-Type': 'text/plain' }
    })
    
  } catch (error) {
    console.error('Error in chat route:', error)
    return new Response(
      JSON.stringify({ 
        error: 'An error occurred while processing your request',
        details: error instanceof Error ? error.message : 'Unknown error'
      }), 
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    )
  }
}
