"""SNMP client wrapper for SNMP operations."""
import logging
from typing import Optional, List, Tuple, Dict, Any
import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    getCmd, nextCmd, bulkCmd, ObjectType, OctetString
)
from pysnmp.smi.rfc1902 import ObjectIdentity
from pysnmp.proto import rfc1902
from snmp_monitor.nms import oids

logger = logging.getLogger(__name__)


class SNMPClient:
    """SNMP client wrapper for SNMP operations."""

    def __init__(
        self,
        host: str,
        port: int = 1161,
        community: str = 'public',
        version: int = oids.SNMP_VERSION_2C,
        timeout: int = 5,
        retries: int = 2
    ):
        """
        Initialize SNMP client.

        Args:
            host: Target host IP address or hostname
            port: Target SNMP port (default: 1161, must match agent port)
            community: SNMP community string
            version: SNMP version (1, 2C, or 3)
            timeout: Timeout in seconds
            retries: Number of retries
        """
        self.host = host
        self.port = port
        self.community = community
        self.version = version
        self.timeout = timeout
        self.retries = retries

    def _get_community_data(self) -> CommunityData:
        """Get community data based on SNMP version."""
        if self.version == oids.SNMP_VERSION_1:
            return CommunityData(self.community, mpModel=0)
        elif self.version == oids.SNMP_VERSION_2C:
            return CommunityData(self.community, mpModel=1)
        else:
            return CommunityData(self.community, mpModel=1)  # Default to v2c

    async def _get_async(self, oid: Tuple[int, ...]) -> Optional[Tuple]:
        """Async implementation of SNMP GET operation."""
        snmp_engine = SnmpEngine()
        try:
            community_data = self._get_community_data()
            transport_target = UdpTransportTarget((self.host, self.port), timeout=self.timeout, retries=self.retries)
            context_data = ContextData()

            error_indication, error_status, error_index, var_binds = await getCmd(
                snmp_engine,
                community_data,
                transport_target,
                context_data,
                ObjectType(ObjectIdentity(oid))
            )

            if error_indication:
                raise Exception(f"SNMP error: {error_indication}")

            if error_status:
                return None

            if var_binds:
                oid_value, value = var_binds[0]
                return (tuple(oid_value), str(value))

            return None

        except Exception as e:
            raise Exception(f"SNMP GET operation failed: {str(e)}")
        finally:
            snmp_engine.closeDispatcher()

    def get(self, oid: Tuple[int, ...]) -> Optional[Tuple]:
        """
        Perform SNMP GET operation.

        Args:
            oid: SNMP OID as tuple

        Returns:
            Tuple of (OID, value) or None if not found
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._get_async(oid))
            loop.close()
            return result
        except RuntimeError:
            # If already in event loop, just run the coroutine
            return asyncio.run(self._get_async(oid))

    async def _get_next_async(self, oid: Tuple[int, ...]) -> List[Tuple]:
        """Async implementation of SNMP GETNEXT operation."""
        snmp_engine = SnmpEngine()
        try:
            community_data = self._get_community_data()
            transport_target = UdpTransportTarget((self.host, self.port), timeout=self.timeout, retries=self.retries)
            context_data = ContextData()

            results = []
            # nextCmd returns a coroutine, not an async generator
            # We need to await it first, then iterate over the result
            error_indication, error_status, error_index, var_binds_table = await nextCmd(
                snmp_engine,
                community_data,
                transport_target,
                context_data,
                ObjectType(ObjectIdentity(oid))
            )

            # Check for errors
            if error_indication:
                raise Exception(f"SNMP error: {error_indication}")
            elif error_status:
                raise Exception(f"SNMP PDU error: {error_status.prettyPrint()}")

            # Process var_binds_table
            for var_binds in var_binds_table:
                for name, val in var_binds:
                    results.append((tuple(name), str(val)))

            return results

        except Exception as e:
            raise Exception(f"SNMP GETNEXT operation failed: {str(e)}")
        finally:
            snmp_engine.closeDispatcher()

    def get_next(self, oid: Tuple[int, ...]) -> List[Tuple]:
        """
        Perform SNMP GETNEXT operation.

        Args:
            oid: SNMP OID as tuple

        Returns:
            List of (OID, value) tuples
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._get_next_async(oid))
            loop.close()
            return result
        except RuntimeError:
            # If already in event loop, just run the coroutine
            return asyncio.run(self._get_next_async(oid))

    async def _get_bulk_async(self, oid: Tuple[int, ...], non_repeaters: int = 0, max_repetitions: int = 10) -> List[Tuple]:
        """Async implementation of SNMP GETBULK operation."""
        snmp_engine = SnmpEngine()
        try:
            logger.info(f"GETBULK operation started")
            logger.info(f"  Target: {self.host}:{self.port}")
            logger.info(f"  OID: {oid}")
            logger.info(f"  Timeout: {self.timeout}s, Retries: {self.retries}")
            logger.info(f"  Total timeout: {self.timeout * (self.retries + 1)}s")

            community_data = self._get_community_data()
            transport_target = UdpTransportTarget((self.host, self.port), timeout=self.timeout, retries=self.retries)
            context_data = ContextData()

            results = []
            # bulkCmd returns a coroutine, not an async generator
            # We need to await it first, then iterate over the result
            logger.debug(f"Calling bulkCmd with oid={oid}")
            error_indication, error_status, error_index, var_binds_table = await bulkCmd(
                snmp_engine,
                community_data,
                transport_target,
                context_data,
                non_repeaters,
                max_repetitions,
                ObjectType(ObjectIdentity(oid))
            )

            logger.debug(f"bulkCmd completed: error_indication={error_indication}, error_status={error_status}")

            # Check for errors
            if error_indication:
                logger.error(f"SNMP error indication: {error_indication}")
                logger.error(f"  This usually means no response from {self.host}:{self.port}")
                logger.error(f"  Check: 1) Agent is running, 2) Port {self.port} is correct, 3) Firewall allows UDP {self.port}")
                raise Exception(f"SNMP error: {error_indication}")
            elif error_status:
                logger.error(f"SNMP PDU error: {error_status.prettyPrint()}")
                raise Exception(f"SNMP PDU error: {error_status.prettyPrint()}")

            # Process var_binds_table
            logger.debug(f"Processing var_binds_table with {len(var_binds_table)} entries")
            for i, var_binds in enumerate(var_binds_table):
                logger.debug(f"  Entry {i}: {len(var_binds)} varBinds")
                for name, val in var_binds:
                    results.append((tuple(name), str(val)))
                    logger.debug(f"    OID: {tuple(name)}, Value: {str(val)}")

            logger.info(f"GETBULK operation completed successfully: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"GETBULK operation failed: {type(e).__name__}: {str(e)}", exc_info=True)
            raise Exception(f"SNMP GETBULK operation failed: {str(e)}")
        finally:
            snmp_engine.closeDispatcher()

    def get_bulk(self, oid: Tuple[int, ...], non_repeaters: int = 0, max_repetitions: int = 10) -> List[Tuple]:
        """
        Perform SNMP GETBULK operation.

        Args:
            oid: SNMP OID as tuple
            non_repeaters: Number of non-repeater variables
            max_repetitions: Maximum number of repetitions

        Returns:
            List of (OID, value) tuples
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._get_bulk_async(oid, non_repeaters, max_repetitions))
            loop.close()
            return result
        except RuntimeError:
            # If already in event loop, just run the coroutine
            return asyncio.run(self._get_bulk_async(oid, non_repeaters, max_repetitions))

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            Dictionary with system information
        """
        info = {}

        # Get system name
        result = self.get(oids.SNMP_SYSTEM_NAME)
        if result:
            info['hostname'] = result[1]

        # Get system description
        result = self.get(oids.SNMP_SYSTEM_DESCR)
        if result:
            info['description'] = result[1]

        # Get system uptime
        result = self.get(oids.SNMP_SYSTEM_UPTIME)
        if result:
            info['uptime'] = result[1]

        # Get system contact
        result = self.get(oids.SNMP_SYSTEM_CONTACT)
        if result:
            info['contact'] = result[1]

        # Get system location
        result = self.get(oids.SNMP_SYSTEM_LOCATION)
        if result:
            info['location'] = result[1]

        return info

    def get_interface_list(self) -> List[Tuple]:
        """
        Get list of network interfaces.

        Returns:
            List of (OID, interface_name) tuples
        """
        return self.get_next(oids.SNMP_IF_DESCR)

    def get_interface_stats(self, interface_index: int) -> Dict[str, Any]:
        """
        Get statistics for a specific interface.

        Args:
            interface_index: Interface index number

        Returns:
            Dictionary with interface statistics
        """
        stats = {}

        # Get interface type
        oid = oids.SNMP_IF_TYPE + (interface_index,)
        result = self.get(oid)
        if result:
            stats['type'] = result[1]

        # Get interface speed
        oid = oids.SNMP_IF_SPEED + (interface_index,)
        result = self.get(oid)
        if result:
            stats['speed'] = result[1]

        # Get interface admin status
        oid = oids.SNMP_IF_ADMIN_STATUS + (interface_index,)
        result = self.get(oid)
        if result:
            stats['admin_status'] = result[1]

        # Get interface operational status
        oid = oids.SNMP_IF_OPER_STATUS + (interface_index,)
        result = self.get(oid)
        if result:
            stats['oper_status'] = result[1]

        # Get interface inbound octets
        oid = oids.SNMP_IF_IN_OCTETS + (interface_index,)
        result = self.get(oid)
        if result:
            stats['in_octets'] = result[1]

        # Get interface outbound octets
        oid = oids.SNMP_IF_OUT_OCTETS + (interface_index,)
        result = self.get(oid)
        if result:
            stats['out_octets'] = result[1]

        return stats

    def get_process_count(self) -> int:
        """
        Get the number of running processes.

        Returns:
            Process count
        """
        result = self.get(oids.SNMP_PROC_COUNT)
        if result:
            try:
                return int(result[1])
            except ValueError:
                return 0
        return 0

    def get_storage_info(self) -> List[Dict[str, Any]]:
        """
        Get storage information.

        Returns:
            List of storage information dictionaries
        """
        storage_info = []

        # Get storage descriptions
        descr_results = self.get_next(oids.SNMP_STORAGE_DESCR)
        # Get storage sizes
        size_results = self.get_next(oids.SNMP_STORAGE_SIZE)
        # Get storage used
        used_results = self.get_next(oids.SNMP_STORAGE_USED)

        # Combine results
        for i in range(min(len(descr_results), len(size_results), len(used_results))):
            # Extract index from OID
            descr_oid = descr_results[i][0]
            index = descr_oid[-1] if len(descr_oid) > len(oids.SNMP_STORAGE_DESCR) else i + 1

            storage_info.append({
                'path': descr_results[i][1],
                'size': size_results[i][1],
                'used': used_results[i][1],
                'index': index
            })

        return storage_info
