from strands import Agent, tool
from strands.models.gemini import GeminiModel
from .llm_model import Model
import json
import os
from dotenv import load_dotenv
load_dotenv()

from rich.traceback import install
from rich.console import Console
console = Console()
install(show_locals=True)

class ItineraryAgent(Model):
    def __init__(self, temperature):
        super().__init__(temperature)
        self.__import_prompt__()
    
    def __import_prompt__(self):
        try:
            with open("./system_prompts/agent-itinerary-prompt.txt","r") as f:
                self.__sys_prompt = f.read()

            with open("./user_profile.json","r") as f:
                user_profile = json.load(f)
                self.__user_profile = {
                    'behavioral_style':user_profile['behavioral_style'],
                    'constraints':user_profile['constraints']
                }
        
        except Exception as e:
            console.print(f"[red](agent_itinerary.py) | Error importing prompt & user profile:[/red]: {e}")
            return f"(agent_itinerary.py) | Error importing prompt & user profile: {str(e)}"
    
    def __initialize_agent(self):
        try:
            self.__sys_prompt = self.__sys_prompt.format(
                user_profile=str(self.__user_profile),
            )
            # console.print(f"[cyan](agent.py) | SYSETM PROMPT:[/cyan]: {self.__sys_prompt}")
            self.__agent = Agent(
                model=self.model,
                system_prompt=self.__sys_prompt
            )

        except Exception as e:
            console.print(f"[red](agent_itinerary.py) | Error initialize agent:[/red]: {e}")
            return f"(agent_itinerary.py) | Error initialize agent: {str(e)}"
    
    @tool
    def call_itinerary_agent(self, vacation_period:int, places:list[dict], hotels:dict={}):
        """
        Tool: call_itinerary_agent
        Description: Use this tool for run agent that help you make itinerary.
        Args:
            vacation_period (int): user vacation period (days)
            hotels (dict): dict of choosen hotel data, contain hotel attribute
            places (list[dict]): list of fetched places data, contain name and category
        Return:
            Itenerary in JSON format
        """
        try:
            console.print(f"[cyan](agent_itinerary.py) | Vaction periode:[/cyan]: {vacation_period}")
            console.print(f"[cyan](agent_itinerary.py) | Places:[/cyan]: {places}")
            console.print(f"[cyan](agent_itinerary.py) | Hotels:[/cyan]: {hotels}")
            
            self.__initialize_agent()
            agent = self.__agent(f"""
            vacation_periode: {vacation_period}
            hotels: {hotels}
            places: {places}
            """)
            return agent
            
        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(f"[red](agent_itinerary.py) | Error processing your prompt:[/red]: {e}")
            return f"(agent_itinerary.py) | Error processing your prompt: {str(e)}"
