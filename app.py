import streamlit as st
from openai import OpenAI
# import os
# from dotenv import load_dotenv
import logging

# Configure logging to see output in the console
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables (for API key)
# load_dotenv()

# Initialize the OpenAI client for OpenRouter
api_key = st.secrets["DEEPSEEK_API_KEY"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    default_headers={"Authorization": f"Bearer {api_key}"}
)

# Bot backstory (Only modifiable in the code by developers)
bot_backstory = '''
You are a room service assistant at a luxury hotel. Your role is to assist guests with various services, including restaurant recommendations and reservations, housekeeping requests, in-room dining and delivery, concierge services, and general hotel amenities. Be extremely polite, professional, and accommodating, ensuring that guests feel valued and well taken care of.
Always identify yourself as the room service assistant and provide detailed, helpful responses to their inquiries.
SPA time: 8AM to 10AM
Breakfast: 8AM to 9:30AM
Lunch: 12PM to 2PM
Dinner: 8PM to 1AM
These timings are not flexible and cannot be changed at the request of guests.
Always answer in the same language as the prompt.
Maintain a very friendly and welcoming tone while being strict about the timing.
'''

# Streamlit app
def main():
    st.set_page_config(page_title="Room Service", page_icon="🤖")
    st.title("Room Service 🤖")

    st.write("API Key found:", "Yes" if "DEEPSEEK_API_KEY" in st.secrets else "No")

    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input
    user_input = st.chat_input("Ask me anything...")

    # Display chat history (before processing new input)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Process user input
    if user_input:
        logger.debug("User input received: %s", user_input)
        
        # Add user message to chat history and display it immediately
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display the updated chat history (including the new user message)
        with st.chat_message("user"):
            st.write(user_input)

        # Prepare the messages for the API
        messages = [
            {"role": "system", "content": bot_backstory},  # Bot's backstory (hidden from users)
            *st.session_state.chat_history  # Include the chat history
        ]

        # Call the API with error handling
        bot_response = None
        try:
            logger.debug("Calling API with messages: %s", messages)
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="meta-llama/llama-3-8b-instruct",  # Try a different model
                    messages=messages,
                    temperature=0.7,  # Adjust for creativity
                    max_tokens=512,  # Limit response length
                )
                bot_response = response.choices[0].message.content
                logger.debug("API response received: %s", bot_response)

                # Basic validation: Check if response looks like code (contains "```")
                if "```" in bot_response and "code" not in user_input.lower():
                    bot_response = "I apologize, I seem to have misunderstood. Let’s try again. How can I assist you today?"
                    logger.debug("Response contained code; using fallback message.")

        except Exception as e:
            bot_response = f"Error: {str(e)}"
            logger.error("API Error: %s", str(e))  # Log the error with more detail

        # Add bot's response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        logger.debug("Chat history updated with response: %s", bot_response)

        # Display the bot's response
        with st.chat_message("assistant"):
            st.write(bot_response)
            logger.debug("Response displayed: %s", bot_response)

# Run the app
if __name__ == "__main__":
    main()
