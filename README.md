# Bank Policy Assistant

A simple GenAI RAG app for banking customer support.

## Problem

Support agents waste a lot of time searching long policy documents. A customer asks one small question, and the agent has to open many pages to find the right line. This makes the work slow and it can lead to wrong answers.

## Solution

This app lets an agent ask a question in plain words. It searches small policy files and returns a clear answer with the source file name. The agent can read the answer fast and can also check the source.

## Features

The app loads policy text files from the data folder and splits them into short parts. It finds the best part for a question with TF-IDF search, so it runs with no API key. It shows the answer and the source on one clean page. It also has a place in the code where a real LLM can be added later with an API key.

## Tech Stack

The backend is Python and it uses only the standard library, so there is no install step to run it. The frontend is one HTML page with plain JavaScript and CSS. The search uses the RAG idea, which means it first finds the right text and then uses that text as the answer source. The code is LLM ready, with an optional hook for Claude or OpenAI through an environment variable.

## How to Run

Step 1. Open a terminal in this project folder.

Step 2. Run the server with this command: python3 app.py

Step 3. Open this link in your browser: http://127.0.0.1:8000

Step 4. Type a question and click Ask. For example, ask what happens if a customer does not know a charge on the card.

You can also test the search from the command line with no server. Run: python3 rag.py "How long does a customer have to raise a dispute?"

## Sample Data

All files in the data folder are sample data created for this demo. They are written in simple English for learning. They are not real bank data and they are not data from any real customer or company.

## Project Structure

The app.py file is the server and it serves the page and the API. The rag.py file has the search logic and the optional LLM hook. The data folder has three sample policy files for card payments, account opening, and dispute and fraud. The static folder has the frontend page in index.html.

## Future Work

In a next version, the app can use real embeddings for better search. It can also use a real LLM to write the answer in a more natural way, while still showing the source. Login, access control, and a log of asked questions can be added for real team use.
