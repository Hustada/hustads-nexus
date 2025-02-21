# 🧠 AI Scientific Hypothesis Generator

## Overview
An advanced AI-powered research assistant that dynamically generates, reflects upon, and evaluates scientific hypotheses using multi-agent interactions and language models.

![Project Banner](docs/banner.png)

## 🚀 Key Features
- Dynamic scientific hypothesis generation
- Multi-agent research exploration
- Real-time progress tracking
- Iterative research cycles
- Cross-domain research support

## 🔬 How It Works
The AI Scientific Hypothesis Generator uses a sophisticated multi-agent system to explore research questions:

1. **Hypothesis Generation**: Create initial scientific hypotheses using Gemini AI
2. **Web Research Integration**: Dynamically enrich hypotheses with real-time web and academic research
   - Leverages SerpAPI for comprehensive web searches
   - Retrieves recent scientific publications from arXiv
   - Provides contextual insights and current research trends
3. **Hypothesis Reflection**: Critically analyze generated hypotheses
4. **Hypothesis Ranking**: Evaluate hypotheses based on scientific merit
5. **Iterative Refinement**: Progressively improve research insights

### Research Iteration Workflow
- Users can select 1-5 research iterations
- Each iteration explores the research goal from different perspectives
- Generates comprehensive, nuanced research insights

### Research Capabilities
- Real-time web and academic research integration
- Multi-source intelligence gathering
- Adaptive research exploration
- Cross-domain knowledge synthesis

## 💻 Technology Stack
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **Backend**: Python, Flask
- **AI Components**: 
  * Multi-agent language model interactions
  * Gemini AI for hypothesis generation
  * Web research agent with SerpAPI integration
- **Research Tools**:
  * arXiv API integration
  * Dynamic web search capabilities
- **Event Streaming**: Server-Sent Events (SSE)

## 🛠 Setup and Installation

### Prerequisites
- Python 3.10+
- pip
- Virtual environment recommended

### Installation Steps
1. Clone the repository
```bash
git clone https://github.com/Hustada/hustads-nexus.git
cd ai_co_scientist
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python app.py
```

## 🔍 Usage

### Research Goal Input
- Enter a scientific research objective
- Select from pre-defined research questions
- Choose number of research iterations (1-5)

### Example Research Questions
- Biology: "How do epigenetic modifications influence neurodegenerative diseases?"
- Physics: "What quantum mechanisms might explain dark matter interactions?"

## 🌟 Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🔮 Future Roadmap
- Expand research domain coverage
- Enhance multi-agent interaction models
- Implement more advanced hypothesis generation techniques
- Add visualization of research insights

## 📞 Contact
Mark Hustad - [Your Email/LinkedIn]

**Powered by cutting-edge AI research and innovation**
