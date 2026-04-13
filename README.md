# AgentDroid

AgentDroid is an open-source AI agent framework focused on Android app control, Android emulator automation, and mobile-engineering workflows.

I first created this framework for my personal use while working on a large-scale Android app to automate user flows, UI/UX consistency, and end-to-end behavioral testing. Recently, I enhanced it by integrating concepts and routing from [claw-code](https://github.com/ultraworkers/claw-code).

It transforms your computer into an AI-powered control center for Android, supporting everything from natural language automation to advanced debugging and script generation.

---

## 🚀 What AgentDroid can do for your Android project

AgentDroid is designed to handle the most tedious parts of Android development and QA. Here is how it can supercharge your project:

- **Multi-Model Intelligence**: Native support for **Gemini 2.0**, **Ollama (local)**, and various AI CLIs (**Codex, Qwen, OpenCode**). You aren't locked into one model; use the best "brain" for your specific task.
- **Vision-Based Reasoning**: Most automation tools fail on "flat" UI hierarchies (like Flutter, Compose, or Games). AgentDroid captures and analyzes real-time **screenshots** using Computer Vision, allowing it to "see" icons, images, and custom elements that have no XML text labels.
- **The Script-Writer (Appium Code Gen)**: Transform AI-driven exploration into permanent code. Once the agent successfully completes a task, it can export the entire flow as a production-ready **Appium Python script**. This allows you to use AI for discovery and standard code for your CI/CD pipeline.
- **Deep-Link Teleportation**: Stop wasting tokens and time clicking through 10 screens. AgentDroid automatically scans your app's manifest via `dumpsys` to discover hidden **Intent Filters** and **Deep Links**, allowing it to "teleport" instantly to specific Activities.
- **Self-Healing Tests**: End the "broken test" nightmare. If an existing test script fails due to a UI change (like a renamed ID), the AgentDroid **Healing Agent** runs the script, captures the crash, analyzes the visual state, and proposes the exact code fix to restore your test suite.
- **Layout Inspector & Mirroring**: Deep-dive into UI bugs with a single command. It toggles "Show Layout Bounds" on the physical device and launches a high-performance `scrcpy` mirror, giving engineers a "skeleton view" of the app layout on their desktop.
- **Action Recorder**: Record complex manual sequences on a physical device and save them as reusable **AI Skills**. You can "show" the agent how to perform a corporate login flow once, and it will remember how to do it forever.
- **MCP Native**: Fully compatible with the **Model Context Protocol**, turning your Android phone into a set of native tools inside **Claude Code**, **Gemini**, and **Codex**.

---

## 📈 Engineering Output & Resource Sufficiency

AgentDroid is engineered for professional environments where time is the most expensive resource and token efficiency is critical. It moves beyond simple "prompt-and-wait" testing to a highly sufficient, autonomous framework:

- **Exponential Output Increase**: Stop writing boilerplate. By converting natural language goals into production-ready **Appium/Pytest code**, AgentDroid allows a single engineer to build and maintain a massive test suite in a fraction of the time. It handles the "how" (selectors, waits, transitions), so you focus on the "what" (user value).
- **80% Lower Token Consumption**: Prompt-based testing is notoriously expensive, as models must "scan" and "think" through every screen transition. AgentDroid's **Deep-Link Teleportation** bypasses manual navigation entirely. By jumping directly to the target Activity, it eliminates redundant reasoning steps, saving up to **80% in token costs** per task.
- **Sufficient Self-Correction**: Traditional agents fail silently or get stuck in loops. AgentDroid's **Vision-First Healing** and **Logcat Sentinel** provide a sufficient "immune system" for your automation. It doesn't just report a failure; it analyzes the visual delta and log signatures to provide an immediate fix, keeping your pipelines green without human intervention.
- **Cognitive Offloading via Reusable Skills**: Use the AI for the hard part—discovery. Once a complex path is identified, save it as a **Skill**. Subsequent runs execute with zero-token overhead for those segments, ensuring your automation is both high-speed and cost-predictable.

---

## 📥 Installation

You can install AgentDroid tools into your favorite AI environment.

### 1. Gemini CLI (Native Extension)
```bash
gemini extension install https://github.com/dcdhameliya/AgentDroid
```

### 2. OpenAI Codex CLI (MCP)
Codex does not use the old `/plugins install` command. Register AgentDroid as an MCP server from a local checkout:
```bash
git clone https://github.com/dcdhameliya/AgentDroid
cd AgentDroid
python3 -m venv .venv
.venv/bin/pip install -e .
codex mcp add agentdroid --env PYTHONPATH="$(pwd)" -- "$(pwd)/.venv/bin/python" -m agentdroid_mcp.server
codex mcp get agentdroid
```

### 3. Qwen CLI (Native Extension)
```bash
qwen extension add https://github.com/dcdhameliya/AgentDroid -y
```

### 4. Oh-My-OpenAgent (OpenCode CLI)
```bash
opencode plugin https://github.com/dcdhameliya/AgentDroid
```

### 5. Claude Code (MCP)
Ask Claude:
`"Install the MCP server from https://github.com/dcdhameliya/AgentDroid"`

---

## 📖 Detailed Examples & Prompts

### 1. Autonomous Task Execution
**Command**: `agentdroid run "task" --provider gemini`
*   **Prompt**: `"Open the Settings app, find the 'Battery' section, and tell me the current percentage."`
*   **Description**: The agent will launch the settings app, use its **Vision** to find the Battery menu (even if the XML ID is obscure), click through, and report the status back to the CLI.

### 2. Exporting AI Flows to Code (Production Automation)
**Command**: `agentdroid run "task" --export <filename>.py`
*   **Prompt**: `"Navigate to the profile screen, change the username to 'AgentDroidUser', and save."`
*   **Description**: After the AI successfully navigates and saves the name, it will generate a file (e.g., `update_profile.py`) containing the **Appium Python** code needed to repeat this action in an automated test suite.

### 3. UI/UX Consistency & Accessibility Audit
**Command**: `agentdroid run "audit screen"`
*   **Prompt**: `"Analyze the current screen for UI inconsistencies. Check if all buttons have content descriptions and if the color contrast of the 'Login' button looks correct."`
*   **Description**: The agent captures a screenshot and XML, then uses its **Vision Reasoning** to perform a heuristic audit. It identifies "missing contentDescription" in the XML and "low contrast" from the image, providing a detailed engineering report.

### 4. Zero-Cost Local Engineering (Ollama)
**Command**: `agentdroid run "task" --local --model llama3`
*   **Prompt**: `"Clear the cache for the 'Chrome' app and restart it."`
*   **Description**: This workflow runs entirely on your local machine using **Ollama**. No data leaves your network, and no API tokens are consumed. It's the perfect sufficient tool for internal corporate apps with sensitive data.

### 5. Advanced Hybrid Routing (Claw-Code Integration)
**Command**: `agentdroid claw-run "Find the deep link for the advanced display settings"`
*   **Description**: This uses the **claw-code** integration to first route the high-level intent through a sophisticated planning layer. It breaks down the task into "Discover Manifest -> Verify Activity -> Teleport", ensuring the most direct and token-efficient path is taken.

### 6. Self-Healing a Broken Script
**Command**: `agentdroid heal path/to/my_test.py`
*   **Description**: If `my_test.py` crashes because a button moved or an ID changed, the Healing Agent will run the script, capture the `NoSuchElementException`, take a screenshot of the current screen, and say: *"I see the 'Submit' button now has ID 'btn_login_v2' instead of 'login_button'. Here is the fix..."*

### 7. Engineering Layout Inspection (Visual Debugging)
**Command**: `agentdroid inspect`
*   **Description**: This command is for human engineers. It instantly turns on "Show Layout Bounds" on your phone and opens a `scrcpy` window. You can see the margins, padding, and alignment of every UI component in real-time. Press **Enter** in the terminal to turn it off and clean up.

---

## 🛠️ Manual Installation (For Local Dev)

### Prerequisites
- **Python 3.10+**
- **Android SDK Platform-Tools** (`adb`)
- **scrcpy** (optional, for screen mirroring: `brew install scrcpy`)

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/dcdhameliya/AgentDroid.git
   cd AgentDroid
   ```

2. **Initialize Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

---

## 📂 Project Structure
- `cli/`: Main entry point.
- `integrations/`: Manifests and plugins for AI CLIs (Codex, OmO, MCP).
- `agent/`: Autonomous runtime, self-healing, and vision logic.
- `android/`: ADB wrappers and manifest analysis.
- `mcp/`: Claude/Gemini-compatible MCP server.
- `tools/`: Script writers, recorders, and teleportation tools.
- `vendor/`: Integrated libraries (including Claw-Code).

## 📄 License

Copyright (C) 2026 dcdhameliya - Licensed under [GPL-3.0](LICENSE.txt)
