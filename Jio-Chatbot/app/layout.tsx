import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'
import { getCompanyName, getAppName } from '@/lib/config'

const inter = Inter({ subsets: ['latin'] })

const companyName = getCompanyName()
const appName = getAppName()

export const metadata: Metadata = {
  title: `${companyName} - AI-Powered HR Assistant`,
  description: `Advanced AI-powered document processing, HR Q&A, and PDF summarization for ${companyName}. Get instant answers, generate official documents, and process large PDFs with intelligent AI assistance.`,
  keywords: `HR Assistant, Document Processing, PDF Summarization, AI Chatbot, ${companyName}, Employee Documents`,
  authors: [{ name: companyName }],
  robots: 'index, follow',
  openGraph: {
    title: `${companyName} - AI-Powered HR Assistant`,
    description: 'Advanced AI-powered document processing and HR assistance',
    type: 'website',
    locale: 'en_US',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta httpEquiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <meta httpEquiv="Pragma" content="no-cache" />
        <meta httpEquiv="Expires" content="0" />
      </head>
      <body className={inter.className}>
        {children}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#059669',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  )
}
