import json
from openai import OpenAI

def build_prompt(old_cv, jd, country, template):
   return f"""
Step 1: Please read and remember my OLD CV (pasted below). DO NOT rewrite yet. Just understand my experience, roles, and achievements.
{template}

<OLD_CV>
{old_cv}
</OLD_CV>

---

=====================================================
STEP 2: ANALYZE THE JOB DESCRIPTION
=====================================================

🔹 Step 2: Here is the Job Description (JD) for the role I am applying for. Use this to guide everything:

<JOB_DESCRIPTION>
{jd}
</JOB_DESCRIPTION>

---
 Step 3: Now write a clean, ATS-optimized resume for this country:
 Target Country: 
 <COUNTRY>
{country}
</COUNTRY>

If the target country is not explicitly listed, follow that country’s common resume style. 
When unsure, default to a clean EU-style resume.

Write the resume like you’re helping me get shortlisted for this exact job — not just pass ATS.

Make sure keywords, tone, and style match hiring patterns in that region.
# Instructions:
  - Study the JD and pull out keywords, tools, responsibilities, and soft skills.
  - Use simple, confident language — no robotic phrases or fluff.
  - Every bullet point should show value, outcome, or measurable result.
Use metrics like:
   % improvement 
   Time saved
   Revenue or cost impact
   Scale handled
   Users supported
   Systems managed
   Performance gains

- At least 40–50% of bullet points MUST contain numbers or measurable results.
- Format should be clean and ATS-friendly (no tables or graphics).
- Match my job titles as close as possible to the role I’m applying for (without faking).

Improve weak or responsibility-only bullets from my old CV by converting them into outcome- or impact-based points. Do not blindly copy.

If exact numbers are missing, use:

   1)"approximately"
   2)"around"
   3)"over"
   4)"more than"
   
   But never invent unrealistic numbers.

Good metric examples:

 1) Reduced incidents by 30%
 2) Improved deployment time by 40%
 3) Supported 200+ users
 4) Managed 50+ servers
 5) Reduced cloud cost by 20%
 6)Increased test coverage from 60% to 85%
 
- Use keywords MOST relevant to the target country + the JD.
- Tone should feel confident and natural (structured, collaborative, humble).

2. Professional Summary (Max 50 words)
- role: 5–6 bullet points with results and keywords
- At least 50% of bullets must include numbers
- For earlier roles: 3–4 concise points
- Each bullet must highlight value, not just duties
Every bullet must follow:
Action → SkX years of experience in [industry/domain]
- Skilled in [Skill 1], [Skill 2], [Skill 3] (from JD)
- Delivered [quantifiable result] at [last company]
- End with: “Open to relocation.”

3. Work Experience (Max 350 words)
- List jobs in reverse order (latest first)
- For latest ill → Result

**4. Skills (Max 50 words)**

* Organize skills into **EXACTLY these 6 categories** (do not rename, remove, or add any):
  **Languages | Frameworks & Libraries | AI / LLM Engineering | Databases & APIs | Cloud, DevOps & Infrastructure | Leadership & Practices**
* Order categories by relevance to the JD/role; within each category, list the JD's **must-have skills first**.
* Include **technical and soft skills explicitly required by the JD**, but only when supported by my CV.
* Place each skill in its single correct category (React = Framework, SQL = Language, PostgreSQL = Database).
* Pull skills from the JD, but **only include skills I actually have from my CV**. Never invent tools, skills, or proficiency levels.
* Mirror the JD's **exact terminology and spelling** (e.g., "TypeScript", "CI/CD", "Kubernetes").
* Use **comma-separated, ATS-safe formatting**. No tables, graphics, or keyword stuffing.
* Avoid generic terms such as "team player" or "hard worker" unless explicitly stated in the JD.
* **Strictly enforce the 50-word maximum**, including category names and skills.

5. Make sure the language feels human — natural, confident, and written as if by an experienced professional, not by AI. Keep a few words that show collaboration, ownership, and problem-solving.”

🎯 Final Output Must Be:
- 500–600 words
- ATS-safe formatting
- Optimized with JD keywords
- Easy to read and recruiter-friendly
- Grammar and tone checked
Avoid generic AI phrases. Write as an experienced professional would naturally explain their work to a recruiter.
 
"""

def generate_resume_json(api_key, model, old_cv, jd, country, template):
    prompt = build_prompt(old_cv, jd, country, template)
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model, temperature=0, top_p=1,
        messages=[
            {"role": "system", "content":
             "You are an expert ATS resume writer and recruiter. Analyze the OLD_CV and JOB_DESCRIPTION. "
             "Optimize for ATS relevance, recruiter readability, and interview defensibility. "
             "Return ONLY valid JSON that matches the schema."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI returned an empty response.")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI returned invalid JSON.") from exc
    required = ["title", "professional_summary", "skills", "experience"]
    missing = [x for x in required if x not in data]
    if missing:
        raise RuntimeError("JSON is missing: " + ", ".join(missing))
    return data
