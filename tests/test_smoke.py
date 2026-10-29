"""Smoke test of the Virtus packaging: import the installed modules and parse one small XML v4 fixture.

The fixture is synthetic. It follows the shape of a weekly grant file (ipgYYMMDD.xml): grants joined one after
the other, each with its own XML declaration.
"""

from pathlib import Path

import parsers.parse_xml_v4_file
import uspto

FIXTURE = Path(__file__).parent / "fixtures" / "ipg_two_grants.xml"


def test_public_entry_points_import():
    assert callable(uspto.read_and_parse_file_from_disk)
    assert uspto.parse_patent_data_xml_4 is parsers.parse_xml_v4_file.parse_patent_data_xml_4


def test_parse_xml_v4_fixture():
    grants = uspto.read_and_parse_file_from_disk(str(FIXTURE), ["INVT", "ABST", "CLMS"], "xml4")

    assert len(grants) == 2
    utility, design = grants

    # Upstream merges the publication and application document ids into one dict, so the application number and
    # date replace the publication ones; `kind` comes from the publication.
    assert utility["bibliographic_information"] == {
        "country": "US",
        "doc-number": "15000001",
        "kind": "B2",
        "date": "20180102",
        "invention_title": "Synthetic widget for a parser smoke test",
    }
    assert utility["abstract"] == ["A synthetic widget that has a first part and a second part."]
    assert utility["inventors"] == [
        {
            "sequence": "001",
            "designation": "us-only",
            "city": "Alexandria",
            "state": "VA",
            "country": "US",
            "addressbook/first-name": "Jane",
            "addressbook/last-name": "Doe",
        }
    ]
    assert [claim["claim_text"] for claim in utility["claim_information"]] == [
        ["1. A widget comprising a first part and a second part."],
        ["2. The widget of claim 1, wherein the first part is round."],
    ]

    assert design["bibliographic_information"]["invention_title"] == "Synthetic ornamental design"
    assert design["bibliographic_information"]["kind"] == "S1"
    assert "inventors" not in design
