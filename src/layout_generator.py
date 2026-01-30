import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json
from src.config import Config

class LayoutGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=Config.GEMINI_API_KEY,
            temperature=0.7
        )

    def generate_layout(self, venture_type, area, dimensions, user_prompt):
        """
        Generate a layout based on user input.
        Returns a JSON object with layout details and potentially SVG code.
        """
        prompt_template = """
        You are an expert architect and interior designer. 
        Your task is to design a functional and aesthetic layout for a {venture_type} with an area of {area} sq ft.
        The site outline is a polygon defined by the following sequential (x, y) coordinates drawn on an 800x400 grid: {dimensions}.
        User's specific requirements: {user_prompt}

        Please provide a detailed floor plan. 
        Include:
        1. A list of rooms/zones with their approximate sizes and positions.
        2. A description of the design philosophy used.
        3. An SVG representation of the floor plan. The SVG should be clean, professional, and include labels for each room.
        
        Output the response in the following JSON format:
        {{
            "title": "A catchy name for the layout",
            "description": "Short description of the layout",
            "rooms": [
                {{"name": "Room Name", "size": "dimensions", "position": "location description"}}
            ],
            "design_philosophy": "Detailed explanation",
            "svg": "<svg>...</svg>"
        }}
        
        Ensure the JSON is valid and the SVG is self-contained.
        """

        prompt = PromptTemplate(
            input_variables=["venture_type", "area", "dimensions", "user_prompt"],
            template=prompt_template
        )

        # Using the new LCEL approach for LangChain
        chain = prompt | self.llm
        
        response = chain.invoke({
            "venture_type": venture_type,
            "area": area,
            "dimensions": json.dumps(dimensions),
            "user_prompt": user_prompt
        })

        content = response.content
        
        # Clean up JSON if LLM added markdown backticks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return {
                "error": "Failed to parse layout data",
                "raw_content": response.content
            }

layout_generator = LayoutGenerator()
