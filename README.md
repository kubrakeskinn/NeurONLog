# 🧠 NeurONLog - LLM-Powered Error Log Debugger for Intel Toolchains

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Intel oneAPI](https://img.shields.io/badge/Intel-oneAPI-orange.svg)](https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html)
---

## 🚀 Overview

**NeurONLog** is a hybrid AI system designed to analyze low-level system logs and C/C++ code, transforming them into **structured, explainable failure reasoning**.

It combines:

* 🧠 **Large Language Models (LLMs)** for semantic understanding
* ⚙️ **Symbolic reasoning (rule-based / Datalog)** for deterministic analysis
* 🔍 **Static analysis principles** for root cause detection

> 🎯 Goal: Convert opaque system errors into actionable engineering insights.

---

## 🔥 Key Features

### 🧠 AI-Powered Log Understanding

* Parses raw compiler/runtime logs
* Extracts semantic meaning from unstructured error messages
* Identifies failure patterns

---

### ⚙️ Symbolic Reasoning Engine

* Transforms extracted data into structured facts
* Applies rule-based inference for deterministic reasoning
* Tracks failure propagation chains

---

### 🔍 Root Cause Analysis

Detects and explains:

* Segmentation faults
* Memory access violations
* Pointer misuse
* Toolchain-specific errors (Intel, SYCL, GPU)

---

### 📊 Explainable Outputs

Each analysis provides:

* ✅ Error classification
* 📈 Confidence score
* 🔴 Severity level
* 🔗 Reasoning path
* 🛠️ Actionable fix suggestions

---

## 🧪 Demo

### ▶️ Input

```bash
python main.py -i "fatal error: segmentation fault in pointer dereference"
```

---

### 📤 Output

```text
Type: Segmentation Fault
Severity: CRITICAL
Confidence: 88%

Root Cause:
Invalid pointer dereference

Explanation Path:
log → runtime failure → memory violation → segfault

Suggested Fix:
- Check null pointers
- Validate memory boundaries
- Debug with gdb / valgrind
```

---

## 🧱 System Architecture

```text
                ┌──────────────────────────┐
                │  Input Layer             │
                │  (Logs / C / C++ Code)   │
                └────────────┬─────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────┐
        │  1. Semantic Extraction (LLM)       │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  2. Fact Generation Layer           │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  3. Symbolic Reasoning Engine       │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  4. Explanation Generator           │
        └─────────────────────────────────────┘
```

---

## ⚙️ Installation

```bash
git clone https://github.com/kubrakeskinn/NeurONLog
cd NeurONLog

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

---

## ▶️ Usage

### 1. Direct Input

```bash
python main.py -i "your error message"
```

### 2. File Input

```bash
python main.py -f error.log
```

### 3. Pipe Input

```bash
type error.log | python main.py
```

---

## 🧩 Use Cases

* 🛡️ Defense software debugging
* ⚙️ Compiler/toolchain error analysis
* 🚀 Embedded systems diagnostics
* 🧪 Pre-deployment failure analysis

---
## 🛠️ Tech Stack

* Python
* LLM APIs (Claude / OpenAI)
* Rule-based inference engine
* Tree-sitter (planned / optional)
* Datalog (planned extension)
---
## 📄 License

MIT License
