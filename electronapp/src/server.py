from flask import Flask, jsonify, request
from datetime import datetime
import time

app = Flask(__name__)

@app.route('/set-notification', methods=['POST'])
def set_notification():
    data = request.json
    notification_time = data.get('notification_time')

    if not notification_time:
        return jsonify({'error': 'Notification time not provided'}), 400

    try:
        notification_time = int(notification_time)
        current_time = int(time.time() * 1000)
        time_diff_ms = notification_time - current_time

        if time_diff_ms <= 0:
            return jsonify({'error': 'Invalid notification time'}), 400

        time.sleep(time_diff_ms / 1000)
        # ここで通知を実行する処理を追加する (例: ログ出力、データベースに保存、通知APIの呼び出しなど)
        app.logger.info('Notification triggered!')

        return jsonify({'message': 'Notification triggered successfully'})
    
    except ValueError:
        return jsonify({'error': 'Invalid notification time format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
