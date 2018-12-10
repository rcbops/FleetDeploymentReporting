import unittest

from cloud_snitch.models import registry


class TestPathsFrom(unittest.TestCase):
    """Test outcomes of the paths_from member function of the forest."""
    def test_bad_label(self):
        """Test that invalid label results in empty list."""
        model = 'notamodel'
        paths = registry.forest.paths_from(model)
        self.assertTrue(isinstance(paths, list))
        self.assertEqual(len(paths), 0)

    def test_model_is_in_path_to_itself(self):
        """Test that the first path is of length 1 and is to itself."""
        model = 'Environment'
        first = registry.forest.paths_from(model)[0]
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0], model)

    def test_sorted(self):
        """Test that paths are produced in order by ascending length."""
        model = 'Environment'
        paths = registry.forest.paths_from(model)
        for i in range(1, len(paths)):
            self.assertTrue(len(paths[i]) >= len(paths[i - 1]))
