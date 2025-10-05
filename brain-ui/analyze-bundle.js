import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import fs from 'fs';

// Bundle analyzer function
function bundleAnalyzer() {
  return {
    name: 'bundle-analyzer',
    writeBundle(options, bundle) {
      const bundleStats = {};
      let totalSize = 0;
      
      for (const [fileName, chunk] of Object.entries(bundle)) {
        if (chunk.type === 'chunk') {
          const size = chunk.code ? chunk.code.length : 0;
          bundleStats[fileName] = {
            size: size,
            sizeFormatted: formatBytes(size),
            modules: chunk.modules ? Object.keys(chunk.modules) : []
          };
          totalSize += size;
        } else if (chunk.type === 'asset') {
          const size = chunk.source ? chunk.source.length : 0;
          bundleStats[fileName] = {
            size: size,
            sizeFormatted: formatBytes(size),
            type: 'asset'
          };
          totalSize += size;
        }
      }

      const analysis = {
        totalSize: totalSize,
        totalSizeFormatted: formatBytes(totalSize),
        files: bundleStats,
        recommendations: getRecommendations(bundleStats, totalSize)
      };

      fs.writeFileSync(
        resolve(options.dir, 'bundle-analysis.json'),
        JSON.stringify(analysis, null, 2)
      );

      console.log('\n📊 Bundle Analysis Complete:');
      console.log(`Total Size: ${formatBytes(totalSize)}`);
      console.log('\nLargest Files:');
      
      const sortedFiles = Object.entries(bundleStats)
        .sort(([,a], [,b]) => b.size - a.size)
        .slice(0, 5);
        
      sortedFiles.forEach(([name, stats]) => {
        console.log(`  ${name}: ${stats.sizeFormatted}`);
      });
      
      console.log('\nRecommendations:');
      analysis.recommendations.forEach(rec => {
        console.log(`  • ${rec}`);
      });
    }
  };
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getRecommendations(bundleStats, totalSize) {
  const recommendations = [];
  
  if (totalSize > 1024 * 1024) {
    recommendations.push('Bundle size > 1MB - consider code splitting');
  }
  
  const jsFiles = Object.entries(bundleStats).filter(([name]) => name.endsWith('.js'));
  if (jsFiles.length > 1) {
    recommendations.push('Multiple JS files detected - good code splitting');
  }
  
  const largestFile = Object.entries(bundleStats)
    .sort(([,a], [,b]) => b.size - a.size)[0];
    
  if (largestFile && largestFile[1].size > 500 * 1024) {
    recommendations.push(`Largest file (${largestFile[0]}) > 500KB - consider optimization`);
  }
  
  recommendations.push('Consider lazy loading for Chart.js');
  recommendations.push('Optimize images with webp format');
  recommendations.push('Enable gzip compression in production');
  
  return recommendations;
}

export default defineConfig({
  plugins: [react(), bundleAnalyzer()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['chart.js', 'react-chartjs-2'],
          utils: ['html2canvas', 'jspdf']
        }
      }
    }
  }
});