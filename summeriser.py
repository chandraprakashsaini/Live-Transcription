import openai
import json
import time

# Set up your OpenAI API key
openai.api_key = 'your_openai_api_key_here'

# Function to process the transcription and send to ChatGPT for multiple tasks processing
async def process_transcription(transcription_text):
    prompt = f"""
    You are a task manager bot that receives a transcript of multiple ongoing tasks in real time. Based on the transcript, identify all tasks and return a JSON response with the following structure:
    - Each task should have:
      - `task_description`: A description of the task.
      - `status`: 'done' if the task is completed, 'in progress' if it is still ongoing.
      - `progress_percentage`: Percentage completion (if applicable).
    
    Here is the transcript:
    {transcription_text}
    
    Response should be in JSON format. Example:
    [
        {{
            "task_description": "Fixing the printer",
            "status": "done",
            "progress_percentage": 100
        }},
        {{
            "task_description": "Cleaning the office",
            "status": "in progress",
            "progress_percentage": 60
        }}
    ]
    """

    
    # Make an asynchronous request to the OpenAI API
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3,
            n=1
        )
        
        # Parse the result
        chatgpt_response = response.choices[0].message.content.strip()
        
        # Try to parse JSON output
        return json.loads(chatgpt_response)
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {"status": "error", "message": str(e)}
