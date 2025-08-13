import { 
  ChatAPIResponse, 
  EmployeeSearchResponse, 
  EmployeeByIdResponse,
  Employee 
} from './types'

// Simple API Configuration - like HTML version
const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
}

// Simple chat message sending - like HTML version's handleQAMessage
export async function sendChatMessage(message: string): Promise<ChatAPIResponse> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message })
    })

    if (!response.ok) {
      throw new Error(`QA API error: ${response.statusText}`)
    }

    const data = await response.json()
    
    return {
      success: true,
      response: data.response || '',
      error: undefined
    }
  } catch (error) {
    console.error('QA Error:', error)
    throw error instanceof Error ? error : new Error('Unknown error occurred')
  }
}

// Simple employee search - like HTML version's searchEmployees
export async function searchEmployees(query: string): Promise<EmployeeSearchResponse> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/certificates/employee-suggestions/${encodeURIComponent(query)}`)
    
    if (!response.ok) {
      throw new Error(`Employee search error: ${response.statusText}`)
    }

    const data = await response.json()
    
    return {
      success: data.success || false,
      suggestions: data.suggestions || [],
      count: data.count || 0,
      error: data.error || undefined
    }
  } catch (error) {
    console.error('Employee search error:', error)
    throw error instanceof Error ? error : new Error('Unknown error occurred')
  }
}

// Simple employee by ID lookup - like HTML version
export async function getEmployeeById(employeeId: string): Promise<EmployeeByIdResponse> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/certificates/employee/${employeeId}`)
    
    if (!response.ok) {
      throw new Error(`Employee lookup error: ${response.statusText}`)
    }

    const data = await response.json()
    
    return {
      success: data.success || false,
      employee: data.employee || undefined,
      error: data.error || undefined
    }
  } catch (error) {
    console.error('Employee by ID error:', error)
    throw error instanceof Error ? error : new Error('Unknown error occurred')
  }
}

// Simple employee data validation - basic checks only
export function validateEmployeeData(employee: any): employee is Employee {
  if (!employee || typeof employee !== 'object') {
    return false
  }
  
  // Basic required fields check
  if (!employee.full_name || !employee.employee_code) {
    return false
  }
  
  return true
}

// Simple employee formatting - like HTML version
export function formatEmployeeForDisplay(employee: Employee): string {
  if (!validateEmployeeData(employee)) {
    return 'Invalid employee data'
  }
  
  return `**${employee.full_name}**\n` +
         `**ID:** ${employee.employee_code}\n` +
         `**Designation:** ${employee.designation || 'Not specified'}\n` +
         `**Department:** ${employee.department || 'Not specified'}\n` +
         `**Joining Date:** ${employee.joining_date || 'Not specified'}`
}

// Simple health check - like HTML version
export async function checkAPIHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/health`)
    return response.ok
  } catch (error) {
    console.error('Health check failed:', error)
    return false
  }
}
