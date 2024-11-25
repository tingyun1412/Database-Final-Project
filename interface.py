from flask import Flask, send_file, jsonify
from flask_cors import CORS  # 用于解决跨域问题
import os

app = Flask(__name__)
CORS(app)  # 允许跨域访问（如果前后端分离运行）

@app.route('/api/songlist', methods=['GET'])
def get_songlist():
    file_path = os.path.join(os.getcwd(), 'song_data.csv')  # 确保路径正确
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
