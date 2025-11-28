"""
Ingest Routes.
Handles ENEX file uploads and parsing.
"""

from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    jsonify,
)
from flask_login import login_required, current_user
from app.blueprints.ingest.blueprint import ingest_bp
from app.services.parser_service import ParserService

ALLOWED_EXTENSIONS = {"enex", "xml"}


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@ingest_bp.route("/")
@login_required
def index():
    """Render the upload page."""
    return render_template("ingest/upload.html")


@ingest_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """
    Handle ENEX file upload and parsing.
    Uses streaming XML parsing to avoid memory issues.
    """
    if "file" not in request.files:
        flash("No file part in the request", "error")
        return redirect(url_for("ingest.index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("ingest.index"))

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload an .enex or .xml file", "error")
        return redirect(url_for("ingest.index"))

    try:
        # Parse the file using streaming parser
        # file.stream is already a file-like object, no need to save to disk
        result = ParserService.parse_enex_stream(file.stream, author_id=current_user.id)

        flash(f"Successfully imported {result['notes_imported']} notes!", "success")
        return redirect(url_for("main.index"))

    except Exception as e:
        current_app.logger.error(f"Error parsing ENEX file: {str(e)}")
        flash(f"Error importing file: {str(e)}", "error")
        return redirect(url_for("ingest.index"))


@ingest_bp.route("/status/<task_id>")
@login_required
def upload_status(task_id):
    """
    Check the status of an async upload task.
    (For future implementation with Celery/RQ)
    """
    # TODO: Implement async task status checking
    return jsonify({"status": "pending", "progress": 0})
