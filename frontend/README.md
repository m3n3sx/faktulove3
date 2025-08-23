# FaktuLove OCR Frontend

Modern React-based frontend for the FaktuLove OCR system with AI-powered invoice processing capabilities.

## 🚀 Features

- **Modern UI/UX**: Clean, responsive design with Tailwind CSS
- **Real-time Processing**: Live status updates and progress tracking
- **Drag & Drop Upload**: Intuitive file upload with drag-and-drop support
- **Advanced Analytics**: Comprehensive statistics and performance metrics
- **Polish Invoice Optimization**: Specialized patterns for Polish invoices
- **Mobile Responsive**: Works seamlessly on all devices
- **Real-time Notifications**: Toast notifications for user feedback

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks and functional components
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **React Dropzone** - File upload with drag-and-drop
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications
- **Axios** - HTTP client

## 📦 Installation

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Django backend running on port 8000

### Quick Start

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Or use the automated script:**
   ```bash
   ./start_frontend.sh
   ```

The frontend will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   └── manifest.json       # PWA manifest
├── src/
│   ├── components/         # Reusable components
│   │   └── Layout.js       # Main layout with navigation
│   ├── pages/              # Page components
│   │   ├── Dashboard.js    # Main dashboard
│   │   ├── UploadPage.js   # Document upload
│   │   ├── DocumentsPage.js # Document management
│   │   ├── StatisticsPage.js # Analytics
│   │   └── SettingsPage.js # System settings
│   ├── App.js              # Main app component
│   ├── index.js            # App entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
└── tailwind.config.js      # Tailwind configuration
```

## 🎨 Design System

### Colors
- **Primary**: Blue (#3b82f6) - Main brand color
- **Success**: Green (#22c55e) - Success states
- **Warning**: Yellow (#f59e0b) - Warning states  
- **Error**: Red (#ef4444) - Error states

### Components
- **Buttons**: Primary, secondary, and danger variants
- **Cards**: Consistent card layouts with headers and bodies
- **Status Badges**: Color-coded status indicators
- **Loading States**: Spinners and skeleton loaders

## 📱 Pages

### Dashboard
- Overview statistics and metrics
- Recent activity feed
- Quick action buttons
- Real-time processing status

### Upload Documents
- Drag-and-drop file upload
- File validation and preview
- Real-time processing status
- Batch upload support

### Documents
- Document list with filtering
- Search and sort functionality
- Detailed OCR results view
- Document management actions

### Statistics
- Comprehensive analytics
- Performance metrics
- File type distribution
- Processing time analysis
- Business impact metrics

### Settings
- OCR processing configuration
- System preferences
- Notification settings
- Security configuration

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
```

### API Integration

The frontend communicates with the Django backend via REST API:

- **Base URL**: `http://localhost:8000`
- **API Endpoints**: `/api/ocr/*`
- **Authentication**: Session-based (Django)
- **CORS**: Configured for development

## 🚀 Development

### Available Scripts

```bash
npm start          # Start development server
npm build          # Build for production
npm test           # Run tests
npm eject          # Eject from Create React App
```

### Development Workflow

1. **Start Django backend:**
   ```bash
   python manage.py runserver
   ```

2. **Start React frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Hot Reload

The development server supports hot reloading. Changes to React components will automatically refresh the browser.

## 📊 Mock Data

During development, the frontend uses mock data when the backend is not available:

- **Dashboard Statistics**: Sample metrics and trends
- **Document List**: Example documents with OCR results
- **Upload Simulation**: Mock upload and processing
- **Settings**: Default configuration values

## 🎯 Key Features

### Polish Invoice Optimization
- Specialized pattern recognition for Polish invoices
- NIP (tax ID) validation with checksum
- Polish date format support (DD.MM.YYYY)
- Currency pattern recognition (zł, PLN)
- Company name detection (Sp. z o.o., S.A.)

### Real-time Processing
- Live status updates during OCR processing
- Progress indicators and estimated completion time
- Automatic polling for processing status
- Real-time confidence score updates

### Advanced Analytics
- Processing performance metrics
- File type distribution analysis
- Confidence score distribution
- Business impact calculations
- Time savings estimation

## 🔒 Security

- **CORS Configuration**: Properly configured for development
- **Input Validation**: Client-side validation for file uploads
- **Error Handling**: Graceful error handling and user feedback
- **Session Management**: Secure session handling

## 📱 Responsive Design

The frontend is fully responsive and optimized for:

- **Desktop**: Full-featured interface with sidebar navigation
- **Tablet**: Adaptive layout with touch-friendly controls
- **Mobile**: Mobile-first design with collapsible navigation

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## 🚀 Production Build

```bash
# Create production build
npm run build

# Build with source maps disabled
npm run build:prod
```

The build output will be in the `build/` directory, ready for deployment.

## 🔧 Troubleshooting

### Common Issues

1. **Port 3000 already in use:**
   ```bash
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **Node modules issues:**
   ```bash
   # Clear npm cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Backend connection issues:**
   - Ensure Django server is running on port 8000
   - Check CORS configuration in Django settings
   - Verify API endpoints are accessible

### Development Tips

- Use React Developer Tools for debugging
- Check browser console for errors
- Monitor network tab for API calls
- Use React Query DevTools for data debugging

## 📈 Performance

- **Code Splitting**: Automatic code splitting with React Router
- **Lazy Loading**: Components loaded on demand
- **Caching**: React Query for efficient data caching
- **Optimization**: Production builds with minification

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Ensure responsive design works
5. Test with mock data and real API

## 📄 License

This project is part of the FaktuLove OCR system and follows the same license terms.

---

**Built with ❤️ for efficient invoice processing**
