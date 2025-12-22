/**
 * Frontend configuration
 * Uses Next.js environment variables (NEXT_PUBLIC_*)
 * 
 * These values are embedded at build time and are safe to expose to the client.
 * For production, set these in your deployment environment or .env.local file.
 */

export const config = {
  company: {
    name: process.env.NEXT_PUBLIC_COMPANY_NAME || 'TechCorp Solutions',
    appName: process.env.NEXT_PUBLIC_APP_NAME || 'TechCorp HR Assistant',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
} as const

// Helper functions for easy access
export const getCompanyName = () => config.company.name
export const getAppName = () => config.company.appName
export const getApiUrl = () => config.api.baseUrl

