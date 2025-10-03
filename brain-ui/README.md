# Brain UI - Web Interface for .brain/ Content

A modern React-based web interface for visualizing and navigating your `.brain/` directory content. Built with Vite for fast development and optimized production builds.

## 🌟 Features

- **Dashboard**: Project overview với stats và quick navigation
- **Documentation Viewer**: Markdown files với syntax highlighting  
- **Tasks Management**: ACTIVE_TASKS.json với filtering và progress tracking
- **Responsive Design**: Mobile-friendly với dark mode support
- **Static Site**: Deployable to GitHub Pages, Vercel, Netlify
- **Vietnamese Support**: Mixed Vietnamese/English content

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ và npm/yarn
- Your project với `.brain/` directory structure

### Installation

```powershell
# Clone hoặc copy brain-ui/ folder vào project của bạn
cd your-project/brain-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

Development server sẽ chạy trên http://localhost:5173

### Build for Production

```powershell
# Build static files
npm run build

# Preview production build locally  
npm run preview
```

Built files sẽ ở trong `dist/` directory.

## 📁 Project Structure

```
brain-ui/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.jsx    # Main dashboard
│   │   ├── Sidebar.jsx      # Navigation sidebar  
│   │   ├── MarkdownViewer.jsx # Markdown file display
│   │   └── TasksViewer.jsx  # Tasks management
│   ├── App.jsx             # Main app component
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles
├── public/                 # Static assets
├── dist/                   # Production build (after npm run build)
├── package.json
├── vite.config.js
└── README.md
```

## 🔧 Configuration

### Brain Data Integration

Currently uses sample data. To integrate with real `.brain/` files:

1. Copy your `.brain/` files to `public/brain/`:
```powershell
# Copy brain files to public directory
Copy-Item -Recurse .brain/* brain-ui/public/brain/
```

2. Update components to fetch from `/brain/` endpoints:
```javascript
// Example: MarkdownViewer.jsx
const response = await fetch('/brain/documentation/SCOPE.md');
const content = await response.text();
```

### Customization

#### Colors & Themes
Edit CSS variables in `src/index.css`:
```css
:root {
  --primary: #3b82f6;        /* Change primary color */
  --card-bg: #ffffff;        /* Card backgrounds */
  --text-primary: #1f2937;   /* Main text color */
}
```

#### Navigation Menu
Update `src/components/Sidebar.jsx` để customize menu items:
```javascript
const menuItems = [
  // Add your custom menu items
  { path: '/custom', label: 'Custom Page', icon: '🔧' }
];
```

## 🌐 Deployment

### GitHub Pages

1. Build project:
```powershell
npm run build
```

2. Push `dist/` contents to `gh-pages` branch:
```powershell
# Using gh-pages package (install first: npm install --save-dev gh-pages)
npm run deploy
```

Or manual:
```powershell
# Copy dist contents to gh-pages branch
git checkout -b gh-pages
Copy-Item -Recurse dist/* .
git add .
git commit -m "Deploy brain-ui"
git push origin gh-pages
```

3. Enable GitHub Pages trong repository settings

### Vercel

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Netlify

```powershell
# Install Netlify CLI  
npm install -g netlify-cli

# Deploy
npm run build
netlify deploy --prod --dir=dist
```

### Docker (Optional)

```dockerfile
# Dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```powershell
# Build và run
docker build -t brain-ui .
docker run -p 8080:80 brain-ui
```

## 🛠️ Development

### Adding New Components

1. Create component file in `src/components/`:
```javascript
// src/components/NewComponent.jsx
import React from 'react';
import './NewComponent.css';

function NewComponent() {
  return <div>New Component</div>;
}

export default NewComponent;
```

2. Add CSS file với same naming pattern
3. Import vào `App.jsx` và add route if needed

### Data Integration

Components currently use sample data. For real integration:

1. **Static Files Approach** (Recommended):
   - Copy `.brain/` files to `public/brain/`
   - Fetch via standard HTTP requests

2. **API Approach**:
   - Create backend API endpoints
   - Update components để call API

### Styling Guidelines

- Use CSS variables for consistent theming
- Follow mobile-first responsive design
- Use semantic HTML elements
- Maintain accessibility (ARIA labels, keyboard navigation)

## 📱 Mobile Support

Interface fully responsive với breakpoints:
- Desktop: 1024px+
- Tablet: 768px - 1023px  
- Mobile: 480px - 767px
- Small Mobile: < 480px

## 🔍 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🐛 Troubleshooting

### Build Issues

```powershell
# Clear cache và reinstall
Remove-Item -Recurse node_modules
Remove-Item package-lock.json
npm install
```

### Routing Issues on Static Hosts

Add `_redirects` file to `public/` directory:
```
/*    /index.html   200
```

### CORS Issues với Brain Files

Ensure brain files are served từ same origin hoặc configure CORS headers properly.

## 📈 Performance

- Vite provides fast HMR trong development
- Production build includes:
  - Code splitting
  - Asset optimization  
  - Tree shaking
  - Minification

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes với proper testing
4. Submit pull request

## 📄 License

This project follows the same license as your main project.

## 🔗 Links

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Brain Template System](../PROJECT_TEMPLATE/)

---

Built with ❤️ for the Brain ecosystem