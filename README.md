


## Installation
```bash

pip install -r requirements.txt

```


## Configuration

- set the environment variables for the open-ai apikey and google service account key for google speech to text service


```bash

export OPEN_AI_API_KEY="your open ai api key"
export GOOGLE_APPLICATION_CREDENTIALS="path to google service account key"

```


## Usage
```python

streamlit run main.py

```

# open the browser and go to the following link
```bash

http://localhost:8501/

```

- Select the file and upload it  to get the output

- The output will be displayed on the screen with transcripted text and time stamps


- write now the code is working using whisper transcribe service, but it can be easily modified to use google speech to text service by changing the service in the code

- The code is written in python and uses streamlit for the ui

## Future Work
- Add websockets to stream the input/output in real time
- Add more services for speech to text
