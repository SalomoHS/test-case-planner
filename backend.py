from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from supabaseClient import supabase_client
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/plans-bookings")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket connection attempt...")
    await websocket.accept()
    print("WebSocket connection accepted!")
    
    try:
        try:
            plans_response = supabase_client.schema('planner').table('plans').select('*').execute()
            bookings_response = supabase_client.schema('planner').table('bookings').select('*').execute()
            
            response_data = {
                "plans": plans_response.data if plans_response.data else [],
                "bookings": bookings_response.data if bookings_response.data else []
            }
            print(f"Sending data: {len(response_data['plans'])} plans, {len(response_data['bookings'])} bookings")
            await websocket.send_text(json.dumps(response_data))
        except Exception as e:
            print(f"Error fetching initial data: {e}")
            await websocket.send_text(json.dumps({"plans": [], "bookings": [], "error": str(e)}))
        
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            
            try:
                plans_response = supabase_client.schema('planner').table('plans').select('*').execute()
                bookings_response = supabase_client.schema('planner').table('bookings').select('*').execute()
                
                response_data = {
                    "plans": plans_response.data if plans_response.data else [],
                    "bookings": bookings_response.data if bookings_response.data else []
                }
                print(f"Sending data: {len(response_data['plans'])} plans, {len(response_data['bookings'])} bookings")
                await websocket.send_text(json.dumps(response_data))
            except Exception as e:
                print(f"Error fetching data: {e}")
                await websocket.send_text(json.dumps({"plans": [], "bookings": [], "error": str(e)}))
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
