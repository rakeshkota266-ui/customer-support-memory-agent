import os
import asyncio

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

load_dotenv(override=True)

app = Flask(__name__)

BANK_ID = os.getenv("HINDSIGHT_BANK_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    customer_name = data.get("customer_name", "Customer").strip()
    message = data.get("message", "").strip()

    async def process():

        client = Hindsight(
            base_url=os.getenv("HINDSIGHT_BASE_URL"),
            api_key=os.getenv("HINDSIGHT_API_KEY")
        )

        groq_client = Groq(api_key=GROQ_API_KEY)

        memories = []

        # -----------------------------------------
        # CLASSIFY QUESTION
        # -----------------------------------------

        classification = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """
Classify this user message.

Reply with ONLY one word:

SUPPORT
or
GENERAL

SUPPORT = a customer's personal support problem,
such as Wi-Fi not working, router problems,
account problems, device troubleshooting,
software errors, order problems, or asking
what solution was used previously.

GENERAL = general knowledge, current affairs,
politics, geography, education, mathematics,
product prices, latest products, latest news,
current information, today's information,
or questions asking what exists or is available now.

IMPORTANT:
If the message contains words such as
"current", "latest", "today", "now", "price",
"available", "who is", or "what is the latest",
classify it as GENERAL.

Examples:
"My Wi-Fi keeps disconnecting" = SUPPORT
"What did we do about my Wi-Fi last time?" = SUPPORT
"What is the current iPhone price?" = GENERAL
"Does iPhone 18 Pro exist?" = GENERAL
"Who is the CM of Telangana?" = GENERAL
"What is the capital of France?" = GENERAL
"""
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        category = classification.choices[0].message.content.strip().upper()

        # -----------------------------------------
        # CUSTOMER SUPPORT
        # -----------------------------------------

        if category == "SUPPORT":

            result = await client.arecall(
                bank_id=BANK_ID,
                query=f"""
Customer: {customer_name}

Current support issue:
{message}

Return only memories directly relevant to this
customer's current support issue.
"""
            )

            memories = [
                memory.text
                for memory in result.results
                if customer_name.lower() in memory.text.lower()
            ]

            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a customer support memory agent.

Answer the current customer problem.

Use previous memories only when they are
directly relevant.

Never use unrelated memories.

Never invent previous actions.

Give practical troubleshooting steps.
"""
                    },
                    {
                        "role": "user",
                        "content": f"""
Customer:
{customer_name}

Current issue:
{message}

Relevant previous memories:
{memories}

Answer the customer.
"""
                    }
                ]
            )

            ai_response = response.choices[0].message.content

            # Save only support interactions
            await client.aretain(
                bank_id=BANK_ID,
                content=f"""
Customer: {customer_name}

Support Issue:
{message}

AI Support Solution:
{ai_response}
"""
            )

        # -----------------------------------------
        # GENERAL / CURRENT QUESTION
        # -----------------------------------------

        else:

            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a current-information assistant.

The user is asking a general or potentially
time-sensitive question.

You MUST use browser search before answering.

Use the browser-search information as the
primary source for your answer.

For current facts, prefer official sources.

Do NOT use customer-support memories.

Do NOT save this question into Hindsight.

Give the answer directly and clearly.
"""
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                tools=[
                    {
                        "type": "browser_search"
                    }
                ],
                tool_choice="required"
            )

            ai_response = response.choices[0].message.content

        client.close()

        return category, memories, ai_response

    category, memories, ai_response = asyncio.run(process())

    return jsonify({
        "customer": customer_name,
        "message": message,
        "category": category,
        "recalled_memories": memories,
        "ai_response": ai_response
    })


if __name__ == "__main__":
    app.run(debug=True)