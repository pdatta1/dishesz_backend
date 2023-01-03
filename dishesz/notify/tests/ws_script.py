

import websocket 
import requests 



data = { 
    'username': 'twitteringc', 
    'password': 'aici8xjIWNTL'
}
req = requests.post('http://127.0.0.1:8000/users/access/', data)

response_data = req.json()

access_token = response_data['access']

ws = websocket.WebSocket() 

websocket.enableTrace(True)
ws.connect(f'ws://127.0.0.1:8000/ws/notify/?token={access_token}')
ws.send("Hello, Server")


print(ws.recv())

ws.close()