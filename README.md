# Agentic Content Finder

## What is it?
This project is an experiment in working with Large Language Models (LLMs) and an agentic approach to problem-solving. The goal is to create an automatic filtering and recommendation service that periodically scans the internet (daily or weekly) for content that may be interesting or relevant to me. In short, it functions like an on-demand recommendation system capable of working with any type of online content.

## Why?
The idea started with everyday situations:
- A friend once invited me to a silent disco event that was happening in just a few hours. I realised I would have liked to know about it sooner.
- Another time I wanted to buy a second-hand tablet with at least 8GB of RAM, but most sellers didn’t even know what RAM was.

These situations highlighted the need for a system that can automatically scan, filter, and understand information on my behalf.

## How?
The system is designed as an agentic pipeline capable of:
- Checking upcoming events in the area
- Scanning listings or offers that match my interests
- Understanding device specifications (e.g., verifying RAM capacity)
- Applying my personal preferences and goals to filter results

LLMs enable semantic understanding of unstructured content on the internet, which is essential for this type of intelligent filtering.

## Technology
- **LangChain** – used to build an agentic pipeline that partially integrates with the OLX.pl platform.
- **Open-source LLMs** – models running locally on my machine, exposed via a custom API.
- This is an early prototype; functionality is limited as the project was developed alongside my master's thesis.

More updates will come as the system evolves.
