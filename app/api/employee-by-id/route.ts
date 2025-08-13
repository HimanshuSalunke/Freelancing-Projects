import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    // Validate request
    if (!request.body) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Request body is required',
          employee: null
        },
        { status: 400 }
      )
    }

    const body = await request.json()
    
    // Validate body structure
    if (!body || typeof body !== 'object') {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid request body format',
          employee: null
        },
        { status: 400 }
      )
    }

    const { employeeId } = body

    // Validate employeeId
    if (!employeeId || typeof employeeId !== 'string' || employeeId.trim().length === 0) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Employee ID is required and must be a non-empty string',
          employee: null
        },
        { status: 400 }
      )
    }

    // Check employeeId length
    if (employeeId.length > 50) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Employee ID is too long (maximum 50 characters)',
          employee: null
        },
        { status: 400 }
      )
    }

    // Forward the request to the FastAPI backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    const response = await fetch(`${backendUrl}/certificates/employee/${encodeURIComponent(employeeId.trim())}`, {
      method: 'GET',
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Employee by ID failed:', response.status, errorText)
      
      // Try to parse error as JSON for better error messages
      let errorMessage = 'Employee not found'
      try {
        const errorJson = JSON.parse(errorText)
        errorMessage = errorJson.detail || errorJson.error || errorJson.message || errorMessage
      } catch {
        errorMessage = `${errorMessage}: ${errorText}`
      }
      
      return NextResponse.json(
        { 
          success: false,
          error: errorMessage,
          employee: null
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Validate backend response
    if (!data || typeof data !== 'object') {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid response format from backend',
          employee: null
        },
        { status: 500 }
      )
    }
    
    // Validate response structure and ensure employee is properly formatted
    const employee = data.employee || null
    const success = data.success === true
    
    return NextResponse.json({
      success,
      employee,
      error: data.error || undefined
    })

  } catch (error) {
    console.error('Employee by ID error:', error)
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
    
    return NextResponse.json(
      { 
        success: false,
        error: `Failed to get employee by ID: ${errorMessage}`,
        employee: null
      },
      { status: 500 }
    )
  }
}
