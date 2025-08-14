'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Upload, 
  FileText, 
  MessageCircle, 
  Download, 
  Eye, 
  Copy,
  Sparkles,
  Shield,
  Zap,
  Users,
  FileCheck,
  Bot,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import toast from 'react-hot-toast'
import ChatInterface from '@/components/ChatInterface'
import DocumentForm from '@/components/DocumentForm'
import PDFUploader from '@/components/PDFUploader'
import ModeSelector from '@/components/ModeSelector'
import Header from '@/components/Header'
import ErrorBoundary from '@/components/ErrorBoundary'
import { cn } from '@/lib/utils'

export default function Home() {
  const [currentMode, setCurrentMode] = useState<'chat' | 'pdf' | 'documents'>('chat')
  const [showFeatures, setShowFeatures] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const mainContainerRef = useRef<HTMLDivElement>(null)
  const interfaceSectionRef = useRef<HTMLDivElement>(null)

  // Handle hydration and ensure page starts at top
  useEffect(() => {
    setIsClient(true)
    
    // Ensure page scrolls to top on load/reload
    window.scrollTo(0, 0)
  }, [])

  // Handle scrolling when mode changes (triggered by feature card clicks)
  const [shouldScrollToInterface, setShouldScrollToInterface] = useState(false)
  
  useEffect(() => {
    if (shouldScrollToInterface) {
      setTimeout(() => {
        if (interfaceSectionRef.current) {
          interfaceSectionRef.current.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          })
        }
        setShouldScrollToInterface(false)
      }, 100)
    }
  }, [currentMode, shouldScrollToInterface])



  // Handle feature card clicks
  const handleFeatureClick = (featureTitle: string) => {
    let targetMode: 'chat' | 'pdf' | 'documents' = 'chat'
    
    // Map feature titles to modes
    if (featureTitle.includes('Q&A') || featureTitle.includes('Chat')) {
      targetMode = 'chat'
    } else if (featureTitle.includes('PDF') || featureTitle.includes('Summarization')) {
      targetMode = 'pdf'
    } else if (featureTitle.includes('Document') || featureTitle.includes('Request')) {
      targetMode = 'documents'
    }
    
    console.log('Feature clicked:', featureTitle, 'Target mode:', targetMode)
    
    // Set the mode and trigger scroll
    setCurrentMode(targetMode)
    setShouldScrollToInterface(true)
  }

  const features = [
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: "HR Q&A Chat",
      description: "Ask questions about company policies, benefits, and procedures with semantic search and AI assistance"
    },
    {
      icon: <FileText className="w-6 h-6" />,
      title: "PDF Summarization",
      description: "Upload large PDFs (30+ pages) with tables and get comprehensive summaries with advanced AI processing"
    },
    {
      icon: <FileCheck className="w-6 h-6" />,
      title: "Document Requests",
      description: "Request any of 16 official document types through chat with form-based data collection"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Enhanced Security",
      description: "Digital signatures and verification elements"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Processing",
      description: "Handles large PDFs up to 50MB with intelligent chunking and progress tracking"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Employee Validation",
      description: "Seamless employee data validation against records with form-based requests"
    }
  ]

  // Don't render until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <main ref={mainContainerRef} className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full mb-6"
          >
            <Sparkles className="w-5 h-5" />
            <span className="font-semibold">AI-Powered HR Assistant</span>
          </motion.div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Welcome to{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Reliance Jio
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Your intelligent companion for HR Q&A, document processing, and official document requests. 
            Powered by advanced AI for superior accuracy and efficiency.
          </p>

          {/* Features Toggle */}
          <div className="mb-8">
            <button
              onClick={() => setShowFeatures(!showFeatures)}
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              {showFeatures ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              {showFeatures ? 'Hide Features' : 'View Key Features'}
            </button>
          </div>

          {/* Features Grid */}
          <AnimatePresence>
            {showFeatures && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
              >
                {features.map((feature, index) => {
                  // Determine if this feature is currently active
                  const isActive = 
                    (feature.title.includes('Q&A') || feature.title.includes('Chat')) && currentMode === 'chat' ||
                    (feature.title.includes('PDF') || feature.title.includes('Summarization')) && currentMode === 'pdf' ||
                    (feature.title.includes('Document') || feature.title.includes('Request')) && currentMode === 'documents'
                  
                  return (
                    <motion.div
                      key={feature.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={cn(
                        "card-clickable",
                        isActive && "ring-2 ring-blue-500 bg-blue-50/50 border-blue-300"
                      )}
                      onClick={() => handleFeatureClick(feature.title)}
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className={cn(
                          "p-2 rounded-lg",
                          isActive ? "bg-blue-200 text-blue-700" : "bg-blue-100 text-blue-600"
                        )}>
                          {feature.icon}
                        </div>
                        <h3 className="font-semibold text-gray-900">{feature.title}</h3>
                      </div>
                      <p className="text-gray-600 text-sm">{feature.description}</p>
                    </motion.div>
                  )
                })}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Mode Selector */}
        <ModeSelector 
          currentMode={currentMode} 
          onModeChange={setCurrentMode}
          onModeChangeWithScroll={(mode) => {
            setCurrentMode(mode)
            setShouldScrollToInterface(true)
          }}
        />

        {/* Main Interface */}
        <ErrorBoundary>
          <motion.div
            key={currentMode}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="mt-8"
            ref={interfaceSectionRef}
          >
            {currentMode === 'chat' && <ChatInterface />}
            {currentMode === 'pdf' && <PDFUploader />}
            {currentMode === 'documents' && <DocumentForm />}
          </motion.div>
        </ErrorBoundary>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Bot className="w-6 h-6 text-blue-400" />
            <span className="text-xl font-semibold">Reliance Jio Infotech Solutions</span>
          </div>
          <p className="text-gray-400">
            Advanced AI-Powered Document Processing & HR Q&A System
          </p>
          <p className="text-gray-500 text-sm mt-2">
            © 2024 Reliance Jio Infotech Solutions. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
