# AI Resume Tailor

Streamlit + OpenAI GPT + RenderCV.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Or without activation:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The user enters their own OpenAI API key in the UI. The app does not write it to project files.

The single default prompt is `prompts/prompt_template_aih.txt`.
The single RenderCV base template is `templates/base_resume.yaml`.

For deployment, push the repository to GitHub and deploy `app.py` on Streamlit Community Cloud.

## Demo
https://kmlnyk-ai-resumetailor.streamlit.app/