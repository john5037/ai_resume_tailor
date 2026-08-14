from pathlib import Path
import os
import subprocess
import sys


def render_resume(yaml_path: Path):
    yaml_path = Path(yaml_path).resolve()

    # Output directory
    output_dir = yaml_path.parent / "rendered"
    output_dir.mkdir(parents=True, exist_ok=True)

    # PDF path
    pdf_path = output_dir / f"{yaml_path.stem}.pdf"

    # RenderCV executable from the current Python environment
    rendercv_exe = Path(sys.executable).parent / "rendercv.exe"

    if not rendercv_exe.exists():
        rendercv_exe = Path(sys.executable).parent / "rendercv"

    if not rendercv_exe.exists():
        raise RuntimeError(
            f"RenderCV executable not found.\n"
            f"Python: {sys.executable}\n"
            f"Expected: {rendercv_exe}"
        )

    command = [
        str(rendercv_exe),
        "render",
        str(yaml_path),
        "--pdf-path",
        str(pdf_path),
        "--dont-generate-markdown",
        "--dont-generate-html",
        "--dont-generate-png",
    ]

    env = os.environ.copy()

    # Windows UTF-8 protection
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    print("Running RenderCV:")
    print(" ".join(command))

    try:
        result = subprocess.run(
            command,
            cwd=str(yaml_path.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "RenderCV timed out after 120 seconds.\n"
            "This usually means Typst/RenderCV is stuck during PDF generation."
        )

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    log = (
        "COMMAND:\n"
        + " ".join(command)
        + "\n\n"
        + "STDOUT:\n"
        + stdout
        + "\n\n"
        + "STDERR:\n"
        + stderr
    )

    print(log)

    if result.returncode != 0:
        raise RuntimeError(
            f"RenderCV failed with exit code {result.returncode}.\n\n{log}"
        )

    # Explicitly requested PDF should now exist
    if pdf_path.exists():
        print(f"PDF generated successfully: {pdf_path}")
        return pdf_path, log

    # Diagnostic information
    generated_files = []

    for file in output_dir.rglob("*"):
        if file.is_file():
            generated_files.append(str(file))

    raise RuntimeError(
        "RenderCV finished without creating the expected PDF.\n\n"
        f"Expected PDF:\n{pdf_path}\n\n"
        f"Files found in output directory:\n"
        + "\n".join(generated_files)
        + "\n\n"
        + log
    )