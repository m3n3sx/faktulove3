#!/usr/bin/env node

/**
 * Simple build script for the OCR Upload React app
 * Creates a standalone bundle without complex dependencies
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Configuration
const config = {
  entry: path.resolve(__dirname, '../src/apps/SimpleUploadApp.js'),
  output: {
    path: path.resolve(__dirname, '../../static/js'),
    filename: 'upload-app.bundle.js',
    library: 'UploadApp',
    libraryTarget: 'window'
  },
  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM'
  }
};

console.log('Building Simple OCR Upload App...');

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
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
  optimization: {
    minimize: true
  }
};
`;

  // Write temporary webpack config
  const tempConfigPath = path.resolve(__dirname, '../webpack.simple.config.js');
  fs.writeFileSync(tempConfigPath, webpackConfig);

  // Run webpack
  console.log('Running webpack build...');
  execSync(`npx webpack --config ${tempConfigPath}`, { 
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..')
  });

  // Clean up temp config
  fs.unlinkSync(tempConfigPath);

  console.log('✅ Simple upload app built successfully!');
  console.log(`📦 Bundle created at: ${config.output.path}/${config.output.filename}`);

} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}