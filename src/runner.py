import nest_asyncio
import uvicorn
from pyngrok import ngrok
import threading


ngrok.set_auth_token("3KPb3edeSX6N9wqiZYOmaGZjNBU_2KX7q6vBwGj4QqQ1UZGJt")

# Tunnel local port 8000 to public internet
ngrok_tunnel = ngrok.connect(8000)
print("=" * 60)
print("NGROK PUBLIC URL:", ngrok_tunnel.public_url)
print("=" * 60)
print("Copy the URL above and paste it into the Streamlit sidebar field.")

nest_asyncio.apply()

def run_backend():
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=False)

# Start backend thread
threading.Thread(target=run_backend, daemon=True).start()