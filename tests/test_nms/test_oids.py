"""Unit tests for oids module - SNMP OID constant definitions."""
import unittest
from snmp_monitor.nms import oids


class TestOIDs(unittest.TestCase):
    """Test OID constant definitions."""

    def test_system_oids_exist(self):
        """Test that system-related OIDs are defined."""
        self.assertTrue(hasattr(oids, 'SNMP_SYSTEM_DESCR'))
        self.assertTrue(hasattr(oids, 'SNMP_SYSTEM_UPTIME'))
        self.assertTrue(hasattr(oids, 'SNMP_SYSTEM_CONTACT'))
        self.assertTrue(hasattr(oids, 'SNMP_SYSTEM_NAME'))
        self.assertTrue(hasattr(oids, 'SNMP_SYSTEM_LOCATION'))

    def test_system_oid_values(self):
        """Test that system OID values are correct."""
        # System description OID
        self.assertEqual(oids.SNMP_SYSTEM_DESCR, (1, 3, 6, 1, 2, 1, 1, 1, 0))

        # System uptime OID
        self.assertEqual(oids.SNMP_SYSTEM_UPTIME, (1, 3, 6, 1, 2, 1, 1, 3, 0))

        # System contact OID
        self.assertEqual(oids.SNMP_SYSTEM_CONTACT, (1, 3, 6, 1, 2, 1, 1, 4, 0))

        # System name OID
        self.assertEqual(oids.SNMP_SYSTEM_NAME, (1, 3, 6, 1, 2, 1, 1, 5, 0))

        # System location OID
        self.assertEqual(oids.SNMP_SYSTEM_LOCATION, (1, 3, 6, 1, 2, 1, 1, 6, 0))

    def test_interface_oids_exist(self):
        """Test that interface-related OIDs are defined."""
        self.assertTrue(hasattr(oids, 'SNMP_IF_DESCR'))
        self.assertTrue(hasattr(oids, 'SNMP_IF_TYPE'))
        self.assertTrue(hasattr(oids, 'SNMP_IF_SPEED'))
        self.assertTrue(hasattr(oids, 'SNMP_IF_ADMIN_STATUS'))
        self.assertTrue(hasattr(oids, 'SNMP_IF_OPER_STATUS'))
        self.assertTrue(hasattr(oids, 'SNMP_IF_IN_OCTETS'))
        self.assertTrue(hasattr(oids, 'SNMP_IF_OUT_OCTETS'))

    def test_interface_oid_values(self):
        """Test that interface OID values are correct."""
        # Interface description table OID
        self.assertEqual(oids.SNMP_IF_DESCR, (1, 3, 6, 1, 2, 1, 2, 2, 1, 2))

        # Interface type table OID
        self.assertEqual(oids.SNMP_IF_TYPE, (1, 3, 6, 1, 2, 1, 2, 2, 1, 3))

        # Interface speed table OID
        self.assertEqual(oids.SNMP_IF_SPEED, (1, 3, 6, 1, 2, 1, 2, 2, 1, 5))

        # Interface admin status table OID
        self.assertEqual(oids.SNMP_IF_ADMIN_STATUS, (1, 3, 6, 1, 2, 1, 2, 2, 1, 7))

        # Interface operational status table OID
        self.assertEqual(oids.SNMP_IF_OPER_STATUS, (1, 3, 6, 1, 2, 1, 2, 2, 1, 8))

        # Interface inbound octets table OID
        self.assertEqual(oids.SNMP_IF_IN_OCTETS, (1, 3, 6, 1, 2, 1, 2, 2, 1, 10))

        # Interface outbound octets table OID
        self.assertEqual(oids.SNMP_IF_OUT_OCTETS, (1, 3, 6, 1, 2, 1, 2, 2, 1, 16))

    def test_process_oids_exist(self):
        """Test that process-related OIDs are defined."""
        self.assertTrue(hasattr(oids, 'SNMP_PROC_COUNT'))

    def test_process_oid_values(self):
        """Test that process OID values are correct."""
        # Process count OID
        self.assertEqual(oids.SNMP_PROC_COUNT, (1, 3, 6, 1, 4, 1, 9, 9, 10, 1, 1, 1, 1))

    def test_storage_oids_exist(self):
        """Test that storage-related OIDs are defined."""
        self.assertTrue(hasattr(oids, 'SNMP_STORAGE_DESCR'))
        self.assertTrue(hasattr(oids, 'SNMP_STORAGE_SIZE'))
        self.assertTrue(hasattr(oids, 'SNMP_STORAGE_USED'))

    def test_storage_oid_values(self):
        """Test that storage OID values are correct."""
        # Storage description table OID
        self.assertEqual(oids.SNMP_STORAGE_DESCR, (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 3))

        # Storage size table OID
        self.assertEqual(oids.SNMP_STORAGE_SIZE, (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 5))

        # Storage used table OID
        self.assertEqual(oids.SNMP_STORAGE_USED, (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 6))

    def test_custom_private_oids_exist(self):
        """Test that custom private OIDs are defined."""
        self.assertTrue(hasattr(oids, 'CUSTOM_PRIVATE_MIB_BASE'))

    def test_custom_private_oid_values(self):
        """Test that custom private OID values are correct."""
        # Custom private MIB base OID
        self.assertEqual(oids.CUSTOM_PRIVATE_MIB_BASE, (1, 3, 6, 1, 4, 1, 99999))

    def test_oid_format(self):
        """Test that OIDs are in correct format (tuple of integers)."""
        oids_list = [
            oids.SNMP_SYSTEM_DESCR,
            oids.SNMP_SYSTEM_UPTIME,
            oids.SNMP_IF_DESCR,
            oids.CUSTOM_PRIVATE_MIB_BASE
        ]

        for oid in oids_list:
            self.assertIsInstance(oid, tuple, f"OID {oid} is not a tuple")
            self.assertTrue(all(isinstance(x, int) for x in oid), f"OID {oid} contains non-integer values")

    def test_snmp_version_constants(self):
        """Test that SNMP version constants are defined."""
        self.assertTrue(hasattr(oids, 'SNMP_VERSION_1'))
        self.assertTrue(hasattr(oids, 'SNMP_VERSION_2C'))
        self.assertTrue(hasattr(oids, 'SNMP_VERSION_3'))

    def test_snmp_version_values(self):
        """Test that SNMP version constants have correct values."""
        self.assertEqual(oids.SNMP_VERSION_1, 0)
        self.assertEqual(oids.SNMP_VERSION_2C, 1)
        self.assertEqual(oids.SNMP_VERSION_3, 3)


if __name__ == '__main__':
    unittest.main()
