import json
from openai import OpenAI

def build_prompt(old_cv, jd, country, template):
   return f"""
Step 1: Please read and remember my OLD CV (pasted below). DO NOT rewrite yet. Just understand my experience, roles, and achievements.
{template}

<PASTE OLD CV HERE>
{old_cv}
</PASTE OLD CV HERE>

🔹 Step 2: Here is the Job Description (JD) for the role I am applying for. 
Use this to guide everything:

<PASTE JOB DESCRIPTION HERE>
{jd}
<PASTE JOB DESCRIPTION HERE>

---
 Step 3: Now write a clean, ATS-optimized resume for this country:
 Target Country: 
<COUNTRY>
{country}
</COUNTRY>

If the target country is not explicitly listed, follow that country's common resume style. 
When unsure, default to a clean EU-style resume.

Write the resume like you’re helping me get shortlisted for this exact job not just pass ATS.

Make sure keywords, tone, and style match hiring patterns in that region.
# Instructions:
  - Study the JD and pull out keywords, tools, responsibilities, and soft skills.
  - Use simple, confident language — no robotic phrases or fluff.
  - Every bullet point should show value, outcome, or measurable result.
Use metrics like:
   - % improvement 
   - Time saved
   - Revenue or cost impact
   - Scale handled
   - Users supported
   - Systems managed
   - Performance gains

- At least 40–50% of bullet points MUST contain numbers or measurable results.
- Format should be clean and ATS-friendly (no tables or graphics).
- Match my job titles as close as possible to the role I’m applying for (without faking).

Improve weak or responsibility-only bullets from my old CV by converting them into outcome- or impact-based points. Do not blindly copy.

If exact numbers are missing, use:

   - "approximately"
   - "around"
   - "over"
   - "more than"
      But never invent unrealistic numbers.

Good metric examples:

 - Reduced incidents by 30%
 - Improved deployment time by 40%
 - Supported 200+ users
 - Managed 50+ servers
 - Reduced cloud cost by 20%
 - Increased test coverage from 60% to 85%
 
- Use keywords MOST relevant to the target country + the JD.
- Tone should feel confident and natural (structured, collaborative, humble).

Resume Format (500–600 words max):
1. Contact Information
Full name, phone number, email, LinkedIn profile, current location (City, Country)

2. Professional Summary (Max 50 words)
Mention total years of experience + relevant years aligned to the JD.
Highlight 3 key skills/technologies from the JD that are supported by the CV.
Include one strong achievement/result from the CV, preferably from the most relevant/latest company.
Tailor wording to the target role, domain, and country.
Do not invent skills, experience, achievements, or metrics.
End with: "Open to relocation."
Follow the concise style and structure of the provided examples. 
    Examples
    Example 1:
    20 years of IT experience with 6 years of relevant expertise in Advanced/network engineering and security. Skilled in VMware NSX-T, Palo Alto firewalls, and WAN technologies. Delivered critical network optimizations and security enhancements at [Last Company].
    Open to relocation.
    Example 2:
    Over 20 years of professional experience with 6 years focused on relevant roles in network architecture and firewall management. Proficient in VMware NSX-T, F5 load balancing, and WAN connectivity. Achieved 30% network downtime reduction at [Last Company].
    Open to relocation.
    Example 3:
    Cloud professional with 15 years of total experience, including 6 years of relevant work in complex network environments. Expertise in Palo Alto firewalls, NSX-T, and WAN design. Successfully led multiple network upgrade projects at [Last Company].
    Open to relocation.

3. Work Experience (Max 350 words)
- List jobs in reverse order (latest first)
- For latest role: 5–6 bullet points with results and keywords
- At least 50% of bullets must include numbers
- For earlier roles: 3–4 concise points
- Each bullet must highlight value, not just duties

Every bullet must follow:
Action → Skill → Result

**4. Skills (Max 50 words)**

- Technical + soft skills from the JD
* Organize skills into **EXACTLY these 6 categories** (do not rename, remove, or add any):
  **Languages | Frameworks & Libraries | AI / LLM Engineering | Databases & APIs | Cloud, DevOps & Infrastructure | Leadership & Practices**
* Order categories by relevance to the JD/role; within each category, list the JD's **must-have skills first**.
* Include **technical and soft skills explicitly required by the JD**.
* Place each skill in its single correct category (React = Framework, SQL = Language, PostgreSQL = Database).
* Mirror the JD's **exact terminology and spelling** (e.g., "TypeScript", "CI/CD", "Kubernetes").
* Use **comma-separated, ATS-safe formatting**. No tables, graphics, or keyword stuffing.
* Avoid generic terms.

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
    request = {
        "model": model.strip(),
        "messages": [
            {"role": "system", "content":
             "You are an expert ATS resume writer and recruiter. Analyze the OLD_CV and JOB_DESCRIPTION. "
             "Optimize for ATS relevance, recruiter readability, and interview defensibility. "
             "Return ONLY valid JSON that matches the schema."},
            {"role": "user", "content": prompt},
        ],
    }

    # Reasoning models generally do not accept sampling controls.
    if not request["model"].startswith(("o1", "o3", "o4", "gpt-5")):
        request["temperature"] = 0
        request["top_p"] = 1

    response = client.chat.completions.create(**request)
    content = response.choices[0].message.content
    print("OpenAI response:", content)
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
