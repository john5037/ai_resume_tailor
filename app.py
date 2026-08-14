from pathlib import Path
import json
import re

import yaml
import streamlit as st

from core.ai_generator import generate_resume_json
from core.yaml_updater import update_resume_yaml
from core.rendercv_runner import render_resume
from core.utils import read_text, safe_name


# ============================================================
# PATHS
# ============================================================

BASE = Path(__file__).resolve().parent

PROMPT_FILE = BASE / "prompts" / "prompt_template_aih.txt"
BASE_YAML_FILE = BASE / "templates" / "base_resume.yaml"
OLD_CV_FILE = BASE / "old_cv.txt"
JD_FILE = BASE / "jd.txt"
OUTPUT = BASE / "outputs"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="📄",
    layout="wide",
)

st.title("AI Resume Tailor")
st.caption("GPT powered ATS resume generation with RenderCV")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_state(name, path):
    """
    Load a file into Streamlit session state only once.
    """
    if name not in st.session_state:
        st.session_state[name] = (
            read_text(path) if path.exists() else ""
        )

    return st.session_state[name]


def make_resume_filename(name, title, country):
    """
    Create a clean dynamic PDF filename.
    """

    def clean(value):
        value = str(value).strip()

        # Remove characters that are unsafe in filenames
        value = re.sub(r'[<>:"/\\|?*]', "", value)

        # Remove special characters but keep letters/numbers/spaces/hyphens
        value = re.sub(r"[^\w\s-]", "", value)

        # Convert spaces and repeated hyphens to underscores
        value = re.sub(r"[\s-]+", "_", value)

        return value.strip("_")

    clean_name = clean(name)
    clean_title = clean(title)
    clean_country = clean(country)

    return f"{clean_name}_{clean_title}_{clean_country}.pdf"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Generation")

    api_key = st.text_input(
        "OpenAI API key",
        type="password",
    )

    model = st.selectbox(
        "Model",
        ["gpt-4.1"],
        index=0,
    )

    country = st.text_input(
        "Target country",
        "Abu Dhabi, UAE",
    )

    st.caption(
        "Your API key is entered per session and is not "
        "written to project files."
    )


# ============================================================
# OLD CV
# ============================================================

old_cv = st.text_area(
    "OLD CV",
    value=read_text(OLD_CV_FILE),
    height=320,
    key="old_cv_editor",
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.session_state["jd"] = st.text_area(
    "JOB DESCRIPTION",
    value=load_state("jd", JD_FILE),
    height=320,
    key="jd_editor",
)


# ============================================================
# PROMPT TEMPLATE
# ============================================================

st.subheader("Prompt Template")

st.session_state["prompt"] = st.text_area(
    "The default prompt is loaded from prompt_template_aih.txt. "
    "Edit it if required.",
    value=load_state("prompt", PROMPT_FILE),
    height=480,
    key="prompt_editor",
)

if st.button("Reset Prompt to Default"):

    st.session_state["prompt"] = read_text(PROMPT_FILE)

    st.rerun()


# ============================================================
# BASE RESUME YAML
# ============================================================

st.subheader("Base Resume YAML")

st.session_state["base_yaml"] = st.text_area(
    "Edit the single RenderCV base template if required.",
    value=load_state("base_yaml", BASE_YAML_FILE),
    height=480,
    key="yaml_editor",
)

if st.button("Reset YAML to Default"):

    st.session_state["base_yaml"] = read_text(BASE_YAML_FILE)

    st.rerun()


# ============================================================
# GENERATE RESUME
# ============================================================

if st.button(
    "🚀 AI Generate Resume",
    type="primary",
    use_container_width=True,
):

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not api_key.strip():

        st.error("Enter an OpenAI API key.")

        st.stop()

    if not old_cv.strip():

        st.error("Enter the OLD CV.")

        st.stop()

    if not st.session_state["jd"].strip():

        st.error("Enter the Job Description.")

        st.stop()


    # --------------------------------------------------------
    # VALIDATE BASE YAML
    # --------------------------------------------------------

    try:

        base = yaml.safe_load(
            st.session_state["base_yaml"]
        )

        if not isinstance(base, dict):

            raise ValueError(
                "Base YAML must contain a valid object."
            )

        if "cv" not in base:

            raise ValueError(
                "Base YAML must contain a top-level cv object."
            )

    except Exception as exc:

        st.error(f"Invalid base YAML: {exc}")

        st.stop()


    # --------------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------------

    with st.spinner(
        "Generating structured JSON with GPT..."
    ):

        try:

            data = generate_resume_json(
                api_key.strip(),
                model,
                old_cv,
                st.session_state["jd"],
                country,
                st.session_state["prompt"],
            )

        except Exception as exc:

            st.error(str(exc))

            st.stop()


    # --------------------------------------------------------
    # CREATE TAILORED YAML
    # --------------------------------------------------------

    try:

        tailored = update_resume_yaml(
            base,
            data,
        )

        OUTPUT.mkdir(
            exist_ok=True
        )

        # Create YAML content
        yaml_content = yaml.safe_dump(
            tailored,
            sort_keys=False,
            allow_unicode=True,
        )

        yaml_path = (
            OUTPUT / "resume_tailored.yaml"
        )

        yaml_path.write_text(
            yaml_content,
            encoding="utf-8",
        )

        # Save in session state
        st.session_state[
            "tailored_yaml"
        ] = yaml_content

        # Save AI JSON
        json_path = (
            OUTPUT / "ai_response.json"
        )

        json_path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        # Save original AI-generated YAML
        st.session_state[
            "original_tailored_yaml"
        ] = yaml_content

        # Save title for dynamic filename
        st.session_state[
            "resume_title"
        ] = data.get(
            "title",
            "Resume",
        )

        st.success(
            "Resume content generated successfully."
        )

    except Exception as exc:

        st.error(
            f"Could not create YAML: {exc}"
        )

        st.stop()

# ============================================================
# READY-MADE RESUME
# ============================================================

st.divider()

st.subheader("📄 Ready-Made Resume")

st.caption(
    "Load the existing resume_tailored.yaml without using OpenAI. "
    "You can edit it below and generate the PDF."
)

if st.button(
    "📄 Load Ready-Made Resume",
    type="secondary",
    use_container_width=True,
):

    ready_yaml_path = OUTPUT / "resume_tailored.yaml"

    if not ready_yaml_path.exists():

        st.error(
            "resume_tailored.yaml was not found in the outputs folder."
        )

    else:

        try:

            ready_yaml_content = ready_yaml_path.read_text(
                encoding="utf-8"
            )

            # Validate YAML
            ready_data = yaml.safe_load(
                ready_yaml_content
            )

            if not isinstance(
                ready_data,
                dict,
            ):

                raise ValueError(
                    "resume_tailored.yaml must contain a valid YAML object."
                )

            if "cv" not in ready_data:

                raise ValueError(
                    "resume_tailored.yaml must contain a top-level 'cv' section."
                )

            # Put ready-made YAML into the same editor
            st.session_state[
                "tailored_yaml"
            ] = ready_yaml_content

            # Keep a restore copy
            st.session_state[
                "original_tailored_yaml"
            ] = ready_yaml_content

            # Default filename title
            st.session_state[
                "resume_title"
            ] = ready_data.get(
                "cv",
                {}
            ).get(
                "headline",
                "Resume"
            )

            st.success(
                "Ready-made resume loaded successfully. "
                "You can edit the YAML below."
            )

            st.rerun()

        except yaml.YAMLError as exc:

            st.error(
                f"Invalid resume_tailored.yaml: {exc}"
            )

        except Exception as exc:

            st.error(
                f"Could not load resume_tailored.yaml: {exc}"
            )
# ============================================================
# AI RESPONSE JSON
# ============================================================

if "ai_response" in st.session_state:

    with st.expander("AI Response JSON"):

        st.json(
            st.session_state["ai_response"]
        )


# ============================================================
# EDITABLE TAILORED YAML
# ============================================================

if "tailored_yaml" in st.session_state:

    st.divider()

    st.subheader(
        "Resume Tailored YAML"
    )

    edited_yaml = st.text_area(
        "Edit the generated YAML below. "
        "You can change wording, bullets, skills, "
        "headline, etc. without calling GPT again.",
        value=st.session_state[
            "tailored_yaml"
        ],
        height=700,
        key="tailored_yaml_editor",
    )


    # ========================================================
    # YAML ACTIONS
    # ========================================================

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # RESTORE AI VERSION
    # --------------------------------------------------------

    with col1:

        if st.button(
            "↩️ Restore AI Generated YAML",
            use_container_width=True,
        ):

            st.session_state[
                "tailored_yaml"
            ] = st.session_state[
                "original_tailored_yaml"
            ]

            st.rerun()


    # --------------------------------------------------------
    # GENERATE PDF
    # --------------------------------------------------------

    with col2:

        generate_pdf = st.button(
            "📄 Generate PDF",
            type="primary",
            use_container_width=True,
        )


    # ========================================================
    # GENERATE PDF FROM EDITED YAML
    # ========================================================

    if generate_pdf:

        # ----------------------------------------------------
        # Validate YAML
        # ----------------------------------------------------

        try:

            edited_data = yaml.safe_load(
                edited_yaml
            )

            if not isinstance(
                edited_data,
                dict,
            ):

                raise ValueError(
                    "YAML must contain a valid object."
                )

            if "cv" not in edited_data:

                raise ValueError(
                    "YAML must contain a top-level "
                    "'cv' section."
                )

        except yaml.YAMLError as exc:

            st.error(
                f"Invalid YAML syntax: {exc}"
            )

            st.stop()

        except Exception as exc:

            st.error(
                f"Invalid YAML: {exc}"
            )

            st.stop()


        # ----------------------------------------------------
        # Save edited YAML
        # ----------------------------------------------------

        try:

            OUTPUT.mkdir(
                exist_ok=True
            )

            yaml_path = (
                OUTPUT / "resume_tailored.yaml"
            )

            yaml_path.write_text(
                edited_yaml,
                encoding="utf-8",
            )

            # Keep latest version
            st.session_state[
                "tailored_yaml"
            ] = edited_yaml

        except Exception as exc:

            st.error(
                f"Could not save edited YAML: {exc}"
            )

            st.stop()


        # ----------------------------------------------------
        # Render PDF
        # ----------------------------------------------------

        with st.spinner(
            "Rendering PDF with RenderCV..."
        ):

            try:

                pdf_path, render_log = render_resume(
                    yaml_path
                )

            except Exception as exc:

                st.error(
                    f"RenderCV failed: {exc}"
                )

                with st.expander(
                    "RenderCV Diagnostic Output",
                    expanded=True,
                ):

                    st.code(
                        str(exc)
                    )

                st.stop()


        # ----------------------------------------------------
        # PDF RESULT
        # ----------------------------------------------------

        if pdf_path and pdf_path.exists():

            st.success(
                "PDF generated successfully."
            )

            pdf_bytes = (
                pdf_path.read_bytes()
            )


            # Dynamic filename
            resume_filename = make_resume_filename(
                "Kamal Nayak",
                st.session_state.get(
                    "resume_title",
                    "Resume",
                ),
                country,
            )


            st.download_button(
                "📄 Download PDF",
                pdf_bytes,
                file_name=resume_filename,
                mime="application/pdf",
                use_container_width=True,
            )


            # ------------------------------------------------
            # Download YAML
            # ------------------------------------------------

            st.download_button(
                "Download YAML",
                edited_yaml.encode("utf-8"),
                file_name="resume_tailored.yaml",
                mime="text/yaml",
                use_container_width=True,
            )


            # ------------------------------------------------
            # Download JSON
            # ------------------------------------------------

            json_path = (
                OUTPUT / "ai_response.json"
            )

            if json_path.exists():

                st.download_button(
                    "Download JSON",
                    json_path.read_bytes(),
                    file_name="ai_response.json",
                    mime="application/json",
                    use_container_width=True,
                )


            # ------------------------------------------------
            # RenderCV Output
            # ------------------------------------------------

            with st.expander(
                "RenderCV Output"
            ):

                st.code(
                    render_log
                    or
                    "RenderCV completed successfully."
                )

        else:

            st.error(
                "RenderCV completed but no PDF "
                "file was found."
            )

            if render_log:

                with st.expander(
                    "RenderCV Output",
                    expanded=True,
                ):

                    st.code(
                        render_log
                    )