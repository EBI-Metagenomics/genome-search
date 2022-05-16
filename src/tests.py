import unittest
from pathlib import Path

import hug

import app

TEST_SEQ = (
    "CATTTAACGCAACCTATGCAGTGTTTTTCTTCAATTAAGGCAAGTCGAGGCACTATGTAT"
    "TTATCTGTTTTTTTGTATAGAGGTTTTATGTCTACACCCACATTCAACGACAATGCCTTT"
    "ATAGTTTCATCGCCGCCCGGTAAGCAGCGGTTTATCTCTGCTGAATGATTTGCTATAGCT"
)


class TestCobs(unittest.TestCase):
    def test_cli(self):
        test_catalogue = Path("fixtures/catalogues/marine1.0")
        test_output = "/opt/local/data/marine1.0"

        hug.test.cli(
            app.index.create, str(test_catalogue.resolve()), test_output, clobber=True
        )
        self.assertTrue(Path(test_output + ".cobs_compact").is_file())

        app.search.clear_cache()

        # Non existent catalogue raises error
        matches = hug.test.cli(
            app.search.search,
            seq=TEST_SEQ,
            catalogues_filter=["badcatalogue0.0", "marine1.0"],
        )
        self.assertIsInstance(matches, hug.HTTPBadRequest)

        # Search matches correct genome
        matches = hug.test.cli(
            app.search.search, seq=TEST_SEQ, catalogues_filter=["marine1.0"]
        )
        query_seq = matches.pop("query")
        self.assertEqual(TEST_SEQ, query_seq)
        self.assertEqual(
            matches,
            {
                "threshold": 0.4,
                "results": [
                    {
                        "genome": "MGYG000296002",
                        "num_kmers": 150,
                        "num_kmers_found": 150,
                        "percent_kmers_found": 100.00,
                    }
                ],
            },
        )

    def test_api(self):
        # Bad request
        response = hug.test.post(
            app, "search", {"seq": TEST_SEQ, "catalogues_filter": ["nope0.0"]}
        )
        self.assertEqual(response.status, hug.HTTP_400)

        # Missing catalogues defaults to all
        response = hug.test.post(app, "search", {"seq": TEST_SEQ})
        self.assertEqual(response.status, hug.HTTP_200)

        # Good request
        response = hug.test.post(
            app, "search", {"seq": TEST_SEQ, "catalogues_filter": ["marine1.0"]}
        )
        self.assertEqual(response.status, hug.HTTP_200)
        matches = response.data
        query_seq = matches.pop("query")
        self.assertEqual(TEST_SEQ, query_seq)
        self.assertEqual(
            matches,
            {
                "threshold": 0.4,
                "results": [
                    {
                        "genome": "MGYG000296002",
                        "num_kmers": 150,
                        "num_kmers_found": 150,
                        "percent_kmers_found": 100.00,
                    }
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
