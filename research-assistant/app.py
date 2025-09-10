import os
import uuid
import tempfile
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

from ai_client import AIClient
from web_search import WebSearchClient
from memory_manager import MemoryManager
from document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
ai_client = AIClient()
web_search = WebSearchClient()
memory_manager = MemoryManager()
document_processor = DocumentProcessor()

@app.route('/')
def index():
    return render_template('index.html', 
                         providers=ai_client.get_available_providers(),
                         web_search_enabled=web_search.is_available())

@app.route('/api/research', methods=['POST'])
def api_research():
    data = request.json
    query = data.get('query', '')
    provider = data.get('provider', ai_client.get_available_providers()[0] if ai_client.get_available_providers() else 'deepseek')
    use_web_search = data.get('web_search', False)
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Get conversation context
    context = memory_manager.get_context(session_id)
    
    # Perform web search if enabled and requested
    search_results = []
    if use_web_search and web_search.is_available():
        search_results = web_search.search(query)
        if search_results:
            # Add search results to the query
            search_context = "\n".join([f"Source: {r['title']}\nContent: {r['snippet']}" for r in search_results])
            query = f"{query}\n\nHere are some web search results for context:\n{search_context}"
    
    # Get AI response
    response = ai_client.query(provider, query, context)
    
    # Update conversation history
    memory_manager.add_exchange(session_id, query, response)
    
    return jsonify({
        'response': response,
        'search_results': search_results,
        'session_id': session_id
    })

@app.route('/api/analyze_document', methods=['POST'])
def api_analyze_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    query = request.form.get('query', 'Analyze this document')
    provider = request.form.get('provider', ai_client.get_available_providers()[0] if ai_client.get_available_providers() else 'deepseek')
    session_id = request.form.get('session_id', str(uuid.uuid4()))
    
    # Check if file is supported
    if not document_processor.is_supported(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400
    
    # Save uploaded file temporarily
    file_extension = document_processor.get_extension(file.filename)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
        file.save(temp_file.name)
        text = document_processor.extract_text(temp_file.name, file_extension)
    
    # Clean up temporary file
    os.unlink(temp_file.name)
    
    # Get conversation context
    context = memory_manager.get_context(session_id)
    
    # Prepare the query with document content
    document_query = f"""
    Analyze the following document content and answer the user's query.
    
    DOCUMENT CONTENT:
    {text[:4000]}  # Limit to first 4000 characters
    
    USER QUERY: {query}
    
    Please provide a comprehensive analysis based on the document content.
    """
    
    # Get AI response
    response = ai_client.query(provider, document_query, context)
    
    # Update conversation history
    memory_manager.add_exchange(session_id, f"Document analysis query: {query}", response)
    
    return jsonify({
        'response': response,
        'session_id': session_id
    })

@socketio.on('research_request')
def handle_research_request(data):
    query = data.get('query', '')
    provider = data.get('provider', ai_client.get_available_providers()[0] if ai_client.get_available_providers() else 'deepseek')
    use_web_search = data.get('web_search', False)
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    emit('research_status', {'status': 'searching'})
    
    # Get conversation context
    context = memory_manager.get_context(session_id)
    
    # Perform web search if enabled and requested
    search_results = []
    if use_web_search and web_search.is_available():
        search_results = web_search.search(query)
        if search_results:
            # Add search results to the query
            search_context = "\n".join([f"Source: {r['title']}\nContent: {r['snippet']}" for r in search_results])
            query = f"{query}\n\nHere are some web search results for context:\n{search_context}"
    
    # Get AI response
    response = ai_client.query(provider, query, context)
    
    # Update conversation history
    memory_manager.add_exchange(session_id, query, response)
    
    # Beautify the response for better readability
    if isinstance(response, str):
        beautified_response = response.strip()
        beautified_response = beautified_response.replace('\n\n', '<br><br>').replace('\n', '<br>')
    else:
        beautified_response = str(response)

    emit('research_complete', {
        'response': beautified_response,
        'search_results': search_results,
        'session_id': session_id
    })

if __name__ == "__main__":
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Create basic HTML template
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Research Assistant</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Advanced Research Assistant</h1>
        
        <div class="controls">
            <label for="provider">AI Provider:</label>
            <select id="provider">
                {% for provider in providers %}
                <option value="{{ provider }}">{{ provider }}</option>
                {% endfor %}
            </select>
            
            {% if web_search_enabled %}
            <label for="web-search">Web Search:</label>
            <input type="checkbox" id="web-search">
            {% endif %}
        </div>
        
        <div class="chat-container" id="chat-container"></div>
        
        <div class="input-container">
            <textarea id="query-input" placeholder="Enter your research question..." rows="3"></textarea>
            <button onclick="sendQuery()">Send</button>
        </div>
        
        <div class="file-upload">
            <h3>Analyze Document</h3>
            <input type="file" id="file-input" accept=".txt,.pdf,.docx">
            <textarea id="document-query" placeholder="What would you like to know about this document?" rows="2"></textarea>
            <button onclick="analyzeDocument()">Analyze Document</button>
        </div>
    </div>
    
    <script>
        const socket = io();
        let sessionId = Date.now().toString();
        
        socket.on('research_status', function(data) {
            addMessage('Assistant', 'Searching for information...', 'status');
        });
        
        socket.on('research_complete', function(data) {
            // Remove status message
            const statusMessages = document.querySelectorAll('.status-message');
            statusMessages.forEach(msg => msg.remove());
            
            addMessage('Assistant', data.response);
            
            // Display search results if any
            if (data.search_results && data.search_results.length > 0) {
                let resultsHtml = '<h4>Search Results:</h4>';
                data.search_results.forEach(result => {
                    resultsHtml += `
                        <div class="search-result">
                            <a href="${result.link}" target="_blank">${result.title}</a>
                            <p>${result.snippet}</p>
                            <small>Source: ${result.source}</small>
                        </div>
                    `;
                });
                addMessage('Assistant', resultsHtml, 'search-results');
            }
            
            sessionId = data.session_id;
        });
        
        function addMessage(sender, message, className = '') {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender.toLowerCase()}-message ${className}`;
            messageDiv.innerHTML = `<strong>${sender}:</strong><br>${message}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function sendQuery() {
            const query = document.getElementById('query-input').value;
            const provider = document.getElementById('provider').value;
            const webSearch = document.getElementById('web-search') ? document.getElementById('web-search').checked : false;
            
            if (!query) return;
            
            addMessage('You', query, 'user-message');
            document.getElementById('query-input').value = '';
            
            // Send via WebSocket for real-time updates
            socket.emit('research_request', {
                query: query,
                provider: provider,
                web_search: webSearch,
                session_id: sessionId
            });
        }
        
        function analyzeDocument() {
            const fileInput = document.getElementById('file-input');
            const query = document.getElementById('document-query').value || 'Analyze this document';
            const provider = document.getElementById('provider').value;
            
            if (!fileInput.files.length) {
                alert('Please select a file first');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('query', query);
            formData.append('provider', provider);
            formData.append('session_id', sessionId);
            
            addMessage('You', `Document analysis: ${query}`, 'user-message');
            
            fetch('/api/analyze_document', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                addMessage('Assistant', data.response);
                sessionId = data.session_id;
            })
            .catch(error => {
                addMessage('Assistant', 'Error analyzing document: ' + error);
            });
        }
        
        // Allow pressing Enter to send message
        document.getElementById('query-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuery();
            }
        });
    </script>
</body>
</html>
        ''')
    
    # Create CSS file
    with open('static/style.css', 'w') as f:
        f.write('''
body {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
}

.container {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
    color: #333;
    text-align: center;
}

.controls {
    margin-bottom: 15px;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 5px;
}

.controls label {
    margin-right: 10px;
    font-weight: bold;
}

.controls select, .controls input {
    margin-right: 15px;
}

.chat-container {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    height: 400px;
    overflow-y: auto;
    margin-bottom: 15px;
    background-color: #fafafa;
}

.message {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 5px;
}

.user-message {
    background-color: #e6f7ff;
    text-align: right;
}

.assistant-message {
    background-color: #f0f0f0;
}

.status-message {
    background-color: #fff3cd;
    font-style: italic;
}

.search-result {
    border-left: 3px solid #4CAF50;
    padding-left: 10px;
    margin-bottom: 10px;
    background-color: #f8fff8;
}

.search-result a {
    color: #1a73e8;
    text-decoration: none;
    font-weight: bold;
}

.search-result a:hover {
    text-decoration: underline;
}

.search-result small {
    color: #666;
}

.input-container {
    display: flex;
    margin-bottom: 15px;
}

#query-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
}

button {
    padding: 10px 15px;
    margin-left: 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}

.file-upload {
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 5px;
    margin-top: 15px;
}

.file-upload h3 {
    margin-top: 0;
}

#file-input {
    margin-bottom: 10px;
}

#document-query {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
    margin-bottom: 10px;
}
        ''')
    
    # Run the Flask app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)