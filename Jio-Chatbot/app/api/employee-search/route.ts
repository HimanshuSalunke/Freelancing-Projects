import { NextRequest, NextResponse } from 'next/server'

// Simple configuration - like HTML version
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = await request.json()
    const { query } = body

    // Basic validation - like HTML version
    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { 
          success: false,
          error: 'Query is required',
          suggestions: [],
          count: 0
        },
        { status: 400 }
      )
    }

    // Simple fetch to backend - exactly like HTML version's searchEmployees
    // Use GET method to match backend endpoint
    const response = await fetch(`${BACKEND_URL}/certificates/employee-suggestions/${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout to prevent hanging (if AbortSignal.timeout is not available, will gracefully handle)
      // Note: AbortSignal.timeout() requires Node.js 17.3+ or modern browsers
    })
    
    if (!response.ok) {
      throw new Error(`Employee search error: ${response.statusText}`)
    }

    const data = await response.json()

    return NextResponse.json({
      success: data.success || false,
      suggestions: data.suggestions || [],
      count: data.count || 0,
      error: data.error || undefined,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Employee search error:', error)
    
    let errorMessage = 'Unknown error occurred'
    let statusCode = 500
    
    if (error instanceof Error) {
      errorMessage = error.message
      
      // Handle connection errors specifically
      if (errorMessage.includes('ECONNREFUSED') || errorMessage.includes('fetch failed')) {
        errorMessage = 'Backend server is not reachable. Please ensure the backend is running on port 8000.'
        statusCode = 503 // Service Unavailable
      } else if (errorMessage.includes('timeout') || errorMessage.includes('aborted')) {
        errorMessage = 'Request timed out. Please try again.'
        statusCode = 504 // Gateway Timeout
      }
    }
    
    return NextResponse.json(
      { 
        success: false,
        error: errorMessage,
        suggestions: [],
        count: 0
      },
      { status: statusCode }
    )
  }
}
