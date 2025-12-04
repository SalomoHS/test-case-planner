from strands import Agent, tool
from strands.models.gemini import GeminiModel
from .llm_model import Model
from supabaseClient import supabase_client

import json
import requests
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

from rich.traceback import install
from rich.console import Console
console = Console()
install(show_locals=True)

class HotelAgent(Model):
    def __init__(self, temperature):
        super().__init__(temperature)
        self.__import_prompt__()
    
    def __import_prompt__(self):
        try:
            with open("./system_prompts/agent-hotel-prompt.txt","r") as f:
                self.__sys_prompt = f.read()

            with open("./user_profile.json","r") as f:
                user_profile = json.load(f)

                if 'payment_method' in user_profile:
                    self.__user_profile = {
                        'email':user_profile['email'],
                        'hotel_preferences':user_profile['preferences']['hotel'],
                        'payment_method':user_profile['payment_method'],
                    }
                else:
                    self.__user_profile = {
                        'hotel_preferences':user_profile['preferences']['hotel'],
                    }
        
        except Exception as e:
            console.print(f"[red](agent_hotel.py) | Error importing prompt & user profile:[/red]: {e}")
            return f"(agent_hotel.py) | Error importing prompt & user profile: {str(e)}"
    
    def __initialize_agent(self):
        try:
            # console.print(f"[cyan](agent.py) | SYSETM PROMPT:[/cyan]: {self.__sys_prompt}")
            self.__sys_prompt = self.__sys_prompt.format(
                user_profile=str(self.__user_profile),
            )

            self.__agent = Agent(
                model=self.model,
                tools=[self.__pick_hotel],
                system_prompt=self.__sys_prompt
            )

        except Exception as e:
            console.print(f"[red](agent_hotel.py) | Error initialize agent:[/red]: {e}")
            return f"(agent_hotel.py) | Error initialize agent: {str(e)}"
    
    def __send_invoice(self, data):
        try:
            url = os.getenv('N8N_ENDPOINT')
            payload = json.dumps({
                "email": self.__user_profile['email'],
                "hotel_name": data['name'],
                "hotel_price": data['price_per_night'],
                "hotel_checkin": data['check-in']
            })
            headers = {
                'Content-Type': 'application/json'
            }
        
            response = requests.request("POST", url, headers=headers, data=payload)
            return response

        except Exception as e:
            console.print(f"[red](agent_hotel.py) | Error send invoice :[/red]: {e}")
            return {'message': 'error when send invoice', 'error':e}


    def __book_hotel(self, data):
        curr_balance = self.__user_profile['payment_method']['balance']
        if curr_balance < data['price_per_night']:
            return {'booked_hotel':'', 'message':"Insufficient Balance: booking hotel failed"}
        
        book_id = "BOOK-" + str(uuid.uuid1()).split("-")[0]
        data["booking_id"] = book_id
        
        try:
            supabase_client.schema('planner').table("bookings").insert([data]).execute()       
            self.__send_invoice(data)
            
            return {'booked_hotel':data, 'message':"booking hotel success"}
        except Exception as e:
            return {'booked_hotel':'', 'message': f"booking hotel failed: {e}"}

    @tool
    def call_hotel_agent_with_hitl(self, hotel_criteria, check_in:str, check_out:str):
        """
        Tool: __call_hotel_agent_with_hitl
        Description: Use this tool for run agent that help you get all hotel data.
        Args:
            hotel_criteria (str): user hotel criteria (city,rating,name,etc)
            check_in (str): date user hotel check-in (ex, 2 December 2025)
            check-out (str): date user hotel check-out (ex, 3 December 2025)
        Return:
            Dict of choosen one hotel, contain hotel attributes
        """
        console.print(f"[cyan](agent_hotel.py) | HOTEL Check in:[/cyan]: {check_in}")
        console.print(f"[cyan](agent_hotel.py) | HOTEL Check out:[/cyan]: {check_out}")
        console.print(f"[yellow](Human-in-the-loop) | Do you want to search for hotels?[/yellow]")
        
        user_input = input("Answer (y/n): ")
        
        if user_input.lower() != "y":
            console.print("[red]Hotel search cancelled by user.[/red]")
            return {"cancelled": True, "message": "Hotel search cancelled by user, skip '__call_hotel_agent_tool' tool"}
        
        try:
            console.print("[green]Proceeding with hotel search...[/green]")
            response_text = self.__call_hotel_agent(hotel_criteria, check_in, check_out)
            response_text = str(response_text)

            hotel_json = ""
            if '```json' in response_text:

                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0]
                
                # Handle escaped characters and clean up the JSON string
                response_text = response_text.replace('\\n', '\n').replace('\\"', '"').strip()
            
            hotel_json = json.loads(response_text)
              
            if "payment_method" in self.__user_profile:

                console.print(f"[cyan](agent_hotel.py) | HOTEL JSON:[/cyan]: {hotel_json}")        
                console.print(f"[yellow](Human-in-the-loop) | Do you want book these hotels?[/yellow]")
                user_input = input(f"Answer (y/n): ")
                
                if user_input.lower() != "y":
                    console.print("[red]Hotel not booked.[/red]")
                    return {"ask_user": False, 'message':'hotel is found, next to the next step', 'data': hotel_json}
                
                book_hotel = self.__book_hotel(hotel_json)

                console.print("[green]Hotel booked.[/green]")
                return book_hotel['booked_hotel']
            
            console.print("[red]User not provide payment information.[/red]")
            return {"ask_user": False, 'message':'hotel is found, next to the next step', 'data': hotel_json}
        
        
        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(f"[red](agent_hotel.py) | Error finding hotels:[/red]: {e}")
            return {'message': 'error when finding hotels','error':e}

    @tool
    def __pick_hotel(self, 
                    city:str, rating:int, swimming_pool:bool, 
                    restaurant:bool, wifi:bool, parking:bool, gym:bool, 
                    max_price_per_night:int,name:str ="" ):
        """
        Tool: __pick_hotel
        Description: Use this tools for get hotels data based on user profile.
        Args:
            name (str): hotel name (optional)
            city (str): hotel location
            rating (int): hotel rating
            swimming_pool (bool): hotel has swimming pool?
            restaurant (bool): hotel has restaurant?
            wifi (bool): hotel has wifi?
            parking (bool): hotel has parking?
            gym (bool): hotel has gym?
            max_price_per_night (int): maximum hotel price per night preferences
        Return
            Dict of hotel that contain hotel attributes matched with params 
        """
        try:
            console.print(f"[cyan](agent_hotel.py) | PARAMS - name:[/cyan] {name}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - city:[/cyan] {city}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - rating:[/cyan] {rating}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - swimming_pool:[/cyan] {swimming_pool}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - restaurant:[/cyan] {restaurant}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - wifi:[/cyan] {wifi}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - parking:[/cyan] {parking}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - gym:[/cyan] {gym}")
            console.print(f"[cyan](agent_hotel.py) | PARAMS - max_price_per_night:[/cyan] {max_price_per_night}")
            
            fetch = supabase_client.schema('travel')\
                    .table("hotels")\
                    .select("*")\
                    .eq("city",city.capitalize())\
                    .gte("rating",rating)\
                    .eq("swimming_pool",swimming_pool)\
                    .eq("restaurant",restaurant)\
                    .eq("wifi",wifi)\
                    .eq("parking",parking)\
                    .eq("gym",gym)\
                    .lte("price_per_night",max_price_per_night)\
                    .limit(1)\
                    .execute()

            console.print(f"[cyan](agent_hotel.py) | Hotel found:[/cyan]: {fetch.data}")
            return {"ask_user": False, 'data': fetch.data}

        except Exception as e:
            console.print(f"[red](agent_hotel.py) | Error fetch hotel data:[/red]: {e}")
            return f"(agent_hotel.py) | Error fetch hotel data: {str(e)}"

    @tool
    def __call_hotel_agent(self, hotel_criteria:str, check_in:str, check_out:str):
        """
        Tool: call_hotel_agent
        Description: Use this tool for run agent that help you pick hotel data.
        Args:
            hotel_criteria (str): user hotel criteria (city,rating,name,etc)
            check_in (str): date user hotel check-in (ex, 2 December 2025)
            check-out (str): date user hotel check-out (ex, 3 December 2025)
        Return:
            Dict of choosen one hotel, contain hotel attributes
        """
        try:
            self.__initialize_agent()
            agent = self.__agent(f"""
            {{
                'hotel_criteria':{hotel_criteria},
                'check-in':{check_in},
                'check-out':{check_out}
            }}
            """)
            return agent
            
        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(f"[red](agent_hotel.py) | Error processing your prompt:[/red]: {e}")
            return f"(agent_hotel.py) | Error processing your prompt: {str(e)}"
