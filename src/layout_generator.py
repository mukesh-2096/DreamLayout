import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json
from src.config import Config

class LayoutGenerator:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration or .env file. Please add it to proceed.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7
        )

    def generate_layout(self, venture_type, area, dimensions, user_prompt):
        """
        Generate a layout based on user input.
        Returns a JSON object with layout details and potentially SVG code.
        """
        prompt_template = """
        You are an expert architect and interior designer. 
        Your task is to design a functional, professional, and aesthetic layout for a {venture_type} with an area of {area}.
        
        CRITICAL INPUT - SITE OUTLINE:
        The site outline below is a rough hand-drawn sketch provided as sequential (x, y) coordinates on an 800x400 grid:
        {dimensions}

        INSTRUCTIONS FOR LAYOUT DESIGN:
        1. RECTIFY THE SHAPE: The input coordinates are rough. First, interpret these as a clean geometric polygon. Align edges to be straight and use sharp, professional angles (orthogonal 90° angles preferred unless the sketch clearly implies a diagonal). This "rectified" shape will be the outer boundary of your design.
        2. ROOM PLANNING: Distribute rooms logically within this rectified boundary based on the {venture_type} and {area}. Ensure efficient circulation and logical flow.
        3. MULTI-FLOOR/PAGE SUPPORT: If the user requirements suggest multiple floors, you MUST provide separate layouts for EACH floor.
        4. AREA ANALYSIS: Carefully consider if the requested {area} is sufficient for the {venture_type} and user requirements. 
        5. CONVERSATIONAL RESPONSE:
           - Start with a friendly confirmation like: "Great news! I've successfully crafted a custom architectural layout that perfectly aligns with your requirements."
           - Provide a professional summary of your design decisions and mention if the area is sufficient.
           - CRITICAL: Provide a CLEAR LEGEND of all rooms/components with their corresponding numbers (from the SVG) and exact dimensions. 
             Example:
             1. Master Bedroom: 15'x12'
             2. Modular Kitchen: 10'x12'
        6. SVG STYLING & LABELING (CRITICAL FOR READABILITY):
           - Use thick, dark lines (2px or 3px) for outer and internal walls.
           - Use light, professional pastel fill colors for different room types (e.g., #EBF4FF for living, #F0FFF4 for kitchen).
           - LABEL CLARITY & NUMBERING: 
             * Do NOT place long text names inside rooms as they often overlap.
             * Instead, assign a unique NUMBER (1, 2, 3...) to each room.
             * Place a small circle with the number inside it at the center of the room.
             * If the room is too small, place a dot in the room and draw a thin leader line (line) to the number placed just outside the room outline.
             * Ensure numbers are bold and legible (font-size: 14px).
           - Add subtle 1px dashed lines for furniture or area suggestions.
           - Ensure the SVG viewBox is set correctly to show the entire rectified layout with a 50px padding.
        
        User's specific requirements: {user_prompt}

        Please provide a detailed floor plan in the following JSON format. 
        {{
            "title": "Professional Project Name",
            "description": "Architectural summary",
            "conversational_response": "A friendly confirmation followed by expert architectural advice and a numbered legend of components. (ChatGPT style)",
            "floors": [
                {{
                    "floor_name": "e.g., Ground Floor",
                    "rooms": [
                        {{"id": 1, "name": "Room Name", "size": "e.g., 12' x 15'", "position": "Description of location"}}
                    ],
                    "svg": "<svg ...>...</svg>"
                }}
            ]
        }}
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
