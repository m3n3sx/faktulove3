
const path = require('path');

module.exports = {
  mode: 'production',
  entry: '/home/ooxo/faktulove_now/frontend/src/apps/UploadApp.js',
  output: {
    path: '/home/ooxo/faktulove_now/static/js',
    filename: 'upload-app.bundle.js',
    library: 'UploadApp',
    libraryTarget: 'window'
  },
  externals: {
  "react": "React",
  "react-dom": "ReactDOM",
  "axios": "axios"
},
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
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
        test: /\.css$/,
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
