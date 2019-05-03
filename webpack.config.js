import path from 'path';

module.exports = {
  entry: {
    frontend: './jsx/frontend.jsx',
    hud: './jsx/hud.jsx',
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'python', 'pokeserver', 'static', 'dist'),
  },
  mode: process.env.NODE_ENV || 'development',
  watch: (process.env.NODE_ENV || 'development') == 'development',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.(jpg|jpeg|png|woff|woff2|eot|ttf|svg)$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 8192,
              publicPath: 'static/dist'
            },
          },
        ],
      }
    ],
  }
};
