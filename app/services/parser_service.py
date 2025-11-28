"""
Parser Service Module.
Handles ENEX file parsing and content sanitization.
Uses streaming XML parsing to avoid memory issues.
"""

import xml.etree.ElementTree as ET
import re
import base64
import hashlib
from typing import Dict, IO
from flask import current_app
import bleach
from app.services.firebase_service import create_post, create_user_index
import time


class ParserService:
    """Service for parsing ENEX files and sanitizing content."""

    # Allowed HTML tags for sanitization (XSS prevention)
    ALLOWED_TAGS = [
        "p",
        "br",
        "strong",
        "em",
        "u",
        "s",
        "blockquote",
        "ul",
        "ol",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "a",
        "img",
        "div",
        "span",
        "pre",
        "code",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    ]

    ALLOWED_ATTRIBUTES = {
        "a": ["href", "title"],
        "img": ["src", "alt", "title", "width", "height"],
        "div": ["class"],
        "span": ["class"],
        "pre": ["class"],
        "code": ["class"],
    }

    @staticmethod
    def parse_enex_stream(file_stream: IO, author_id: str) -> Dict:
        """
        Parse an ENEX file using streaming to avoid memory overflow.

        Args:
            file_stream: File-like object (from request.files['file'].stream)
            author_id: The user ID who is uploading the file

        Returns:
            Dictionary with parsing results: {'notes_imported': int, 'errors': list}
        """
        notes_imported = 0
        errors = []

        try:
            # Use iterparse for memory-efficient streaming
            context = ET.iterparse(file_stream, events=("end",))

            for event, elem in context:
                if elem.tag == "note":
                    try:
                        # Process this note
                        ParserService._process_note(elem, author_id)
                        notes_imported += 1

                        # Clear the element from memory
                        elem.clear()

                    except Exception as e:
                        error_msg = f"Error processing note: {str(e)}"
                        current_app.logger.error(error_msg)
                        errors.append(error_msg)
                        elem.clear()
                        continue

            return {"notes_imported": notes_imported, "errors": errors}

        except ET.ParseError as e:
            error_msg = f"XML parsing error: {str(e)}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

    @staticmethod
    def _process_note(note_elem: ET.Element, author_id: str):
        """
        Process a single note element and save to Firebase.

        Args:
            note_elem: XML Element representing a note
            author_id: The user ID
        """
        # Extract basic fields
        title = note_elem.find("title")
        title_text = title.text if title is not None and title.text else "Untitled"

        content_elem = note_elem.find("content")
        content_raw = (
            content_elem.text if content_elem is not None and content_elem.text else ""
        )

        created_elem = note_elem.find("created")
        created_timestamp = (
            ParserService._parse_enex_date(created_elem.text)
            if created_elem is not None and created_elem.text
            else time.time()
        )

        updated_elem = note_elem.find("updated")
        updated_timestamp = (
            ParserService._parse_enex_date(updated_elem.text)
            if updated_elem is not None and updated_elem.text
            else created_timestamp
        )

        # Extract tags
        tags = []
        for tag_elem in note_elem.findall("tag"):
            if tag_elem.text:
                tags.append(tag_elem.text)

        # Extract resources (images, attachments)
        resources = {}
        for resource_elem in note_elem.findall("resource"):
            resource_hash, resource_url = ParserService._process_resource(resource_elem)
            if resource_hash and resource_url:
                resources[resource_hash] = resource_url

        # Clean and sanitize content
        content_clean = ParserService._sanitize_enml(
            content_raw if content_raw else "", resources
        )

        # Create post data
        post_data = {
            "title": title_text,
            "content": content_clean,
            "author_id": author_id,
            "timestamp": created_timestamp,
            "updated_at": updated_timestamp,
            "tags": tags,
            "source": "enex_import",
        }

        # Save to Firebase
        post_id = create_post(post_data)

        # Create user-post index
        create_user_index(author_id, post_id)

    @staticmethod
    def _process_resource(resource_elem: ET.Element) -> tuple:
        """
        Process a resource (image/attachment) from ENEX.

        Args:
            resource_elem: XML Element representing a resource

        Returns:
            Tuple of (hash, url) - For now, returns (hash, data_uri)
            TODO: Upload to Firebase Storage or S3 and return public URL
        """
        try:
            # Get the resource hash (used to match <en-media> tags)
            # recognition_elem = resource_elem.find(".//recognition")
            data_elem = resource_elem.find("data")
            mime_elem = resource_elem.find("mime")

            if data_elem is None or data_elem.text is None:
                return None, None

            # The hash is in the data element's hash attribute
            resource_hash = data_elem.get("hash") if data_elem.get("hash") else None

            # If no hash in attribute, compute it from the data
            if not resource_hash:
                data_bytes = base64.b64decode(data_elem.text)
                resource_hash = hashlib.md5(data_bytes).hexdigest()

            mime_type = mime_elem.text if mime_elem is not None else "image/png"

            # For now, create a data URI (base64 embedded image)
            # TODO: Upload to cloud storage and return URL
            data_uri = f"data:{mime_type};base64,{data_elem.text}"

            return resource_hash, data_uri

        except Exception as e:
            current_app.logger.error(f"Error processing resource: {str(e)}")
            return None, None

    @staticmethod
    def _sanitize_enml(enml_content: str, resources: Dict[str, str]) -> str:
        """
        Sanitize ENML content and convert to safe HTML.

        Args:
            enml_content: Raw ENML string from ENEX
            resources: Dictionary mapping resource hashes to URLs

        Returns:
            Cleaned HTML string safe for rendering with |safe filter
        """
        if not enml_content:
            return ""

        # Remove ENML wrapper tags
        content = enml_content.replace("<en-note>", "").replace("</en-note>", "")

        # Replace <en-media> tags with <img> tags
        # Pattern: <en-media hash="abc123" type="image/png"/>
        def replace_media(match):
            hash_value = match.group(1)
            if hash_value in resources:
                return f'<img src="{resources[hash_value]}" alt="Embedded image" />'
            return ""  # Remove if resource not found

        content = re.sub(r'<en-media[^>]*hash="([^"]+)"[^>]*/>', replace_media, content)

        # Remove any remaining ENML tags
        content = re.sub(r"</?en-[^>]+>", "", content)

        # Sanitize with bleach to prevent XSS
        content = bleach.clean(
            content,
            tags=ParserService.ALLOWED_TAGS,
            attributes=ParserService.ALLOWED_ATTRIBUTES,
            strip=True,
        )

        return content

    @staticmethod
    def _parse_enex_date(date_string: str) -> float:
        """
        Parse Evernote date format to Unix timestamp.

        Evernote uses format: 20230615T120000Z (yyyymmddThhmmssZ)

        Args:
            date_string: Date string from ENEX

        Returns:
            Unix timestamp (float)
        """
        try:
            from datetime import datetime

            # Remove 'T' and 'Z' and parse
            clean_date = date_string.replace("T", "").replace("Z", "")
            dt = datetime.strptime(clean_date, "%Y%m%d%H%M%S")
            return dt.timestamp()
        except Exception as e:
            current_app.logger.warning(f"Error parsing date {date_string}: {str(e)}")
            return time.time()  # Fallback to current time
