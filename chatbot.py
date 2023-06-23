from bottle import Bottle, request, template, static_file, response, run, route
import openai
import uuid
from docx import Document
import tempfile
import os

# Set up your OpenAI API key
openai.api_key = "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"

# Create a Bottle app
app = Bottle()

# Dictionary to store the chat history for each session
# Global dictionary to store chat history and session data
session_data = {}

def get_chat_history(session_id):
    # Get the chat history for the specified session
    if session_id in session_data:
        return session_data[session_id]['chat_history']
    else:
        return ''

def get_prompt(file_data):
    # Generate the prompt based on the file data
    if file_data:
        # Process the file data and generate a prompt
        # Replace this with your own logic
        prompt = "Tell me about the file."
    else:
        prompt = "Enter your input."

    return prompt

def update_chat_history(session_id, chat_history):
    # Update the chat history for the specified session
    session_data[session_id] = {'chat_history': chat_history}


# Function to generate a response using ChatGPT for a specific session
def generate_chat_response(session_id, user_input, file_data, completion_length=100):
    chat_history = get_chat_history(session_id)
    prompt = get_prompt(file_data) if file_data else user_input

    # Concatenate the chat history and user input with the file data
    inputs = chat_history + '\n' + prompt

    # Generate chat response using the specified completion length
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=inputs,
        max_tokens=completion_length,
        temperature=0.7,
        n=1,
        stop=None,
        logprobs=0
    )

    response_text = response.choices[0].text.strip()

    # Update chat history
    update_chat_history(session_id, inputs + '\n' + response_text)

    return response_text


# Rest of the code remains the same



@app.route('/')
def home():
    session_id = str(uuid.uuid4())  # Generate a random session ID
    prompts = [
        "Write 3 Introductory Emails for an Organization",
        "3 Templates For a Financial Report",
        "Pointers for a Product Presentation",
        "Social media sample for Hiring",
        "3 Leave Applications to a Manager",
        "3 Referral Emails for an Organization",
        "3 Sample Sales pointers for a PPT",
        "3 different Briefings about a company",
        "Pointers for a Sample Analytical Report",
        "Company Profile of Stratacent",
        "Email for Work from Home",
        "Event Announcement Email"
    ]

    return template('index.html', session_id=session_id, prompts=prompts)


# Route to serve static files
@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./static')


# Chat route
@app.route('/chat', method='POST')
def chat():
    user_input = request.forms.get('user_input')
    session_id = request.forms.get('session_id')

    # Generate a response using ChatGPT for the specific session
    response_text = generate_chat_response(session_id, user_input, None)

    return {'response': response_text}


@app.route('/upload', method='POST')
def upload():
    file = request.files.get('file')
    session_id = request.forms.get('session_id')

    if file:
        # Generate a unique filename using UUID
        unique_filename = str(uuid.uuid4()) + '_' + file.filename
        temp_file_path = os.path.join(tempfile.gettempdir(), unique_filename)

        # Save the file in chunks
        chunk_size = 4096  # Set the chunk size as per your requirement
        with open(temp_file_path, 'wb') as f:
            while True:
                chunk = file.file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)

        # Read the content of the uploaded file with 'utf-8' encoding
        with open(temp_file_path, 'r', encoding='utf-8', errors='replace') as f:
            file_data = f.read()

        # Limit the prompt length to 4000 characters
        prompt = file_data[:4000]

        # Generate a response using ChatGPT with the limited prompt
        response_text = generate_chat_response(session_id, prompt, file_data)

        # Delete the temporary file
        os.remove(temp_file_path)

        return {'response': response_text}

    return ''


# Global dictionary to store session chat history
session_chat_history = {}

@app.route('/download/pdf/<session_id:path>')
def download_pdf(session_id):
    chat_history = session_chat_history.get(session_id, "")

    # Create a PDF document
    pdf_content = f"Chat History:\n\n{chat_history}"

    # Set the response headers
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="chat_history.pdf"'

    # Save the PDF file directly to the user's Downloads folder
    file_path = os.path.expanduser('~/Downloads/chat_history.pdf')
    with open(file_path, 'wb') as file:
        file.write(pdf_content.encode('utf-8'))

    # Return an empty response
    return ''


# Start the application
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
