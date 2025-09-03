#!/usr/bin/env python3
import os
import sys
import uuid
import tempfile
import argparse
from dotenv import load_dotenv

# Import our modular components
from ai_client import AIClient
from web_search import WebSearchClient
from memory_manager import MemoryManager
from document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

class TerminalResearchAssistant:
    def __init__(self, default_provider="deepseek", use_web_search=False):
        """
        Initialize the terminal research assistant
        
        Args:
            default_provider: Default AI provider to use
            use_web_search: Whether to enable web search by default
        """
        self.ai_client = AIClient()
        self.web_search = WebSearchClient()
        self.memory_manager = MemoryManager()
        self.document_processor = DocumentProcessor()
        
        # Set default provider if available, otherwise use first available
        available_providers = self.ai_client.get_available_providers()
        if default_provider in available_providers:
            self.current_provider = default_provider
        elif available_providers:
            self.current_provider = available_providers[0]
        else:
            print("Error: No AI providers configured. Please check your API keys.")
            sys.exit(1)
            
        self.use_web_search = use_web_search and self.web_search.is_available()
        self.session_id = str(uuid.uuid4())
        
        # Display welcome message
        self._print_welcome()
    
    def _print_welcome(self):
        """Display welcome message and current settings"""
        print("\n" + "="*60)
        print("          TERMINAL RESEARCH ASSISTANT")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print(f"Current AI Provider: {self.current_provider}")
        print(f"Web Search: {'Enabled' if self.use_web_search else 'Disabled'}")
        print(f"Available Providers: {', '.join(self.ai_client.get_available_providers())}")
        print("="*60)
        print("\nCommands:")
        print("  /provider <name>    - Switch AI provider")
        print("  /websearch <on|off> - Toggle web search")
        print("  /upload <file>      - Upload and analyze a document")
        print("  /clear              - Clear conversation history")
        print("  /quit or /exit      - Exit the program")
        print("\nEnter your research question to begin.")
        print("="*60)
    
    def _print_response(self, response, search_results=None):
        """Format and print the AI response"""
        print("\n" + "-"*60)
        print("RESPONSE:")
        print("-"*60)
        print(response)
        
        if search_results:
            print("\n" + "-"*60)
            print("SEARCH RESULTS:")
            print("-"*60)
            for i, result in enumerate(search_results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   {result['snippet']}")
                print(f"   URL: {result['link']}")
                print(f"   Source: {result['source']}")
        
        print("-"*60)
    
    def process_query(self, query):
        """Process a research query"""
        if not query.strip():
            return
        
        # Get conversation context
        context = self.memory_manager.get_context(self.session_id)
        
        # Perform web search if enabled
        search_results = []
        if self.use_web_search:
            print("Searching the web...", end=" ", flush=True)
            search_results = self.web_search.search(query)
            print("Done!")
            
            if search_results:
                # Add search results to the query
                search_context = "\n".join([f"Source: {r['title']}\nContent: {r['snippet']}" for r in search_results])
                query = f"{query}\n\nHere are some web search results for context:\n{search_context}"
        
        # Get AI response
        print(f"Querying {self.current_provider}...", end=" ", flush=True)
        response = self.ai_client.query(self.current_provider, query, context)
        print("Done!")
        
        # Update conversation history
        self.memory_manager.add_exchange(self.session_id, query, response)
        
        # Display response
        self._print_response(response, search_results)
    
    def analyze_document(self, file_path, query="Analyze this document"):
        """Analyze a document file"""
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return
        
        # Check if file is supported
        if not self.document_processor.is_supported(file_path):
            print("Error: Unsupported file type. Supported types: .txt, .pdf, .docx")
            return
        
        # Extract text from document
        file_extension = self.document_processor.get_extension(file_path)
        print(f"Extracting text from {file_extension.upper()} file...", end=" ", flush=True)
        text = self.document_processor.extract_text(file_path, file_extension)
        print("Done!")
        
        # Get conversation context
        context = self.memory_manager.get_context(self.session_id)
        
        # Prepare the query with document content
        document_query = f"""
        Analyze the following document content and answer the user's query.
        
        DOCUMENT CONTENT:
        {text[:4000]}  # Limit to first 4000 characters
        
        USER QUERY: {query}
        
        Please provide a comprehensive analysis based on the document content.
        """
        
        # Get AI response
        print(f"Analyzing with {self.current_provider}...", end=" ", flush=True)
        response = self.ai_client.query(self.current_provider, document_query, context)
        print("Done!")
        
        # Update conversation history
        self.memory_manager.add_exchange(
            self.session_id, 
            f"Document analysis query: {query} for file: {os.path.basename(file_path)}", 
            response
        )
        
        # Display response
        self._print_response(response)
    
    def run(self):
        """Main loop for the terminal interface"""
        try:
            while True:
                try:
                    user_input = input(f"\n[{self.current_provider}, Web: {'ON' if self.use_web_search else 'OFF'}] > ").strip()
                    
                    # Handle commands
                    if user_input.startswith('/'):
                        self._handle_command(user_input)
                        continue
                    
                    # Handle empty input
                    if not user_input:
                        continue
                    
                    # Process research query
                    self.process_query(user_input)
                    
                except KeyboardInterrupt:
                    print("\nUse /quit to exit or press Ctrl+C again to force quit.")
                except EOFError:
                    print("\n\nGoodbye!")
                    break
                except Exception as e:
                    print(f"\nError: {str(e)}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
    
    def _handle_command(self, command):
        """Handle terminal commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == '/provider' and len(parts) > 1:
            new_provider = parts[1].lower()
            available = self.ai_client.get_available_providers()
            
            if new_provider in available:
                self.current_provider = new_provider
                print(f"Switched to provider: {new_provider}")
            else:
                print(f"Provider '{new_provider}' not available. Available providers: {', '.join(available)}")
        
        elif cmd == '/websearch':
            if len(parts) > 1:
                arg = parts[1].lower()
                if arg in ['on', 'yes', 'true', '1']:
                    if self.web_search.is_available():
                        self.use_web_search = True
                        print("Web search enabled.")
                    else:
                        print("Web search is not available. Check your API keys.")
                elif arg in ['off', 'no', 'false', '0']:
                    self.use_web_search = False
                    print("Web search disabled.")
                else:
                    print("Usage: /websearch <on|off>")
            else:
                # Toggle web search
                self.use_web_search = not self.use_web_search
                status = "enabled" if self.use_web_search else "disabled"
                print(f"Web search {status}.")
        
        elif cmd == '/upload' and len(parts) > 1:
            file_path = parts[1]
            query = " ".join(parts[2:]) if len(parts) > 2 else "Analyze this document"
            self.analyze_document(file_path, query)
        
        elif cmd in ['/clear', '/reset']:
            self.memory_manager.clear_session(self.session_id)
            print("Conversation history cleared.")
        
        elif cmd in ['/quit', '/exit', '/q']:
            print("Goodbye!")
            sys.exit(0)
        
        elif cmd == '/help':
            self._print_welcome()
        
        else:
            print("Unknown command. Type /help for available commands.")

def main():
    """Main function to run the terminal research assistant"""
    parser = argparse.ArgumentParser(description='Terminal Research Assistant')
    parser.add_argument('--provider', default='deepseek', 
                       help='Default AI provider (deepseek, openai, anthropic, gemini, huggingface)')
    parser.add_argument('--web-search', action='store_true',
                       help='Enable web search by default')
    parser.add_argument('--query', '-q', 
                       help='Process a single query and exit (non-interactive mode)')
    parser.add_argument('--file', '-f', 
                       help='Analyze a document file and exit (non-interactive mode)')
    parser.add_argument('--document-query', '-d', default='Analyze this document',
                       help='Query for document analysis (used with --file)')
    
    args = parser.parse_args()
    
    # Initialize the research assistant
    assistant = TerminalResearchAssistant(
        default_provider=args.provider,
        use_web_search=args.web_search
    )
    
    # Non-interactive mode for single query
    if args.query:
        assistant.process_query(args.query)
        return
    
    # Non-interactive mode for document analysis
    if args.file:
        assistant.analyze_document(args.file, args.document_query)
        return
    
    # Interactive mode
    assistant.run()

if __name__ == "__main__":
    main()