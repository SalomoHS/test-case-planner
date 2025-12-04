from strands import Agent, tool
from strands.models.gemini import GeminiModel
from .llm_model import Model
from .agent_place import PlaceAgent
from .agent_hotel import HotelAgent
from .agent_itinerary import ItineraryAgent
from supabaseClient import supabase_client

import uuid
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

from rich.traceback import install
from rich.console import Console
console = Console()
install(show_locals=True)


class StrandsAgent(Model):
    def __init__(self):
        super().__init__()
        self.__import_prompt__()

        self.__hotel_agent = HotelAgent(temperature = 0.7)
        self.__place_agent = PlaceAgent(temperature = 0.7)
        self.__itenerary_agent = ItineraryAgent(temperature = 0.7)

    def __custom_callback_handler(self, **kwargs):
        if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            console.print(f"\n[yellow]CALLING TOOL: {kwargs['current_tool_use']['name']}[/yellow]")
    
    def __import_prompt__(self):
        try:
            with open("./system_prompts/root-agent-prompt.txt","r") as f:
                self.__sys_prompt = f.read()
            
            with open("./user_profile.json","r") as f:
                self.__user_profile = json.load(f)

        except Exception as e:
            console.print(f"[red](root_agent.py) | Error importing prompt & user profile:[/red]: {e}")
            return f"(root_agent.py) | Error importing prompt & user profile: {str(e)}"

    def __initialize_agent(self):
        try:
            self.__agent = Agent(
                model=self.model,
                tools=[
                    self.__hotel_agent.call_hotel_agent_with_hitl, 
                    self.__place_agent.call_place_agent,
                    self.__itenerary_agent.call_itinerary_agent
                ],
                system_prompt=self.__sys_prompt,
                callback_handler=self.__custom_callback_handler
            )

        except Exception as e:
            console.print(f"[red](root_agent.py) | Error initialize agent:[/red]: {e}")
            return f"(root_agent.py) | Error initialize agent: {str(e)}"
  
    def call_agent(self, prompt):
        try:
            self.__initialize_agent()
            agent = self.__agent(prompt)
            return agent

        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(f"[red](root_agent.py) | Error processing your prompt:[/red]: {e}")
            return f"(root_agent.py) | Error processing your prompt: {str(e)}"
