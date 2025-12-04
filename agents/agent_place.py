from strands import Agent, tool
from strands.models.gemini import GeminiModel
from .llm_model import Model
from supabaseClient import supabase_client

import json
import os
from dotenv import load_dotenv
load_dotenv()

from rich.traceback import install
from rich.console import Console
console = Console()
install(show_locals=True)

class PlaceAgent(Model):
    def __init__(self, temperature):
        super().__init__(temperature)
        self.__import_prompt__()
    
    def __import_prompt__(self):
        try:
            with open("./system_prompts/agent-place-prompt.txt","r") as f:
                self.__sys_prompt = f.read()

            with open("./user_profile.json","r") as f:
                user_profile = json.load(f)
                self.__user_profile = {
                    'hotel_preferences':user_profile['preferences']['attractions'],
                    'behavioral_style':user_profile['behavioral_style'],
                    'constraint':user_profile['constraints']
                }
            
        except Exception as e:
            console.print(f"[red](agent_place.py) | Error importing prompt & user profile:[/red]: {e}")
            return f"(agent_place.py) | Error importing prompt & user profile: {str(e)}"
    
    def __initialize_agent(self):
        try:
            self.__sys_prompt = self.__sys_prompt.format(
                user_profile=str(self.__user_profile),
            )

            self.__agent = Agent(
                model=self.model,
                tools=[self.__find_places],
                system_prompt=self.__sys_prompt
            )

        except Exception as e:
            console.print(f"[red](agent_place.py) | Error initialize agent:[/red]: {e}")
            return f"(agent_place.py) | Error initialize agent: {str(e)}"

    @tool
    def __find_places(self, 
                    city:str, 
                    max_ticket_price:int,
                    category:list[str],
                    name:str =""):
        """
        Tool: __find_places
        Description: Use this tools for fetching places data based on user profile.
        Args:
            name (str): place name (optional)
            city (str): place location (capitalize)
            category (str): List contain: Beach|Cultural|Family|Historical|Landmark|Museum|Nature|Shopping|Theme Park
            max_ticket_price (int): maximum ticket price user preferences 
        Return
            List all places name and description
        """
        try:
            console.print(f"[cyan](agent_place.py) | PARAMS - name:[/cyan] {name}")
            console.print(f"[cyan](agent_place.py) | PARAMS - city:[/cyan] {city}")
            console.print(f"[cyan](agent_place.py) | PARAMS - category:[/cyan] {category}")
            
            fetch = supabase_client.schema('travel')\
                    .table("places")\
                    .select("name, category")\
                    .eq("city",city.capitalize())\
                    .in_("category",category)\
                    .lte("ticket_price", max_ticket_price)\
                    .limit(5)\
                    .execute()

            console.print(f"[cyan](agent.py) | Place List:[/cyan]: {fetch.data}")    
            return fetch.data

        except Exception as e:
            console.print(f"[red](agent.py) | Error fetch place data:[/red]: {e}")
            return f"(agent.py) | Error fetch place data: {str(e)}"

    @tool
    def call_place_agent(self, place_description):
        """
        Tool: call_place_agent
        Description: Use this tool for run agent that help you fetch all place data.
        Args:
            place_description: description of place
        Return:
            Dictionary of all choosen places, contain name and category
        """
        try:
            self.__initialize_agent()
            agent = self.__agent(place_description)
            return agent
            
        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(f"[red](agent_place.py) | Error processing your prompt:[/red]: {e}")
            return f"(agent_place.py) | Error processing your prompt: {str(e)}"
