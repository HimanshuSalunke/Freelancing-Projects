'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot } from 'lucide-react'
import { Message } from '@/lib/types'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Handle hydration
  useEffect(() => {
    setIsClient(true)
    // Initialize messages only on client side - same as HTML version
    setMessages([
      {
        id: '1',
        type: 'assistant',
        content: 'I\'m ready to help you with HR questions! 💬\n\n• Ask about company policies, benefits, and procedures\n• Get information about leave policies, attendance, and more\n• Request official documents (type "I need a document")\n• Powered by semantic search and AI assistance\n• Quick and accurate responses to your queries\n\nJust type your question and I\'ll help you find the information you need!',
        timestamp: new Date()
      }
    ])
  }, [])

  // Auto-scroll to bottom - same as HTML version
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Focus input after message is sent
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isLoading])

  // Simple message sending - exactly like HTML version's handleQAMessage
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Simple fetch to /chat API - exactly like HTML version
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage.trim() })
      })

      if (!response.ok) {
        throw new Error(`QA API error: ${response.statusText}`)
      }

      const data = await response.json()

      if (data.response) {
        // Check if response is a special form trigger - same as HTML version
        if (data.response.startsWith('SHOW_FORM:')) {
          const parts = data.response.split(':')
          if (parts.length === 3) {
            const docType = parts[1]
            const docName = parts[2]
            const formMessage = `📝 Please fill in the details below to generate your ${docName}.`
            addMessage('assistant', formMessage)
          } else {
            addMessage('assistant', data.response)
          }
        } else {
          addMessage('assistant', data.response)
        }
      } else {
        addMessage('assistant', '❌ Sorry, I couldn\'t process your question. Please try again.')
      }

    } catch (error) {
      console.error('QA Error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      addMessage('assistant', `❌ Sorry, I encountered an error processing your question: ${errorMessage}\n\nPlease try again or contact support if the issue persists.`)
    } finally {
      setIsLoading(false)
    }
  }

  // Simple message adding - same as HTML version
  const addMessage = (type: 'user' | 'assistant', content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, message])
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Don't render until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing chat...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">HR Q&A Chat</h2>
              <p className="text-blue-100 text-sm">Ask questions about policies, benefits, and procedures</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4" ref={messagesEndRef}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs md:max-w-md lg:max-w-lg rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
              </div>
            </div>
          ))}
          
          {/* Typing indicator - same as HTML version */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="animate-pulse">🤖</div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your question here..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

