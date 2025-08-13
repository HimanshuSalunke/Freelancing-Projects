# Reliance Jio Infotech Solutions - AI-Powered HR Assistant

A modern, enhanced Next.js frontend for the AI-powered HR assistant with advanced document processing, PDF summarization, and HR Q&A capabilities.

## 🚀 Features

### ✨ Enhanced UI/UX
- **Modern Next.js 14** with App Router
- **Responsive Design** with Tailwind CSS
- **Smooth Animations** using Framer Motion
- **Real-time Interactions** with React hooks
- **Professional Branding** with Reliance Jio theme

### 🤖 AI-Powered Capabilities
- **HR Q&A Chat** - Ask questions about company policies and procedures
- **PDF Summarization** - Upload large PDFs (up to 50MB) for intelligent summaries
- **Document Generation** - Generate 16 types of official HR documents
- **Enhanced Security** - ISO 27001 certified features with digital signatures

### 📄 Document Types Supported
1. Bonafide / Employment Verification Letter
2. Experience Certificate
3. Offer Letter Copy
4. Appointment Letter Copy
5. Promotion Letter
6. Relieving Letter
7. Salary Slips
8. Form 16 / Tax Documents
9. Salary Certificate
10. PF Statement / UAN details
11. No Objection Certificate (NOC)
12. Non-Disclosure Agreement Copy
13. ID Card Replacement
14. Medical Insurance Card Copy
15. Business Travel Authorization Letter
16. Visa Support Letter

### 🎨 Premium Design Features
- **Professional Company Logo** and branding
- **Digital Signatures** with security indicators
- **QR Code Integration** for instant verification
- **Enhanced Borders** and watermarks
- **ISO 27001 Security** features

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications
- **React Dropzone** - File upload handling

### Backend Integration
- **FastAPI** - Python backend (separate repository)
- **ReportLab** - PDF generation
- **AI/ML** - Document processing and summarization

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot_project
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   Create a `.env.local` file:
   ```env
   BACKEND_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   │   ├── chat/          # HR Q&A chat endpoint
│   │   ├── upload-pdf/    # PDF upload endpoint
│   │   ├── process-pdf/   # PDF processing endpoint
│   │   └── generate-document/ # Document generation endpoint
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── Header.tsx         # Application header
│   ├── ModeSelector.tsx   # Mode selection interface
│   ├── ChatInterface.tsx  # HR Q&A chat interface
│   ├── PDFUploader.tsx    # PDF upload and processing
│   └── DocumentForm.tsx   # Document generation forms
├── lib/                   # Utility functions
│   └── utils.ts           # Helper functions
├── backend/               # FastAPI backend (existing)
├── static/                # Static files (existing)
└── package.json           # Dependencies and scripts
```

## 🔧 Configuration

### Environment Variables
- `BACKEND_URL` - FastAPI backend URL (default: `http://localhost:8000`)

### Tailwind Configuration
Custom colors and animations are defined in `tailwind.config.js`:
- Primary color scheme
- Jio brand colors
- Custom animations
- Responsive breakpoints

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Other Platforms
- **Netlify** - Static site hosting
- **AWS Amplify** - Full-stack hosting
- **Docker** - Containerized deployment

## 🔌 API Integration

The Next.js frontend communicates with the FastAPI backend through:

### Chat API
- `POST /api/chat` - HR Q&A chat functionality

### PDF Processing
- `POST /api/upload-pdf` - Upload PDF files
- `POST /api/process-pdf` - Process and summarize PDFs

### Document Generation
- `POST /api/generate-document` - Generate HR documents

## 🎯 Key Features

### 1. HR Q&A Chat
- Real-time chat interface
- Semantic search capabilities
- Company policy assistance
- Benefits and procedure guidance

### 2. PDF Summarization
- Drag-and-drop file upload
- Large file support (up to 50MB)
- Intelligent chunking and processing
- Progress tracking
- Download summaries

### 3. Document Generation
- 16 official document types
- Form-based data collection
- Real-time validation
- Enhanced PDF output
- Preview and download options

### 4. Enhanced Security
- Digital signatures
- QR code verification
- ISO 27001 compliance
- Professional branding

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradient (`#3b82f6` to `#1d4ed8`)
- **Secondary**: Purple gradient (`#7c3aed` to `#5b21b6`)
- **Success**: Green (`#059669`)
- **Jio Brand**: Custom blue and green tones

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Responsive**: Mobile-first design

### Animations
- **Fade In/Out**: Smooth transitions
- **Scale**: Hover effects
- **Slide**: Page transitions
- **Pulse**: Loading states

## 🔒 Security Features

- **Input Validation** - Client and server-side validation
- **File Type Checking** - PDF-only uploads
- **Size Limits** - 50MB file size restriction
- **CORS Protection** - Secure API communication
- **Error Handling** - Graceful error management

## 📱 Responsive Design

- **Mobile First** - Optimized for mobile devices
- **Tablet Support** - Responsive grid layouts
- **Desktop Enhanced** - Full feature access
- **Touch Friendly** - Optimized for touch interactions

## 🧪 Testing

### Development Testing
```bash
# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Build testing
npm run build
```

### Manual Testing
- Test all 16 document types
- Verify PDF upload and processing
- Check chat functionality
- Validate responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary to Reliance Jio Infotech Solutions.

## 🆘 Support

For technical support or questions:
- Check the documentation
- Review existing issues
- Contact the development team

## 🔄 Migration from Old Frontend

This Next.js frontend replaces the old HTML/CSS/JavaScript interface while maintaining all existing functionality:

### Preserved Features
- All 16 document types
- PDF upload and processing
- HR Q&A chat
- Enhanced PDF design
- Security features

### Enhanced Features
- Modern React components
- Better performance
- Improved UX/UI
- Type safety
- Better error handling
- Responsive design

### Backend Compatibility
- Uses existing FastAPI endpoints
- Maintains data structure
- Preserves validation logic
- Compatible with existing PDF generation

---

**Built with ❤️ for Reliance Jio Infotech Solutions**
