from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# 각 아두이노의 최근 명령을 저장하는 딕셔너리
command_cache = {
    "arduino1": {"target": "arduino1", "cmd": None},
    "arduino2": {"target": "arduino2", "cmd": None}
}

@app.route('/')
def index():
    """웹 페이지에서 현재 명령을 확인하는 HTML 페이지 렌더링"""
    return render_template("LedControl.html", command_cache=command_cache)

@app.route('/command', methods=['GET'])
def command():
    """
    아두이노 또는 앱 인벤터에서 현재 명령을 가져가는 엔드포인트.
    아두이노가 한 번 요청하면 이후 값이 None으로 초기화됨.
    예: http://<server-ip>:5010/command?target=arduino1
    """
    target = request.args.get('target')
    
    if target not in command_cache:
        return jsonify({"status": "error", "message": "Invalid target"}), 400

    response = jsonify(command_cache[target])

    # **아두이노가 가져간 후 명령 초기화 (중복 방지)**
    command_cache[target]["cmd"] = None

    return response

@app.route('/set_command', methods=['GET'])
def set_command():
    """
    웹에서 명령을 설정하는 엔드포인트.
    예: http://<server-ip>:5010/set_command?target=arduino1&cmd=LED_ON
    """
    target = request.args.get('target')
    cmd = request.args.get('cmd')

    if target not in command_cache:
        return jsonify({"status": "error", "message": "Invalid target"}), 400

    # 웹 명령을 `_WEB` 접미어 추가하여 처리
    if cmd in ["LED_ON", "LED_OFF", "AUTO_MODE"]:
        cmd = f"{cmd}_WEB"

    # 기존 명령과 동일하면 다시 보내지 않음 (중복 방지)
    if command_cache[target]["cmd"] == cmd:
        return jsonify({"status": "no_change", "command": cmd})

    # 새로운 명령 저장
    command_cache[target]["cmd"] = cmd
    return jsonify({"status": "ok", "command": cmd})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)