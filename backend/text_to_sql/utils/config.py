from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from typing import Dict

# Generation Configuration
GENERATION_CONFIG = genai.GenerationConfig(temperature=0, top_p=0)

# Safety Configurations
SAFETY_CONFIGS: Dict[str, str] = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

# Database Query Dialect
QUERY_DIALECT = "Microsoft Postgres SQL Server"  # or "SQLite SQL Server"