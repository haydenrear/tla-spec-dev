"""The fixture's own tests. Green before the agents touch it, and the harness
records whether they are still green afterwards -- an agent that leaves the
fixture red has broken the thing it was modeling.
"""

import unittest

from shortlink import Shortener, ShortlinkError


class ShortenerTests(unittest.TestCase):
    def test_reserve_then_claim_makes_the_slug_live(self) -> None:
        s = Shortener()
        s.reserve("go", "ana")
        s.claim("go", "ana", "https://example.test/")
        self.assertEqual(s.resolve("go"), "https://example.test/")

    def test_a_reservation_is_not_claimable_by_another_owner(self) -> None:
        s = Shortener()
        s.reserve("go", "ana")
        with self.assertRaises(ShortlinkError):
            s.claim("go", "bo", "https://example.test/")

    def test_release_frees_the_slug_for_a_different_owner(self) -> None:
        s = Shortener()
        s.reserve("go", "ana")
        s.claim("go", "ana", "https://a.test/")
        s.release("go", "ana")
        s.reserve("go", "bo")
        s.claim("go", "bo", "https://b.test/")
        self.assertEqual(s.resolve("go"), "https://b.test/")

    def test_a_live_slug_cannot_be_released_by_a_stranger(self) -> None:
        s = Shortener()
        s.reserve("go", "ana")
        s.claim("go", "ana", "https://a.test/")
        with self.assertRaises(ShortlinkError):
            s.release("go", "bo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
