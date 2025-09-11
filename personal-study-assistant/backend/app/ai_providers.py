import os

# OpenAI client
try:
	import openai
except Exception:
	openai = None

# Google Generative AI (Gemini) client
try:
	import google.generativeai as ggen
except Exception:
	ggen = None

class BaseProvider:
	def generate(self, prompt: str, mode: str = "chat") -> str:
		raise NotImplementedError

class OpenAIProvider(BaseProvider):
	def __init__(self):
		api_key = os.getenv("OPENAI_API_KEY")
		if not api_key:
			raise RuntimeError("OPENAI_API_KEY not set")
		if not openai:
			raise RuntimeError("openai package not installed")
		openai.api_key = api_key

	def generate(self, prompt: str, mode: str = "chat") -> str:
		# Simple ChatCompletion call; adjust model as needed.
		model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
		resp = openai.ChatCompletion.create(
			model=model,
			messages=[{"role": "user", "content": prompt}],
			max_tokens=600,
		)
		return resp.choices[0].message.content.strip()

class GeminiProvider(BaseProvider):
	def __init__(self):
		# Google Generative AI uses GOOGLE_API_KEY or service account credentials
		if ggen is None:
			raise RuntimeError("google.generativeai package not installed")
		api_key = os.getenv("GOOGLE_API_KEY")
		# if using service account, set GOOGLE_APPLICATION_CREDENTIALS
		if not api_key and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
			raise RuntimeError("Either GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS must be set")
		if api_key:
			ggen.configure(api_key=api_key)
		else:
			# library will pick up credentials from env
			pass

	def generate(self, prompt: str, mode: str = "chat") -> str:
		model = os.getenv("GOOGLE_GEMINI_MODEL", "models/text-bison-001")
		# simple example using text generation
		response = ggen.generate_text(model=model, prompt=prompt, max_output_tokens=600)
		return response.text