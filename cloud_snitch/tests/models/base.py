import unittest


class DefinitionTestCase(unittest.TestCase):
    """Subclass this to test entity definitions."""

    label = 'somelabel'
    state_label = 'somelabelstate'
    identity_property = 'some_identity_property'
    static_properties = []
    state_properties = []
    concat_properties = {}
    children = {}

    entity = None

    def definition_test(self):
        """Test definition."""
        self.assertEqual(self.entity.label, self.label)
        self.assertEqual(self.entity.state_label, self.state_label)

        # Test identity property
        self.assertEqual(
            self.entity.identity_property,
            self.identity_property
        )

        # Test static properties
        for prop in self.static_properties:
            self.assertTrue(prop in self.entity.static_properties)
        self.assertEqual(
            len(self.entity.static_properties),
            len(self.static_properties)
        )

        # Test state properties
        for prop in self.state_properties:
            self.assertTrue(prop in self.entity.state_properties)
        self.assertEqual(
            len(self.entity.state_properties),
            len(self.state_properties)
        )

        # Test concat properies
        for prop_name, prop_list in self.concat_properties.items():
            for i, prop in enumerate(prop_list):
                self.assertEqual(
                    self.entity.concat_properties[prop_name][i],
                    prop
                )
            self.assertEqual(
                len(self.entity.concat_properties[prop_name]),
                len(prop_list)
            )
        self.assertEqual(
            len(self.entity.concat_properties),
            len(self.concat_properties)
        )

        # Test children
        for name, tup in self.children:
            self.assertEqual(self.entity.children[name], tup)
        self.assertEqual(len(self.entity.children), len(self.children))
