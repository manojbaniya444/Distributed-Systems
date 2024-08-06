import requests
from flask import jsonify, Response, Flask, request
import sys
import time

class LogicalClock:
    def __init__(self):
        self.time = 0
        
    def tick(self):
        self.time += 1
        
    def update(self, received_time):
        self.time = max(self.time, received_time) + 1
        
    def get_time(self):
        return self.time
    
        
class Process:
    def __init__(self, process_id, port):
        self.process_id = process_id
        self.port = port
        self.clock = LogicalClock()
        self.app = Flask(__name__)
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route("/internal_event", methods=["POST"])
        def internal_event():
            self.clock.tick()
            return jsonify({
                "process_id": self.process_id,
                "event": "internal",
                "time": self.clock.get_time()
            })
            
        @self.app.route("/send_message", methods=["POST"])
        def send_message():
            data = request.json
            receiver_url = data["receiver_url"]
            self.clock.tick()
            timestamp = self.clock.get_time()
            response = requests.post(receiver_url, json={
                "timestamp": timestamp
            })
            
            return jsonify({
                "process_id": self.process_id,
                "event": "send_message",
                "time": timestamp,
                "receiver_response": response.json()
            })
            
        @self.app.route("/receive_message", methods=[])
        def receive_message():
            data = request.json
            received_time = data["time"]
            