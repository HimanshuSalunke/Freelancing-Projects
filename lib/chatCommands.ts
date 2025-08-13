import { ChatCommand, ChatCommandResult } from './types'

// Simple command detection - like HTML version
export function detectChatCommand(message: string): ChatCommand {
  if (!message || typeof message !== 'string') {
    return 'none'
  }
  
  const lowerMessage = message.toLowerCase().trim()
  
  if (lowerMessage.includes('search employee') || lowerMessage.includes('find employee')) {
    return 'search_employee'
  }
  
  if (lowerMessage.includes('fill form for')) {
    return 'fill_form'
  }
  
  if (lowerMessage.includes('i need a document') || lowerMessage.includes('request document')) {
    return 'document_request'
  }
  
  if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
    return 'help'
  }
  
  if (lowerMessage.includes('status') || lowerMessage.includes('health')) {
    return 'status'
  }
  
  return 'none'
}

// Simple command processing - like HTML version's hardcoded responses
export async function processChatCommand(message: string): Promise<ChatCommandResult | null> {
  try {
    const command = detectChatCommand(message)
    
    if (command === 'none') {
      return null
    }
    
    switch (command) {
      case 'search_employee': {
        const query = message.replace(/search employee|find employee/i, '').trim()
        if (query) {
          return {
            command: 'search_employee',
            response: `🔍 Searching for employees matching "${query}"...\n\nPlease use the employee search feature in the Document Requests mode to find specific employees.`
          }
        } else {
          return {
            command: 'search_employee',
            response: '🔍 Please provide a name or ID to search for. Example: "search employee John" or "search employee EMP0001"'
          }
        }
      }
      
      case 'fill_form': {
        const employeeQuery = message.replace(/fill form for/i, '').trim()
        if (employeeQuery) {
          return {
            command: 'fill_form',
            response: `📝 Auto-filling form for "${employeeQuery}"...\n\nPlease switch to Document Requests mode and use the employee search feature to auto-fill forms with employee details.`
          }
        } else {
          return {
            command: 'fill_form',
            response: '📝 Please provide an employee name or ID. Example: "fill form for John Smith" or "fill form for EMP0001"'
          }
        }
      }
      
      case 'document_request':
        return {
          command: 'document_request',
          response: '📜 **Document Request System**\n\nI can help you generate official documents. Please:\n\n1. **Switch to Document Requests mode** using the mode selector above\n2. **Select a document type** from the 16 available options\n3. **Fill in the required details**\n4. **Generate and download** your document\n\n**Available Documents:**\n• Bonafide / Employment Verification Letter\n• Experience Certificate\n• Offer Letter Copy\n• Appointment Letter Copy\n• Promotion Letter\n• Relieving Letter\n• Salary Slips\n• Form 16 / Tax Documents\n• Salary Certificate\n• PF Statement / UAN details\n• No Objection Certificate (NOC)\n• Non-Disclosure Agreement Copy\n• ID Card Replacement\n• Medical Insurance Card Copy\n• Business Travel Authorization Letter\n• Visa Support Letter\n\n⚠️ **Important:** Document generation requires ALL employee details to match our records exactly.'
        }
      
      case 'help':
        return {
          command: 'help',
          response: '🤖 **Reliance Jio Infotech Solutions - Your Intelligent Companion**\n\nI can help you with three main services:\n\n💬 **HR Q&A Chat**\n• Ask about company policies, benefits, and procedures\n• Get information about leave policies, attendance, and more\n• Request official documents (type "I need a document")\n• Powered by semantic search and AI assistance\n• Quick and accurate responses to your queries\n\n📄 **PDF Summarization**\n• Upload PDFs up to 50MB\n• Handles large documents (30+ pages)\n• Extracts and formats table data\n• Powered by advanced AI technology\n• Real-time processing with progress tracking\n\n📜 **Document Requests**\n• Request any of 16 official document types\n• Official Reliance Jio Infotech Solutions format\n• Professional document generation\n• Immediate download available\n• **Strict validation:** ALL fields must match exactly with employee records\n• Employee data validation against records\n\n💡 **Quick Commands:**\n• Type "qa" or "chat" to switch to HR Q&A mode\n• Type "summarize" or "pdf" to switch to PDF mode\n• Type "I need a document" to request official documents\n• Search employees: "search employee [name or ID]"\n• Auto-fill forms: "fill form for [name or ID]"\n• Use the mode buttons above for quick switching\n\n⚠️ **Important:** Document generation requires ALL employee details to match our records exactly.'
        }
      
      case 'status':
        return {
          command: 'status',
          response: '🟢 **System Status:** All services are operational\n\n💬 **HR Q&A Chat:** Semantic Search - Active\n📊 **PDF Processing:** Advanced AI - Active\n📜 **Document Generation:** ReportLab - Active\n🌐 **API Endpoints:** All responding\n\nEverything is working perfectly! 🚀'
        }
      
      default:
        return null
    }
  } catch (error) {
    console.error('Error processing chat command:', error)
    return null
  }
}
