# 🎓 LectureLab - YouTube Lecture to Study Kit

LectureLab is an AI-powered EdTech web application built with Streamlit and Gemini Video Understanding. It converts public YouTube lectures into structured notes, interactive revision flashcards, self-grading quizzes, and execution usage logs.

## 🌟 Features
- Multimodal video analysis directly from YouTube URLs.
- JSON schema structured output parsing.
- Interactive flashcard deck with flip and loop navigation.
- Python-checked auto-graded quizzes with full explanations.
- Token consumption and response latency tracking panel.

## 🚀 How to Run Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/atharvabarge2008/Lecturelab.git
   cd Lecturelab
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your key into `.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## 🌐 Live Application
[LectureLab Streamlit App](https://lecturelab-atharvabarge.streamlit.app)
