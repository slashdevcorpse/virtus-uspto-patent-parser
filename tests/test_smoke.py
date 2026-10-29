"""Smoke test of the Virtus packaging: import the installed package and parse two small fixtures.

The fixtures are synthetic. Each follows the shape of a weekly grant file: the XML v4 one (ipgYYMMDD.xml) joins
grants one after the other, each with its own XML declaration; the APS TXT one (Green Book) starts with a header
line and opens each grant with a PATN line.
"""

from pathlib import Path

import uspto_patent_parser
from uspto_patent_parser.parsers import parse_xml_v4_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_public_entry_points_import():
    assert callable(uspto_patent_parser.read_and_parse_file_from_disk)
    assert uspto_patent_parser.parse_patent_data_xml_4 is parse_xml_v4_file.parse_patent_data_xml_4


def test_parse_xml_v4_fixture():
    grants = uspto_patent_parser.read_and_parse_file_from_disk(str(FIXTURES / "ipg_two_grants.xml"), ["INVT", "ABST", "CLMS"], "xml4")

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


def test_parse_aps_txt_fixture():
    grants = uspto_patent_parser.read_and_parse_file_from_disk(
        str(FIXTURES / "aps_two_grants.txt"), ["INVT", "ABST", "CLMS"], "txt"
    )

    assert len(grants) == 2
    first, second = grants

    assert first["bibliographic_information"] == {
        "Patent Number": "039999911",
        "Series Code": "5",
        "Application Number": "5000001",
        "Application Type": "1",
        "Art unit": "242",
        "Application Filing Date": "19750102",
        "Title of Invention": "Synthetic widget for a parser smoke test",
        "Issue Date": "19760106",
        "Number of Claims": "2",
    }
    assert first["abstract"] == "A synthetic widget that has a first part and a second part."
    assert first["inventors"] == [{"inventor name": "Doe; Jane", "City": "Alexandria", "State": "VA"}]
    assert first["claim_information"] == {
        "NUM": "1.",
        "PAR": "A widget comprising a first part and a second part.",
        "NUM_2": "2.",
        "PAR_2": "The widget of claim 1, wherein the first part is round.",
    }

    assert second["bibliographic_information"]["Patent Number"] == "039999929"
    assert "inventors" not in second
