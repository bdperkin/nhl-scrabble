"""XML output formatter.

Converts NHL Scrabble analysis data to XML format for integration with enterprise systems and legacy
applications.
"""

from __future__ import annotations

from typing import Any


class XMLFormatter:
    """Format analysis data as XML.

    Produces well-formatted XML output with proper indentation, suitable for
    enterprise integration and legacy system compatibility.

    Example:
        >>> formatter = XMLFormatter()
        >>> output = formatter.format(data)
        >>> "<?xml" in output
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to XML string.

        Args:
            data: Analysis data dictionary with structure:
                {
                    "teams": {...},
                    "divisions": {...},
                    "conferences": {...},
                    "playoffs": {...},
                    "summary": {...}
                }

        Returns:
            Pretty-printed XML string with proper structure

        Raises:
            ImportError: If dicttoxml is not installed

        Example:
            >>> formatter = XMLFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> "<teams>" in output
            True
        """
        try:
            import xml.dom.minidom  # noqa: PLC0415  # nosec B408

            from dicttoxml import dicttoxml  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(
                "dicttoxml is required for XML format. Install with: pip install dicttoxml"
            ) from e

        # Convert dict to XML
        xml_bytes = dicttoxml(
            data,
            custom_root="nhl_scrabble",
            attr_type=False,  # Don't add type attributes
        )

        # Parse and pretty-print (safe: parsing our own generated XML, not untrusted input)
        dom = xml.dom.minidom.parseString(xml_bytes)  # noqa: S318  # nosec B318
        pretty_xml = dom.toprettyxml(indent="  ")

        return pretty_xml
