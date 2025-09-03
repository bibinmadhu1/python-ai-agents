# python-ai-agents
$ python -m venv research-env
source research-env/bin/activate

1. Install Dependencies

bash
pip install requests python-dotenv flask flask-socketio pdfminer.six python-docx PyPDF2 serpapi google-generativeai huggingface_hub google-api-python-client
2. Set Up API Keys

Create a .env file with all your API keys:

env
DEEPSEEK_API_KEY=your_actual_deepseek_key
OPENAI_API_KEY=your_actual_openai_key
ANTHROPIC_API_KEY=your_actual_anthropic_key
GEMINI_API_KEY=your_actual_gemini_key
HUGGINGFACE_API_KEY=your_actual_huggingface_key
SERPAPI_API_KEY=your_actual_serpapi_key
GOOGLE_PSE_ID=your_actual_google_pse_id
GOOGLE_API_KEY=your_actual_google_api_key
3. Run the Application



bash
python app.py
4. Access the Web Interface

Open your browser and go to http://localhost:5000

