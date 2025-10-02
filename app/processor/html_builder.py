"""HTML generation helpers for informativos."""
from __future__ import annotations

from typing import Mapping

SVG_SNIPPET = (
    '<svg aria-labelledby="icon-download-solid" role="img" enable-background="new 0 0 24 24" '
    'viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="svg-8 svg-fill-white mb-1">\n'
    "        <path d=\"m12 16c-.205 0-.401-.084-.543-.232l-5.25-5.5c-.455-.477-.114-1.268.543-1.268h2.75v-1.25c0-4.273 3.477-7.75 7.75-7.75.414 0 .75.336.75.75s-.336.75-.75.75c-1.517 0-2.75 1.233-2.75 2.75v4.75h2.75c.657 0 .998.791.543 1.268l-5.25 5.5c-.142.148-.338.232-.543.232z\"></path>\n"
    "        <path d=\"m21 18h-18c-1.654 0-3 1.346-3 3s1.346 3 3 3h18c1.654 0 3-1.346 3-3s-1.346-3-3-3z\"></path>\n"
    "      </svg>"
)


def build_li(metadata: Mapping[str, str], filename: str) -> str:
    """Build the HTML ``<li>`` element for a processed PDF."""
    number = metadata["number"]
    acronym = metadata["acronym"]
    fullname = metadata["fullname"]
    year = metadata["year"]
    semester = metadata.get("semester", "1")

    href = f"assets/download/informativos/{year}/{filename}"
    title = f"Veja o informativo da {fullname} ({year}.{semester})"

    return (
        '<li class="informativo list-group-item col-12 col-md-6 border-end">\n'
        f'  <a class="page-pdf" href="{href}" title="{title}">\n'
        f'    {number}. {acronym}\n'
        "    <span class=\"badge bg-primary rounded-pill float-end\">PDF\n"
        f"      {SVG_SNIPPET}\n"
        "    </span>\n"
        "  </a>\n"
        "</li>"
    )
