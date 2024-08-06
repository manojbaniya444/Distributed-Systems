from flask import Flask, request, jsonify
import threading 
import requests
import time

app = Flask(__name__)

# configurations

# unique id for this server
server_id = 1 
total_servers = 3
servers = {
    1: "http://localhost:9001",
    2: "http://localhost:9002",
    3: "http://localhost:9003",
}

status = {
    "alive": True,
    "coordinator": False
}

coordinator_id = None
heartbeat_interval = 3 # in seconds
heartbeat_timeout = 6 # in seconds

# Lock for thread safety
lock = threading.Lock()

# API route
@app.route("/heartbeat", methods = ["POST"])
def heartbeat():
    global coordinator_id
    data = request.json
    print(f"Received heartbeat from coordinator {data["coordinator_id"]}")
    coordinator_id = data["coordinator_id"]
    with lock:
        if data["coordinator_id"]  == coordinator_id:
            status["last_heartbeat"] = time.time()
            
    return jsonify({
        "message": "Heartbeat received."
    }), 200
    
@app.route("/coordinator", methods = ["POST"])
def coordinator():
    global coordinator_id
    data = request.json
    print(f"Received coordinator message from data {data["coordinator_id"]}")
    with lock:
        coordinator_id = data["coordinator_id"]
        status["coordinator"] = False
    
    return jsonify({
        "message": "Coordinator Updated"
    }), 200
    
@app.route("/start_election", methods = ["POST"])
def start_election():
    data = request.json
    candidate_id = data["candidate_id"]
    print(f"Received election request from {data["candidate_id"]}")
    with lock:
        if candidate_id < server_id:
            return jsonify({
                "message": "I have a higher id."
            }), 200
        return jsonify({
            "message": "OK"
        }), 200
        
def send_heartbeat():
    global coordinator_id
    while True:
        time.sleep(heartbeat_interval)
        with lock:
            if status["coordinator"]:
                print(f"server id: {server_id} is sending heartbeat.")
                for sid, url in servers.items():
                    if sid != server_id:
                        try:
                            requests.post(f"{url}/heartbeat", json={"coordinator_id": coordinator_id})
                        except requests.ConnectionError:
                            print(f"Error sending heartbeat to server {sid}")
                            
def monitor_heartbeat():
    global coordinator_id
    while True:
        time.sleep(heartbeat_timeout)
        with lock:
            if coordinator_id != server_id and time.time() - status.get("last_heartbeat", 0) > heartbeat_timeout:
                print(f"No heartbeat received from coordinator {coordinator_id}. Starting election now.")
                coordinator_id = None
                start_election_process()
                
            elif coordinator_id < server_id:
                print(f"Server {server_id} which is higher than coordinator {coordinator_id} is active.")
                coordinator_id = None
                start_election_process()
                
def start_election_process():
    global coordinator_id
    coordinator_id = None
    status["coordinator"] = False
    
    higher_id_exists = False
    for sid, url in servers.items():
        if sid > server_id:
            try:
                response = requests.post(f"{url}/start_election", json={"candidate_id": server_id})
                if response.json()["message"] == "I have a higher id.":
                    print(f"Server {sid} has a higher id than {server_id}")
                    higher_id_exists = True
            except requests.ConnectionError:
                print(f"Fail to contact server {sid} for election.")
                pass
            
    if not higher_id_exists:
        coordinator_id = server_id
        status["coordinator"] = True
        print(f"Server {server_id} is the new coordinator.")
        
        for sid,url in servers.items():
            if sid != server_id:
                try:
                    response = requests.post(url + "/coordinator", json = ({"coordinator_id": coordinator_id}))
                except requests.ConnectionError:
                    pass
                

# start the main
if __name__ == "__main__":
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=monitor_heartbeat, daemon=True).start()
    
    app.run(
        port = 9000 + server_id
    )