# Brainwave
Repository used for the submission as per the evaluation criteria specified by the AIMS-DTU team for the Brainwave'26 Hackathon

🧠 Whistle — Emotion-Aware Agentic AI Assistant

A brAInwave Hackathon Project

Whistle is a speech-first, emotion-aware, agentic AI personal assistant designed to go beyond traditional chatbots.
It not only converses naturally with users but can also understand intent, adapt behavior based on emotion, and safely take actions on the user’s behalf inside the browser.

This project is being developed as part of the brAInwave AI Hackathon (Open Innovation Track).

🚀 Vision

Most AI assistants today either:

Talk well but cannot act, or

Act blindly without understanding human emotion

Whistle bridges this gap by combining:

Conversational intelligence

Emotion-aware behavior

Agentic tool orchestration

Safe, explainable browser interaction

✨ Key Features

🎙️ Speech-First Interaction
Natural voice conversation with optional text input fallback.

🧠 Emotion-Aware Intelligence
Detects user emotion from language and speech features and adapts:

Response tone

Decision making

Action aggressiveness

🧩 Agentic Architecture (LangGraph)
Uses a state-driven workflow for:

Intent understanding

Emotion assessment

Action planning

Tool execution

🌐 Browser-Level Autonomy (Safe by Design)
Reads and interacts with web pages using DOM & accessibility data
(No fragile computer vision or screen scraping).

🔍 Explainable & Human-Aligned Actions
Every action is planned, validated, and explained before execution.

Phase 1 — Personalized Agentic Core (Current Focus)

At the current stage, our primary focus is on building Whistle as a highly capable, personalized agent that can:

Understand user intent through natural conversation

Adapt behavior based on detected emotional state

Orchestrate complex tasks using predefined tools

Execute multi-step workflows reliably and safely

In this phase, Whistle can:

Use tools such as Gmail, Calendar, and Slack

Define custom task flows composed of multiple tool actions

Schedule tasks for specific times or recurring intervals

Trigger predefined workflows using custom trigger words or phrases

Maintain structured task graphs (flowcharts) for repeatable execution

The goal of this phase is to ensure Whistle functions as a dependable, intelligent task orchestrator, capable of handling real productivity workflows before expanding its autonomy.

Phase 2 — Browser Agent Capabilities (In Progress / Target Phase)

In parallel, we are actively working toward enabling Browser Agent functionality, where Whistle will be able to:

Read and understand web pages using DOM and accessibility data

Identify actionable elements such as buttons, inputs, and links

Perform safe, validated browser actions (click, type, navigate)

Explain actions before and after execution to maintain transparency

This phase represents the transition from:

“An assistant that can coordinate tools”
to
“An agent that can directly operate within the browser on the user’s behalf.”

🧠 Cognitive Core (LangGraph)

Whistle’s intelligence is implemented as a state machine, not a single prompt:

Intent Interpretation

Emotion Assessment

Context & Memory Update

Action Planning

Decision: Talk or Act

Execution + Explanation

This ensures predictable, safe, and controllable agent behavior.

🤖 LLM Choice

Primary LLM: Local LLM via Ollama

Recommended Model: LLaMA 3.1 8B Instruct

Role Separation (Same Model):

Conversational role (user-facing)

Orchestrator role (LangGraph agent)

This keeps the system:

Fast

Offline-capable

Demo-safe

Fully controllable

🌐 Browser Agent (USP)

Whistle does not use computer vision to understand the screen.

Instead, it:

Reads visible elements via DOM & ARIA

Identifies buttons, inputs, and links

Executes validated actions (click, type, navigate)

Requests confirmation for sensitive actions

This makes browser interaction:

Faster

More reliable

More explainable

🧰 Tech Stack

Python

LangGraph — agentic workflow orchestration

Ollama — local LLM inference

Whisper / Web Speech API — speech-to-text

Neural / Browser TTS — text-to-speech

JavaScript (Browser Extension) — screen reading & actions

HTML / CSS — UI

📂 Project Status

🚧 Work in Progress

This repository currently contains:

Initial orchestration logic

Early LangGraph setup

Foundational components for speech and agent flow

Planned next steps:

Complete browser agent integration

Finalize emotion assessment pipeline

End-to-end demo flow

UI polish for hackathon presentation

🎯 Hackathon Focus

This project prioritizes:

Clear system design

Explainability and safety

Feasible scope for a hackathon

Strong demo-ability

👥 Team

Built by Agentic Labs
for the brAInwave AI Hackathon

📌 Disclaimer

This project is a prototype built for hackathon demonstration purposes.
It is not intended for production use without further security, privacy, and robustness improvements.

⭐ If You’re a Judge or Mentor

Thank you for taking the time to review Whistle.
We’re happy to walk you through:

The cognitive core

Emotion-aware decision making

Browser agent safety design
