import os
import unittest

from packaging.requirements import Requirement

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIREMENTS = os.path.join(BASEDIR, "requirements.txt")

# extras actually provided by dependencies used in requirements.txt
KNOWN_EXTRAS = {
    "ovos-utils": set(),
    "langcodes": {"data"},
}


class TestRequirements(unittest.TestCase):
    def _requirements(self):
        with open(REQUIREMENTS) as f:
            lines = [l.strip() for l in f.read().splitlines()]
        return [Requirement(l) for l in lines
                if l and not l.startswith("#")]

    def test_no_nonexistent_extras(self):
        for req in self._requirements():
            allowed = KNOWN_EXTRAS.get(req.name, set())
            self.assertTrue(
                set(req.extras) <= allowed,
                f"{req.name} declares unknown extra(s): {req.extras}")

    def test_ovos_utils_plain_with_floor(self):
        reqs = {r.name: r for r in self._requirements()}
        self.assertIn("ovos-utils", reqs)
        req = reqs["ovos-utils"]
        self.assertEqual(set(req.extras), set())
        self.assertTrue(len(req.specifier) > 0,
                        "ovos-utils must declare a version constraint")


if __name__ == "__main__":
    unittest.main()
