#!/usr/bin/env node

/**
 * Build script for the OCR Upload React app
 * Creates a standalone bundle that can be included in Django templates
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Configuration
const config = {
  entry: path.resolve(__dirname, '../src/apps/UploadApp.js'),
  output: {
    path: path.resolve(__dirname, '../../static/js'),
    filename: 'upload-app.bundle.js',
    library: 'UploadApp',
    libraryTarget: 'window'
  },
  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM',
    'axios': 'axios'
  }
};

console.log('Building OCR Upload App...');

try {
  // Create webpack config
  const webpackConfig = `
const path = require('path');

module.exports = {
  mode: 'production',
  entry: '${config.entry}',
  output: {
    path: '${config.output.path}',
    filename: '${config.output.filename}',
    library: '${config.output.library}',
    libraryTarget: '${config.output.libraryTarget}'
  },
  externals: ${JSON.stringify(config.externals, null, 2)},
  module: {
    rules: [
      {
        test: /\\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', { targets: 'defaults' }],
              ['@babel/preset-react', { runtime: 'automatic' }]
            ]
          }
        }
      },
      {
        test: /\\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, '../src')
    }
  },
  optimization: {
    minimize: true
  }
};
`;

  // Write temporary webpack config
  const tempConfigPath = path.resolve(__dirname, '../webpack.upload.config.js');
  fs.writeFileSync(tempConfigPath, webpackConfig);

  // Run webpack
  console.log('Running webpack build...');
  execSync(`npx webpack --config ${tempConfigPath}`, { 
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..')
  });

  // Clean up temp config
  fs.unlinkSync(tempConfigPath);

  console.log('✅ Upload app built successfully!');
  console.log(`📦 Bundle created at: ${config.output.path}/${config.output.filename}`);

} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}