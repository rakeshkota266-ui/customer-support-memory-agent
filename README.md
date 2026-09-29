# Customer Support Memory Agent

An AI-powered customer support agent that remembers previous customer issues and solutions using Hindsight.

## Problem

Customers often become frustrated when they have to repeat the same issue every time they contact customer support.

## Solution

The Customer Support Memory Agent uses long-term memory to remember previous customer interactions.

When a customer returns with a similar issue, the agent recalls relevant information and provides a more personalized response.

## How It Works

1. Customer enters their name and support issue.
2. Flask receives the request.
3. Hindsight recalls relevant customer memories.
4. Groq with GPT-OSS 120B generates the support response.
5. The interaction and solution are stored in Hindsight.
6. On future interactions, relevant memories are recalled.

## Technology Stack

- Python
- Flask
- Hindsight
- Groq
- GPT-OSS 120B
- HTML
- CSS
- JavaScript

## Memory Demonstration

### First Interaction

Customer:

> My Wi-Fi disconnects every evening.

The agent provides troubleshooting steps and stores the interaction.

### Later Interaction

Customer:

> My Wi-Fi is disconnecting again. What did we do last time?

The agent recalls the previous support interaction and uses that information to provide a personalized response.

## Architecture

Customer  
↓  
Web Interface  
↓  
Flask Backend  
↓  
Hindsight Memory + Groq AI  
↓  
Personalized Support Response  
↓  
Customer

## Hindsight Usage

Hindsight is the central memory layer of the application.

It is used to:

- Retain customer support interactions
- Recall previous customer issues
- Recall previous solutions
- Provide personalized support based on customer history

## Security

API keys are stored in a local `.env` file and are excluded from the GitHub repository using `.gitignore`.

## Project Structure

```text
customer-support-memory-agent/
│
├── app.py
├── requirements.txt
├── test_hindsight.py
├── .gitignore
│
└── templates/
    └── index.html
