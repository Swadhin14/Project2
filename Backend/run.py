import uvicorn
import webbrowser
import threading
import time
import os

def open_browser():
    # Only open browser on initial run, not on every auto-reload
    if os.environ.get("RUN_MAIN") != "true":
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)