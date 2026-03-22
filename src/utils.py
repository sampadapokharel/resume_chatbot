import re
from openai import OpenAI

client = OpenAI()

NAME_PATTERN = re.compile(r"\b(sampada|pokharel|she|her)\b", re.IGNORECASE)
SMALLTALK_PATTERN = re.compile(
    r"^\s*(hi|hello|hey|howdy|how are you|how('s| is) it going|what'?s up|good (morning|afternoon|evening)|thanks|thank you|bye|goodbye)\s*[!?.]*\s*$",
    re.IGNORECASE
)


def load_prompt(filename: str, replacements: dict = None) -> str:
    with open(f"prompts/{filename}", "r") as f:
        text = f.read()
    if replacements:
        for key, value in replacements.items():
            text = text.replace(key, value)
    return text


def strip_name_references(text: str) -> str:
    return re.sub(r"[^\w\s]", "", NAME_PATTERN.sub("", text)).strip()


def is_smalltalk(question: str) -> bool:
    return bool(SMALLTALK_PATTERN.match(question))


def is_task_question(question: str, classifier_prompt: str) -> bool:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": classifier_prompt},
            {"role": "user", "content": question}
        ],
        max_tokens=5,
        temperature=0
    )
    return response.choices[0].message.content.strip().upper() == "OFF_TOPIC"
