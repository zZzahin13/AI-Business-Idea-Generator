import gradio as gr
import google.generativeai as genai
import os
from typing import List, Dict, Tuple, Any

# Configure Gemini API
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")
genai.configure(api_key=api_key)

# Store business idea
business_idea = None

def generate_business_idea(skills: str, interests: str, budget: str) -> str:
    """Generate a business idea based on user input."""
    global business_idea
    
    prompt = f"""Suggest a unique business idea based on:
    - Skills: {skills}
    - Interests: {interests}
    - Budget: {budget}
    Provide a short description and potential revenue model."""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            business_idea = response.text
            return business_idea
        else:
            return "Failed to generate a business idea. Please try again."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def business_chatbot(message: str, history: List[List[str]]) -> str:
    """Chatbot that discusses the generated business idea."""
    global business_idea
    
    if not business_idea:
        return "Please generate a business idea first before asking questions."

    try:
        
        chat_context = "\n".join([f"User: {q}\nAI: {a}" for q, a in history])
        
        chat_prompt = f"""Business Idea: {business_idea}
        Conversation History:
        {chat_context}
        User Question: {message}
        Provide a detailed response, considering the previous context."""

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(chat_prompt)

        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "Sorry, I couldn't generate a response. Try again."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Gradio interface
with gr.Blocks() as iface:
    gr.Markdown("# AI Business Idea Generator with Chatbot")

    with gr.Row():
        skills = gr.Textbox(label="Your Skills", placeholder="e.g., Programming, Marketing")
        interests = gr.Textbox(label="Your Interests", placeholder="e.g., Technology, Sustainability")
        budget = gr.Textbox(label="Budget Range ($)", placeholder="e.g., 1000-5000")
        generate_btn = gr.Button("Generate Business Idea", variant="primary")

    business_output = gr.Textbox(label="Generated Business Idea", interactive=False)

    generate_btn.click(
        generate_business_idea,
        inputs=[skills, interests, budget],
        outputs=business_output
    )

    gr.Markdown("## Ask Questions About Your Business Idea")
    chatbot = gr.ChatInterface(
        fn=business_chatbot,
        examples=["How can I market this business?", 
                 "What are the potential challenges?",
                 "Can you suggest a name for this business?"],
        title="Business Idea Chatbot"
    )

iface.launch(share=True)