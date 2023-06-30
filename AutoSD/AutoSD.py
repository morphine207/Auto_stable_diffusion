import openai
import os
import requests
import re
from colorama import Fore, Style, init
import datetime
import base64

# Initialize colorama
init()

# Define a function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Define a function to save content to a file
def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

# Set the OpenAI API keys by reading them from files
api_key = open_file('openaiapikey2.txt')

#sd api key
sd_api_key = open_file('sdapikey.txt')

# Initialize two empty lists to store the conversations for each chatbot
conversation1 = []
conversation2 = []

# Read the content of the files containing the chatbots' prompts
chatbot1 = open_file('chatbot4.txt')
chatbot2 = open_file('chatbot3.txt')

# Define a function to make an API call to the OpenAI ChatCompletion endpoint
def chatgpt(api_key, conversation, chatbot, user_input, temperature=0.75, frequency_penalty=0.2, presence_penalty=0):

    # Set the API key
    openai.api_key = api_key

    # Update conversation by appending the user's input
    conversation.append({"role": "user","content": user_input})

    # Insert prompt into message history
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    messages_input.insert(0, prompt[0])

    # Make an API call to the ChatCompletion endpoint with the updated messages
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)

    # Extract the chatbot's response from the API response
    chat_response = completion['choices'][0]['message']['content']

    # Update conversation by appending the chatbot's response
    conversation.append({"role": "assistant", "content": chat_response})

    # Return the chatbot's response
    return chat_response
    
# Define a function to generate images using the Stability API    
def generate_image(api_key, text_prompt, height=512, width=512, cfg_scale=7, clip_guidance_preset="FAST_BLUE", steps=50, samples=1):
    api_host = 'https://api.stability.ai'
    engine_id = "stable-diffusion-xl-beta-v2-2-2"

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": text_prompt
                }
            ],
            "cfg_scale": cfg_scale,
            "clip_guidance_preset": clip_guidance_preset,
            "height": height,
            "width": width,
            "samples": samples,
            "steps": steps,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    image_data = data["artifacts"][0]["base64"]

    # Save the generated image to a file with a unique name in the "SDimages" folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    image_filename = os.path.join("SDimages", f"generated_image_{timestamp}.png")

    with open(image_filename, "wb") as f:
        f.write(base64.b64decode(image_data))

    return image_filename
    
# Add a function to print text in green if it contains certain keywords
def print_colored(agent, text):
    agent_colors = {
        "Agent69:": Fore.YELLOW,
        "Agent007:": Fore.CYAN,
    }

    color = agent_colors.get(agent, "")

    print(color + f"{agent}: {text}" + Style.RESET_ALL, end="")  

num_turns = 10  # Number of turns for each chatbot (you can adjust this value)

# Start the conversation with ChatBot1's first message
user_message = "Hello Agent007, I am Agent69. How can i help you?"

# Update the loop where chatbots talk to each other
for i in range(num_turns):
    print_colored("Agent69:", f"{user_message}\n\n")
    save_file("ChatLog.txt", "Agent69: " + user_message + "\n\n")
    response = chatgpt(api_key, conversation1, chatbot1, user_message)
    user_message = response
    
    if "generate_image:" in user_message:
        image_prompt = user_message.split("generate_image:")[1].strip()
        image_path = generate_image(sd_api_key, image_prompt)
        print(f"Generated image: {image_path}")    

    print_colored("Agent007:", f"{user_message}\n\n")
    save_file("ChatLog.txt", "Agent007: " + user_message + "\n\n")
    response = chatgpt(api_key, conversation2, chatbot2, user_message)
    user_message = response
    
    if "generate_image:" in user_message:
        image_prompt = user_message.split("generate_image:")[1].strip()
        image_path = generate_image(sd_api_key, image_prompt)
        print(f"Generated image: {image_path}")    
    
