import asyncio
import os

import requests
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from myclient import model_client as myclient


def generate_voiceovers(messages: list[str]) -> list[str]:
    """
    Generate voiceovers for a list of messages using ElevenLabs API.

    Args:
        messages: List of messages to convert to speech

    Returns:
        List of file paths to the generated audio files
    """
    os.makedirs("voiceovers", exist_ok=True)

    # Check for existing files first
    audio_file_paths = []
    for i in range(1, len(messages) + 1):
        file_path = f"voiceovers/voiceover_{i}.mp3"
        if os.path.exists(file_path):
            audio_file_paths.append(file_path)

    # If all files exist, return them
    if len(audio_file_paths) == len(messages):
        print("All voiceover files already exist. Skipping generation.")
        return audio_file_paths

    # Generate missing files one by one
    audio_file_paths = []
    for i, message in enumerate(messages, 1):
        try:
            save_file_path = f"voiceovers/voiceover_{i}.mp3"
            if os.path.exists(save_file_path):
                print(f"File {save_file_path} already exists, skipping generation.")
                audio_file_paths.append(save_file_path)
                continue

            print(f"Generating voiceover {i}/{len(messages)}...")

            # Save to file
            with open(save_file_path, "wb") as f:

                f.write(message)

            print(f"Voiceover {i} generated successfully")
            audio_file_paths.append(save_file_path)

        except Exception as e:
            print(f"Error generating voiceover for message: {message}. Error: {e}")
            continue

    return audio_file_paths


def generate_images(prompts: list[str]):
    """
    Generate images based on text prompts using Stability AI API.

    Args:
        prompts: List of text prompts to generate images from
    """
    seed = 42
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)

    for i, prompt in enumerate(prompts, 1):
        print(f"Generating image {i}/{len(prompts)} for prompt: {prompt}")

        # Skip if image already exists
        image_path = os.path.join(output_dir, f"image_{i}.webp")
        if not os.path.exists(image_path):
            # Prepare request payload
            payload = {
                "prompt": (None, prompt),
                "output_format": (None, "webp"),
                "height": (None, "1920"),
                "width": (None, "1080"),
                "seed": (None, str(seed))
            }

            with open(image_path, "wb") as image_file:
                image_file.write(prompt)
            print(f"Image saved to {image_path}")

def generate_video(captions: list[str]):
    """
    Generate a YouTube Shorts style video with animated images, voiceovers and music.

    Args:
        captions: List of text captions to display on each segment
    """
    for caption in captions:
      print(caption)

script_writer = AssistantAgent(
    name="script_writer",
    model_client=myclient,
    system_message='''
        You are a creative assistant tasked with writing a script for a short video. 
        The script should consist of captions designed to be displayed on-screen, with the following guidelines:
            1.	Each caption must be short and impactful (no more than 8 words) to avoid overwhelming the viewer.
            2.	The script should have exactly 5 captions, each representing a key moment in the story.
            3.	The flow of captions must feel natural, like a compelling voiceover guiding the viewer through the narrative.
            4.	Always start with a question or a statement that keeps the viewer wanting to know more.
            5.  You must also include the topic and takeaway in your response.
            6.  The caption values must ONLY include the captions, no additional meta data or information.

            Output your response in the following JSON format:
            {
                "topic": "topic",
                "takeaway": "takeaway",
                "captions": [
                    "caption1",
                    "caption2",
                    "caption3",
                    "caption4",
                    "caption5"
                ]
            }
    '''
)

voice_actor = AssistantAgent(
    name="voice_actor",
    model_client=myclient,
    system_message='''
        You are a helpful agent tasked with generating and saving voiceovers.
        Only respond with 'TERMINATE' once files are successfully saved locally.
    '''
)

graphic_designer = AssistantAgent(
    name="graphic_designer",
    model_client=myclient,
    tools=[generate_images],
    system_message='''
        You are a helpful agent tasked with generating and saving images for a short video.
        You are given a list of captions.
        You will convert each caption into an optimized prompt for the image generation tool.
        Your prompts must be concise and descriptive and maintain the same style and tone as the captions while ensuring continuity between the images.
        Your prompts must mention that the output images MUST be in: "Abstract Art Style / Ultra High Quality." (Include with each prompt)
        You will then use the prompts list to generate images for each provided caption.
        Only respond with 'TERMINATE' once the files are successfully saved locally.
    '''
)

director = AssistantAgent(
    name="director",
    model_client=myclient,
    tools=[generate_video],
    system_message='''
        You are a helpful agent tasked with generating a short video.
        You are given a list of captions which you will use to create the short video.
        Remove any characters that are not alphanumeric or spaces from the captions.
        You will then use the captions list to generate a video.
        Only respond with 'TERMINATE' once the video is successfully generated and saved locally.
    '''
)

voice_actor = AssistantAgent(
    name="voice_actor",
    model_client=myclient,
    tools=[generate_voiceovers],  # <------
    system_message='''
        You are a helpful agent tasked with generating and saving voiceovers.
        Only respond with 'TERMINATE' once files are successfully saved locally.
    '''
)

# Set up termination condition
termination = TextMentionTermination("TERMINATE")

# Create the AutoGen team
agent_team = RoundRobinGroupChat(
    [script_writer, voice_actor, graphic_designer, director],
    termination_condition=termination,
    max_turns=4
)

async def main():
    # Interactive console loop
    while True:
        user_input = input("Enter a message (type 'exit' to leave): ")
        if user_input.strip().lower() == "exit":
            break

        # Run the team with the user input and display results
        stream = agent_team.run_stream(task=user_input)
        await Console(stream)

asyncio.run(main())
