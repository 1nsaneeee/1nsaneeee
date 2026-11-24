import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

import terminal_art as art


class ColdJokeTests(unittest.TestCase):
    def test_shuffle_operates_on_complete_blocks(self):
        config = "single\n===\npart 1\n # ignored\n\npart 2\n===\n===\n===\n===\nopen 1\nopen 2"
        with patch.object(art.random, "shuffle", side_effect=list.reverse):
            self.assertEqual(art.tip_pages(config), ["open 1", "open 2", "part 1", "part 2", "single"])

    def test_literal_equals_and_unmarked_lines(self):
        with patch.object(art.random, "shuffle", side_effect=list.reverse):
            self.assertEqual(art.tip_pages("A\n B===C\nD # literal\n==="),
                             ["D # literal", "B===C", "A"])
            self.assertEqual(art.tip_pages(" \n # none\n===\n==="), [])

    def test_budget_keeps_wrapped_lines_and_groups_whole(self):
        long_line = "甲" * 80
        config = f"a\n===\n{long_line}\nend\n===\nb"
        with patch.object(art.random, "shuffle", return_value=None):
            self.assertEqual(art.tip_pages(config, page_budget=4), ["a", "b"])
            self.assertEqual(art.tip_pages(config, page_budget=5),
                             ["a", "甲" * 37, "甲" * 37, "甲" * 6, "end"])
            oversized = f"===\n{long_line}\nend\n===\nb"
            with self.assertLogs("terminal_art", level="WARNING"):
                self.assertEqual(art.tip_pages(oversized, page_budget=2), ["b"])
            self.assertEqual(art.tip_pages(oversized, page_budget=None),
                             ["甲" * 37, "甲" * 37, "甲" * 6, "end", "b"])

    def test_render_uses_one_playlist_for_both_themes(self):
        with tempfile.TemporaryDirectory() as folder:
            outputs = {}
            def capture(path, content):
                outputs[path.name] = content
            with patch.object(art, "read_tip_pages", return_value=["first", "second"]) as read:
                art.render_terminal({"end": "2026-11-24", "owned": 0, "commits": []}, Path(folder), capture)
            read.assert_called_once_with()
        for theme in art.THEMES:
            svg = ElementTree.fromstring(outputs[f"banner-{theme}.svg"])
            reel = svg.find(".//{*}g[@class='tip-reel']")
            self.assertEqual([item[-1].text for item in reel], ["first", "second"])
            self.assertEqual(reel[0].get("y"), "19")
            self.assertNotIn("animation-delay", reel.attrib["style"])


if __name__ == "__main__":
    unittest.main()
