from agents.root_agent import StrandsAgent
from supabaseClient import supabase_client

import config
import uuid
import json
import os
from dotenv import load_dotenv
load_dotenv()

from rich.traceback import install
from rich.console import Console
console = Console()
install(show_locals=True)

def parse_json(response_text):
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0]
    elif '```' in response_text:
        response_text = response_text.split('```')[1].split('```')[0]

    data = json.loads(response_text.strip())
    return data

def insert_plan_to_planner(data):
    plan_id = "PLAN-" + str(uuid.uuid1()).split("-")[0]
    data["plan_id"] = plan_id

    if data['booking_id'] == "":
        data["booking_id"] = None

    try:
        res = supabase_client.schema('planner').table("plans").insert([data]).execute()
        console.print("[green]Planning Success[/green]")
        return res

    except Exception as e:
        console.print(f"[red]Planning Failed: {e}[/red]")
        return 

if __name__ =='__main__':
    try:
        agent = StrandsAgent()
        res = agent.call_agent(config.prompt)

        response_text = str(res.message['content'][0]['text'])
        console.print(f"[cyan](main.py) | itenerary:[/cyan]: {response_text}")
            
        data = parse_json(response_text.strip())
        insert_plan_to_planner(data)

    except Exception as e:
        console.print_exception(show_locals=True)
        console.print(f"[red](main.py) | Error running program:[/red]: {e}")
        raise
