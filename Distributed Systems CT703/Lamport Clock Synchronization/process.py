from flask import Flask, request, jsonify
import requests
import sys

class LogicalClock:
    def __init__(self):
        self.time = 0
    
    def tick(self):
        """Increment the logical clock for an internal event."""
        self.time += 1

    def update(self, received_time):
        """Update the logical clock with a received timestamp for a message event."""
        self.time = max(self.time, received_time) + 1

    def get_time(self):
        """Get the current logical time."""
        return self.time

class Process:
    def __init__(self, process_id, port):
        self.process_id = process_id
        self.port = port
        self.clock = LogicalClock()
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/internal_event', methods=['POST'])
        def internal_event():
            self.clock.tick()
            return jsonify({
                'process_id': self.process_id,
                'event': 'internal',
                'time': self.clock.get_time()
            })

        @self.app.route('/send_message', methods=['POST'])
        def send_message():
            data = request.json
            receiver_url = data['receiver_url']
            self.clock.tick()
            timestamp = self.clock.get_time()
            response = requests.post(receiver_url, json={'timestamp': timestamp})
            return jsonify({
                'process_id': self.process_id,
                'event': 'send_message',
                'time': timestamp,
                'receiver_response': response.json()
            })

        @self.app.route('/receive_message', methods=['POST'])
        def receive_message():
            data = request.json
            received_time = data['timestamp']
            self.clock.update(received_time)
            return jsonify({
                'process_id': self.process_id,
                'event': 'receive_message',
                'received_time': received_time,
                'time': self.clock.get_time()
            })
    
    def run(self):
        self.app.run(port=self.port)

if __name__ == '__main__':
    process_id = sys.argv[1]
    port = int(sys.argv[2])
    process = Process(process_id, port)
    process.run()

# Start Process 1:
# python process.py 1 5001

# Start Process 2:
# python process.py 2 5002

# Start Process 3:
# python process.py 3 5003

# Internal Event in Process 1:
# curl -X POST http://localhost:5001/internal_event

# Process 1 Sends Message to Process 2:
# curl -X POST http://localhost:5001/send_message -H "Content-Type: application/json" -d '{"receiver_url": "http://localhost:5002/receive_message"}'


