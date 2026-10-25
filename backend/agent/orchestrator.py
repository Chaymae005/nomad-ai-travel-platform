"""
agent/orchestrator.py

Le cœur de l'agent : reçoit la question de l'utilisateur, décide (via Gemini)
quel(s) tool(s) appeler parmi les tools voyage disponibles, exécute
réellement ces tools, et renvoie une réponse finale justifiée.
"""

from google.genai import types
from gemini.client import send_message
from agent.tool_definitions import AVAILABLE_TOOLS
from agent.tools_external import get_weather, get_country_info, get_wikipedia_summary
from agent.rag import search_rag

TOUTES_LES_FONCTIONS = {
    "get_weather": get_weather,
    "get_country_info": get_country_info,
    "search_rag": search_rag,
    "get_wikipedia_summary": get_wikipedia_summary,
}

INSTRUCTION_BASE = (
    "Tu es un assistant voyage sympathique et compétent, qui discute "
    "naturellement avec l'utilisateur, comme un ami connaisseur qui a "
    "beaucoup voyagé. Réponds de façon claire, chaleureuse et concise "
    "-- va à l'essentiel, évite les réponses trop longues ou formatées "
    "comme un rapport.\n\n"
    "Règle importante : ne jamais inventer une donnée factuelle "
    "(météo, chiffres, faits précis) -- base-toi uniquement sur ce que "
    "les outils disponibles retournent réellement. Si tu n'as pas "
    "l'information exacte, dis-le simplement et naturellement, sans "
    "formule figée.\n\n"
    "N'utilise pas de formatage markdown lourd (pas de listes à puces "
    "systématiques, pas de titres, pas de gras excessif) -- écris en "
    "phrases naturelles comme dans une vraie conversation. Si "
    "get_country_info retourne un drapeau ou un lien vers une carte, "
    "tu peux les mentionner brièvement en fin de réponse si c'est "
    "utile, sans les imposer systématiquement."
)


def ask_agent(user_question: str, history: list = None) -> tuple[str, list]:
    contents = list(history) if history else []
    contents.append(types.Content(role="user", parts=[types.Part(text=user_question)]))

    while True:
        response = send_message(
            contents=contents,
            usage="agent",
            tools=AVAILABLE_TOOLS,
            system_instruction=INSTRUCTION_BASE,
        )

        candidate = response.candidates[0]
        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call
        ]

        if not function_calls:
            contents.append(candidate.content)
            return response.text, contents

        contents.append(candidate.content)

        tool_response_parts = []
        for call in function_calls:
            func = TOUTES_LES_FONCTIONS.get(call.name)
            result = {"error": f"Tool inconnu : {call.name}"} if func is None else func(**call.args)
            tool_response_parts.append(
                types.Part.from_function_response(name=call.name, response=result)
            )

        contents.append(types.Content(role="user", parts=tool_response_parts))