def update_resume_yaml(base, data):
    cv = base["cv"]
    sections = cv.setdefault("sections", {})

    # ---------------------------------
    # Headline
    # ---------------------------------
    cv["headline"] = data["title"]

    # ---------------------------------
    # Professional Summary
    # ---------------------------------
    sections["professional_summary"] = data["professional_summary"]

    # ---------------------------------
    # Skills
    # IMPORTANT:
    # RenderCV detects this as OneLineEntry
    # because every item contains ONLY:
    # label + details
    # ---------------------------------
    skills = data.get("skills", {})

    if not isinstance(skills, dict):
        raise ValueError("AI skills must be a JSON object.")

    sections["skills"] = []

    skill_order = [
        "Languages",
        "Frameworks & Libraries",
        "AI / LLM Engineering",
        "Databases & APIs",
        "Cloud, DevOps & Infrastructure",
        "Leadership & Practices",
    ]

    for category in skill_order:
        details = skills.get(category)

        if details:
            sections["skills"].append({
                "label": category,
                "details": str(details),
            })

    # ---------------------------------
    # Projects
    # ---------------------------------
    if data.get("projects"):
        sections["projects"] = [
            {
                "name": project["name"],
                "summary": project.get("summary", ""),
                "highlights": project.get("highlights", []),
            }
            for project in data["projects"]
        ]

    # ---------------------------------
    # Work Experience
    # ---------------------------------
    work_experience = sections.get("work_experience", [])

    for index, role in enumerate(data.get("experience", [])):
        if index < len(work_experience):
            work_experience[index]["highlights"] = role.get(
                "highlights", []
            )

    sections["work_experience"] = work_experience

    return base