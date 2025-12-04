from strands.models.gemini import GeminiModel

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="./agents/.env")

from rich.traceback import install
from rich.console import Console
console = Console()
install(show_locals=True)

class Model:
    def __init__(self, temperature = 0.7):
        try:
            self.model = GeminiModel(
                client_args={
                    "api_key": os.getenv('GEMINI_API_KEY'),
                },
                model_id="gemini-2.5-flash", 
                params={
                    "temperature": temperature,
                    "max_output_tokens": 8192,  
                }
            )
        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(f"[red](llm_model.py) | Error in model initialization: {e}[/red]")
            raise