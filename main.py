import threading
import subprocess
import time

def run_max():
    subprocess.run(["python", "max_code.py"])

def run_tg():
    subprocess.run(["python", "tg_code.py"])

if __name__ == "__main__":
    print("🚀 Запуск объединенного сервера ботов...")
    
    thread_max = threading.Thread(target=run_max)
    thread_max.start()
    
    thread_tg = threading.Thread(target=run_tg)
    thread_tg.start()
    
    while True:
        time.sleep(1)
