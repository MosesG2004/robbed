# Proteus

A hacker-style web application that translates simple English programming instructions into executable Python code and visually demonstrates how a computer interprets the instructions.

![Proteus](https://img.shields.io/badge/Proteus-English→Python-00ff41?style=for-the-badge&labelColor=0d0d0d)

## Features

- **English to Python translation** — write instructions in plain English, see them converted to Python in real-time
- **AI-powered fallback** — commands the regex engine can't handle are translated by Claude (Haiku 4.5), so you can write _any_ English instruction
- **Live execution** — run your programs and see output instantly
- **Variable memory tracking** — watch variables change as your program executes
- **Cyberpunk terminal UI** — dark hacker aesthetic with neon green glow effects and smooth animations
- **Step-by-step animation** — parsing, translating, and executing phases with visual feedback

## Supported Commands

| English | Python |
|---------|--------|
| `set x to 5` | `x = 5` |
| `print x` | `print(x)` |
| `repeat 3 times` | `for _i in range(3):` |
| `add 2 to x` | `x += 2` |
| `subtract 1 from x` | `x -= 1` |
| `multiply x by 3` | `x *= 3` |
| `divide x by 2` | `x /= 2` |
| `if x is 5` | `if x == 5:` |
| `if x is greater than 10` | `if x > 10:` |
| `if x is less than 10` | `if x < 10:` |
| `create list names with Alice, Bob, Eve` | `names = ["Alice", "Bob", "Eve"]` |
| `find shortest in names` | `print(min(names, key=len))` |
| `find longest in names` | `print(max(names, key=len))` |
| `find smallest in nums` | `print(min(nums))` |
| `find largest in nums` | `print(max(nums))` |
| `for each item in mylist` | `for item in mylist:` |
| `sort mylist` | `mylist.sort()` |
| `sort mylist in descending order` | `mylist.sort(reverse=True)` |
| `output x` / `show x` / `display x` | `print(x)` |
| `while x is less than 10` | `while x < 10:` |
| `get item 0 from mylist` | `print(mylist[0])` |
| `store shortest in names as result` | `result = min(names, key=len)` |

### Block Handling

Lines after `repeat`, `for each`, `while`, and `if` are automatically indented. A blank line closes the block.

```
set x to 0
repeat 5 times
add 1 to x
print x

print "done"
```

## Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm**

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Positivitty/proteus.git
cd proteus
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. (Optional) Enable AI mode

To translate _any_ English instruction (not just built-in patterns), add your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and add your key from https://console.anthropic.com/settings/keys
```

Without a key, the app still works using the built-in regex patterns. With a key, unrecognized commands are sent to Claude Haiku (~$0.0005 per call).

### 4. Start the backend

```bash
uvicorn main:app --reload
```

The API server runs at `http://localhost:8000`.

### 5. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:3000`.

## Project Structure

```
proteus/
├── backend/
│   ├── main.py              # FastAPI app with /parse, /translate, /run endpoints
│   ├── interpreter.py        # English-to-Python translator (regex + AI fallback)
│   ├── executor.py           # Safe Python execution sandbox
│   ├── requirements.txt
│   └── .env.example          # API key template
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main 4-panel layout
│   │   ├── hooks/
│   │   │   └── useProteus.js # State management and API integration
│   │   └── components/
│   │       ├── Header.jsx         # Title bar and run button
│   │       ├── HumanTerminal.jsx  # CodeMirror English input editor
│   │       ├── PythonPanel.jsx    # Translated Python display
│   │       ├── VariableMemory.jsx # Variable state tracker
│   │       ├── OutputConsole.jsx  # Terminal output display
│   │       └── PanelWrapper.jsx   # Reusable panel frame
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── README.md
```

## Tech Stack

- **Backend:** Python, FastAPI, Anthropic SDK (Claude Haiku 4.5)
- **Frontend:** React, Vite, Tailwind CSS v4, Framer Motion, CodeMirror
