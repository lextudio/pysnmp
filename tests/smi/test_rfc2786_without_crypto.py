"""Regression tests for issue #250: MIB loading without cryptography.

These tests verify that PySNMP can load all bundled MIB modules, including
SNMP-USM-DH-OBJECTS-MIB, without requiring the ``cryptography`` package.

The ``cryptography`` package should only be required when actual DH key
generation is performed, not for MIB loading or parameter encoding/decoding.
"""

import sys
import unittest
from unittest import mock


class TestRfc2786WithoutCryptography(unittest.TestCase):
    """Test RFC 2786 implementation without cryptography installed."""

    def test_import_rfc2786_without_crypto(self):
        """Test that rfc2786 module can be imported without cryptography."""
        # Temporarily remove cryptography from imported modules
        original_cryptography = sys.modules.pop("cryptography", None)
        original_cryptography_backends = sys.modules.pop(
            "cryptography.hazmat.backends", None
        )
        original_cryptography_dh = sys.modules.pop(
            "cryptography.hazmat.primitives.asymmetric.dh", None
        )

        try:
            # Also remove the rfc2786 module to force re-import
            sys.modules.pop("pysnmp.proto.secmod.rfc2786", None)

            # Block cryptography imports
            import builtins

            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name.startswith("cryptography"):
                    raise ImportError(f"Mocked import error: No module named '{name}'")
                return original_import(name, *args, **kwargs)

            with mock.patch("builtins.__import__", side_effect=mock_import):
                # Re-import rfc2786
                from pysnmp.proto.secmod import rfc2786

                # Verify module loaded successfully
                self.assertTrue(hasattr(rfc2786, "DHParameters"))
                self.assertTrue(hasattr(rfc2786, "get_default_parameters"))
                self.assertTrue(hasattr(rfc2786, "decode_parameters"))
                self.assertTrue(hasattr(rfc2786, "encode_parameters"))
                self.assertTrue(hasattr(rfc2786, "compute_shared_secret"))
                self.assertTrue(hasattr(rfc2786, "derive_key"))
        finally:
            # Restore original modules
            if original_cryptography is not None:
                sys.modules["cryptography"] = original_cryptography
            if original_cryptography_backends is not None:
                sys.modules["cryptography.hazmat.backends"] = (
                    original_cryptography_backends
                )
            if original_cryptography_dh is not None:
                sys.modules["cryptography.hazmat.primitives.asymmetric.dh"] = (
                    original_cryptography_dh
                )

    def test_dh_parameters_work_without_crypto(self):
        """Test that DHParameters and related functions work without cryptography."""
        from pysnmp.proto.secmod.rfc2786 import (
            DHParameters,
            compute_shared_secret,
            decode_parameters,
            encode_parameters,
            get_default_parameters,
            int_to_bytes,
            bytes_to_int,
        )

        # Test get_default_parameters
        params = get_default_parameters()
        self.assertIsInstance(params, DHParameters)
        self.assertEqual(params.g, 2)
        self.assertGreater(params.p, 0)

        # Test encode/decode round-trip
        encoded = encode_parameters(params, private_value_length=1024)
        decoded = decode_parameters(encoded)
        self.assertEqual(decoded.p, params.p)
        self.assertEqual(decoded.g, params.g)

        # Test compute_shared_secret (pure math, no crypto needed)
        private_int = 12345
        public_int = pow(params.g, private_int, params.p)
        p_byte_len = (params.p.bit_length() + 7) // 8
        public_bytes = int_to_bytes(public_int, p_byte_len)

        shared = compute_shared_secret(params, private_int, public_bytes)
        self.assertIsInstance(shared, bytes)
        self.assertEqual(len(shared), p_byte_len)

    def test_generate_key_pair_raises_without_crypto(self):
        """Test that generate_key_pair raises ImportError without cryptography."""
        from pysnmp.proto.secmod.rfc2786 import get_default_parameters

        params = get_default_parameters()

        # Block cryptography imports
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name.startswith("cryptography"):
                raise ImportError(f"Mocked import error: No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=mock_import):
            from pysnmp.proto.secmod import rfc2786

            with self.assertRaises(ImportError) as ctx:
                rfc2786.generate_key_pair(params)

            self.assertIn("cryptography", str(ctx.exception))
            self.assertIn("pip install pysnmp[crypto]", str(ctx.exception))


class TestMibLoadingWithoutCryptography(unittest.TestCase):
    """Test MIB loading without cryptography installed."""

    def test_load_mib_modules_without_crypto(self):
        """Test that MibBuilder.load_modules() works without cryptography.

        This is the exact reproduction case from issue #250.
        """
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name.startswith("cryptography"):
                raise ImportError(f"Mocked import error: No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=mock_import):
            # Remove any cached rfc2786 module
            sys.modules.pop("pysnmp.proto.secmod.rfc2786", None)

            from pysnmp.smi import builder

            mib_builder = builder.MibBuilder()
            # This should not raise an exception
            mib_builder.load_modules()


if __name__ == "__main__":
    unittest.main()
