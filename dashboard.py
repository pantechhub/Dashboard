from flask import Flask, render_template_string, request, send_from_directory
import psutil
import os

app = Flask(__name__)

# ✅ Customize your app shortcuts here
APPS = {
    "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "VS Code": r"C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "Notepad": "notepad.exe"
}

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>My PC Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; background: #121212; color: #eee; text-align: center; }
    .card { background: #1e1e1e; padding: 20px; margin: 20px; border-radius: 12px; box-shadow: 0 0 10px #000; }
    button { padding: 10px 20px; margin: 10px; border: none; border-radius: 8px; background: #4CAF50; color: white; cursor: pointer; }
    button:hover { background: #45a049; }
    a { color: #4CAF50; }
  </style>
</head>
<body>
  <h1>📊 PC Dashboard</h1>
  
  <div class="card">
    <h2>System Status</h2>
    <p><b>CPU Usage:</b> {{cpu}}%</p>
    <p><b>Memory Usage:</b> {{memory}}%</p>
    <p><b>Disk Usage:</b> {{disk}}%</p>
    <p><b>Battery:</b> {{battery}}%</p>
    {% if alert %}<p style="color:red;"><b>⚠️ ALERT:</b> {{alert}}</p>{% endif %}
  </div>
  
  <div class="card">
    <h2>Quick Actions</h2>
    <form action="/shutdown"><button>Shutdown</button></form>
    <form action="/restart"><button>Restart</button></form>
    <form action="/taskbar"><button>Toggle Taskbar Auto-Hide</button></form>
  </div>

  <div class="card">
    <h2>App Launcher</h2>
    {% for name in apps %}
      <form action="/launch/{{name}}"><button>{{name}}</button></form>
    {% endfor %}
  </div>

  <div class="card">
    <h2>Process Monitor</h2>
    <ul>
    {% for p in processes %}
      <li>{{p['pid']}} - {{p['name']}} 
        <a href="/kill/{{p['pid']}}">❌ Kill</a>
      </li>
    {% endfor %}
    </ul>
  </div>

  <div class="card">
    <h2>File Explorer</h2>
    <form method="get" action="/files">
      <input type="text" name="path" placeholder="C:\\" value="{{cwd}}" size="40">
      <button>Browse</button>
    </form>
    <ul>
    {% for f in files %}
      <li><a href="/download?path={{cwd}}&file={{f}}">{{f}}</a></li>
    {% endfor %}
    </ul>
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    battery = psutil.sensors_battery()
    alert = None
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    if cpu > 80:
        alert = f"High CPU usage ({cpu}%)"
    elif mem > 80:
        alert = f"High Memory usage ({mem}%)"

    processes = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            processes.append(p.info)
        except: 
            pass

    files = []
    cwd = request.args.get("path", "C:\\")
    if os.path.exists(cwd):
        try:
            files = os.listdir(cwd)
        except PermissionError:
            files = ["Access Denied"]

    return render_template_string(
        HTML,
        cpu=cpu,
        memory=mem,
        disk=psutil.disk_usage('/').percent,
        battery=battery.percent if battery else "N/A",
        alert=alert,
        apps=APPS.keys(),
        processes=processes[:20],  # show top 20
        files=files,
        cwd=cwd
    )

@app.route("/shutdown")
def shutdown():
    os.system("shutdown /s /t 1")
    return "Shutting down..."

@app.route("/restart")
def restart():
    os.system("shutdown /r /t 1")
    return "Restarting..."

@app.route("/taskbar")
def taskbar_toggle():
    os.system('powershell -ExecutionPolicy Bypass -File "C:\\Users\\YourName\\Desktop\\ToggleTaskbar.ps1"')
    return "Toggled taskbar auto-hide!"

@app.route("/launch/<app>")
def launch(app):
    if app in APPS:
        os.startfile(APPS[app])
        return f"Launched {app}"
    return "App not found"

@app.route("/kill/<int:pid>")
def kill(pid):
    try:
        psutil.Process(pid).terminate()
        return f"Killed process {pid}"
    except Exception as e:
        return str(e)

@app.route("/files")
def files():
    return home()

@app.route("/download")
def download():
    path = request.args.get("path")
    file = request.args.get("file")
    return send_from_directory(path, file, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
