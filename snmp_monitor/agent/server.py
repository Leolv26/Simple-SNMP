"""SNMP Agent Server using pysnmp CommandResponder."""
import logging
import os
from typing import Dict, Any, Optional, Tuple
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.proto import rfc1902
from pysnmp.proto.api import v2c

from snmp_monitor.agent import handlers
from snmp_monitor.agent import trap as agent_trap
from snmp_monitor.nms import oids

# Try to import yaml for config file reading
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("PyYAML not available, config file reading disabled")


def get_config() -> Dict[str, Any]:
    """Get server configuration.

    Returns:
        Dictionary with configuration values
    """
    # Default configuration
    config_data = {
        'host': '0.0.0.0',
        'port': 161,
        'community': 'public',
        'thresholds': {
            'cpu': 80,
            'memory': 85,
            'disk': 90,
            'check_interval': 10.0,
            'cooldown': 300.0
        }
    }

    # Try to load from config.yaml if it exists and yaml is available
    if YAML_AVAILABLE:
        config_path = 'config.yaml'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        if 'snmp_agent' in yaml_config:
                            config_data.update(yaml_config['snmp_agent'])
                        if 'thresholds' in yaml_config:
                            config_data['thresholds'].update(yaml_config['thresholds'])
            except Exception as e:
                logging.warning(f"Failed to load config from {config_path}: {e}")

    return config_data


class SNMPGetHandler(cmdrsp.GetCommandResponder):
    """Handler for SNMP Get requests."""

    def __init__(self, snmpEngine, snmpContext, data_collector):
        super().__init__(snmpEngine, snmpContext)
        self.data_collector = data_collector

    def handleMgmtOperation(self, snmpEngine, stateReference, contextName, PDU, acInfo):
        """Handle SNMP GET requests with explicit var-bind generation."""
        req_var_binds = v2c.apiPDU.getVarBinds(PDU)
        rsp_var_binds = []

        for oid, _ in req_var_binds:
            rsp_var_binds.append(self._get_var_bind(tuple(oid)))

        self.sendVarBinds(snmpEngine, stateReference, 0, 0, rsp_var_binds)
        self.releaseStateInformation(stateReference)

    def _get_var_bind(self, oid_tuple: Tuple[int, ...]) -> tuple:
        value = _build_oid_value(self.data_collector, oid_tuple)
        if value is None:
            return _no_such_object_var_bind(oid_tuple)
        return _var_bind(oid_tuple, value)


class SNMPGetNextHandler(cmdrsp.NextCommandResponder):
    """Handler for SNMP GetNext requests."""

    def __init__(self, snmpEngine, snmpContext, data_collector):
        super().__init__(snmpEngine, snmpContext)
        self.data_collector = data_collector

    def handleMgmtOperation(self, snmpEngine, stateReference, contextName, PDU, acInfo):
        """Handle SNMP GETNEXT requests against the supported OID set."""
        req_var_binds = v2c.apiPDU.getVarBinds(PDU)
        rsp_var_binds = []

        for oid, _ in req_var_binds:
            rsp_var_binds.append(self._next_var_bind(tuple(oid))[0])

        self.sendVarBinds(snmpEngine, stateReference, 0, 0, rsp_var_binds)
        self.releaseStateInformation(stateReference)

    def _next_var_bind(self, oid_tuple: Tuple[int, ...]) -> Tuple[tuple, Optional[Tuple[int, ...]]]:
        return _next_var_bind_for_collector(self.data_collector, oid_tuple)


class SNMPGetBulkHandler(cmdrsp.BulkCommandResponder):
    """Handler for SNMP GetBulk requests."""

    def __init__(self, snmpEngine, snmpContext, data_collector):
        super().__init__(snmpEngine, snmpContext)
        self.data_collector = data_collector

    def handleMgmtOperation(self, snmpEngine, stateReference, contextName, PDU, acInfo):
        """Handle SNMP GETBULK requests against the supported OID set."""
        non_repeaters = max(0, int(v2c.apiBulkPDU.getNonRepeaters(PDU)))
        max_repetitions = max(0, int(v2c.apiBulkPDU.getMaxRepetitions(PDU)))
        req_var_binds = v2c.apiPDU.getVarBinds(PDU)

        repeaters_start = min(non_repeaters, len(req_var_binds))
        rsp_var_binds = []

        for oid, _ in req_var_binds[:repeaters_start]:
            rsp_var_binds.append(_next_var_bind_for_collector(self.data_collector, tuple(oid))[0])

        repeater_oids = [tuple(oid) for oid, _ in req_var_binds[repeaters_start:]]
        for _ in range(max_repetitions):
            if not repeater_oids:
                break

            next_repeater_oids = []
            active_repeater_found = False

            for current_oid in repeater_oids:
                var_bind, next_oid = _next_var_bind_for_collector(self.data_collector, current_oid)
                rsp_var_binds.append(var_bind)
                next_repeater_oids.append(next_oid if next_oid is not None else current_oid)
                if next_oid is not None:
                    active_repeater_found = True

            if not active_repeater_found:
                break

            repeater_oids = next_repeater_oids

        self.sendVarBinds(snmpEngine, stateReference, 0, 0, rsp_var_binds)
        self.releaseStateInformation(stateReference)


GUI_CPU_OID = (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0)
GUI_MEMORY_OID = (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0)
GUI_DISK_OID = (1, 3, 6, 1, 4, 1, 2021, 4, 7, 0)


def _supported_oids() -> list[Tuple[int, ...]]:
    return sorted([
        oids.SNMP_SYSTEM_DESCR,
        oids.SNMP_SYSTEM_UPTIME,
        oids.SNMP_SYSTEM_CONTACT,
        oids.SNMP_SYSTEM_NAME,
        oids.SNMP_SYSTEM_LOCATION,
        oids.SNMP_PROC_COUNT,
        GUI_CPU_OID,
        GUI_MEMORY_OID,
        GUI_DISK_OID,
        oids.CUSTOM_SYSTEM_LOAD,
    ])


def _next_supported_oid(oid_tuple: Tuple[int, ...]) -> Optional[Tuple[int, ...]]:
    for candidate in _supported_oids():
        if candidate > oid_tuple:
            return candidate
    return None


def _var_bind(oid_tuple: Tuple[int, ...], value) -> tuple:
    return rfc1902.ObjectName(oid_tuple), value


def _no_such_object_var_bind(oid_tuple: Tuple[int, ...]) -> tuple:
    return rfc1902.ObjectName(oid_tuple), v2c.NoSuchObject()


def _end_of_mib_var_bind(oid_tuple: Tuple[int, ...]) -> tuple:
    return rfc1902.ObjectName(oid_tuple), v2c.EndOfMibView()


def _next_var_bind_for_collector(data_collector, oid_tuple: Tuple[int, ...]) -> Tuple[tuple, Optional[Tuple[int, ...]]]:
    next_oid = _next_supported_oid(oid_tuple)
    if next_oid is None:
        return _end_of_mib_var_bind(oid_tuple), None

    return _var_bind(next_oid, _build_oid_value(data_collector, next_oid)), next_oid


def _build_oid_value(data_collector, oid_tuple: Tuple[int, ...]):
    system_handler = data_collector.system_handler
    process_handler = data_collector.process_handler

    if oid_tuple == oids.SNMP_SYSTEM_DESCR:
        return rfc1902.OctetString(f"SNMP Agent on {system_handler.get_hostname()}")
    if oid_tuple == oids.SNMP_SYSTEM_UPTIME:
        return rfc1902.TimeTicks(int(system_handler.get_uptime() * 100))
    if oid_tuple == oids.SNMP_SYSTEM_CONTACT:
        return rfc1902.OctetString("admin@localhost")
    if oid_tuple == oids.SNMP_SYSTEM_NAME:
        return rfc1902.OctetString(system_handler.get_hostname())
    if oid_tuple == oids.SNMP_SYSTEM_LOCATION:
        return rfc1902.OctetString("Unknown")
    if oid_tuple == oids.SNMP_PROC_COUNT:
        return rfc1902.Integer32(int(process_handler.get_process_count()))
    if oid_tuple == GUI_CPU_OID:
        return rfc1902.Gauge32(int(system_handler.get_cpu_percent(interval=0.0)))
    if oid_tuple == GUI_MEMORY_OID:
        return rfc1902.Gauge32(int(system_handler.get_memory_info()['percent']))
    if oid_tuple == GUI_DISK_OID:
        return rfc1902.Gauge32(int(system_handler.get_disk_info()['percent']))
    if oid_tuple == oids.CUSTOM_SYSTEM_LOAD:
        return rfc1902.Gauge32(int(system_handler.get_cpu_percent(interval=0.0)))

    return None


class SNMPAgentServer:
    """SNMP Agent Server using pysnmp CommandResponder."""

    def __init__(self):
        """Initialize SNMP agent server."""
        config_data = get_config()
        self.host = config_data['host']
        self.port = config_data.get('port', 1161)  # Default to 1161 (non-privileged port)
        self.community = config_data['community']

        # Validate port
        if self.port < 1024:
            logging.warning(f"Using privileged port {self.port}. May require root/sudo.")

        # Initialize data collector
        self.data_collector = handlers.SNMPDataCollector()

        # Initialize SNMP engine
        self.snmp_engine = engine.SnmpEngine()

        # Configure transport
        config.addTransport(
            self.snmp_engine,
            udp.domainName,
            udp.UdpTransport().openServerMode((self.host, self.port))
        )

        # Configure community
        config.addV1System(self.snmp_engine, 'my-area', self.community)

        # Create SNMP context
        self.snmp_context = context.SnmpContext(self.snmp_engine)

        # Register handlers
        self.get_handler = SNMPGetHandler(self.snmp_engine, self.snmp_context, self.data_collector)
        self.getnext_handler = SNMPGetNextHandler(self.snmp_engine, self.snmp_context, self.data_collector)
        self.bulk_handler = SNMPGetBulkHandler(self.snmp_engine, self.snmp_context, self.data_collector)

        # Error handler
        self.error_handler = self._handle_error

        logging.info(f"SNMP Agent initialized on {self.host}:{self.port} with community '{self.community}'")

        # Create TrapSender (uses pysnmp.hlapi, independent from agent engine)
        self._trap_sender = agent_trap.TrapSender()

        thresholds_cfg = config_data.get('thresholds', {})

        from snmp_monitor.agent.trap import ThresholdMonitor
        self._threshold_monitor = ThresholdMonitor(
            data_collector=self.data_collector,
            trap_sender=self._trap_sender,
            thresholds=thresholds_cfg,
            check_interval=thresholds_cfg.get('check_interval', 10.0),
            cooldown_duration=thresholds_cfg.get('cooldown', 300.0)
        )

        logging.info(f"ThresholdMonitor initialized (cpu>{thresholds_cfg.get('cpu', 80)}%, "
                     f"mem>{thresholds_cfg.get('memory', 85)}%, "
                     f"disk>{thresholds_cfg.get('disk', 90)}%)")

    def _handle_error(self, error_msg: str):
        """Handle SNMP errors."""
        logging.error(f"SNMP Agent error: {error_msg}")

    def _start_snmp_engine(self):
        """Start the SNMP engine."""
        self.snmp_engine.transportDispatcher.jobStarted(1)

    def _stop_snmp_engine(self):
        """Stop the SNMP engine."""
        self.snmp_engine.transportDispatcher.closeDispatcher()

    def start(self):
        """Start the SNMP agent server."""
        try:
            logging.info(f"Starting SNMP Agent server on {self.host}:{self.port}...")
            logging.info(f"Community: {self.community}")
            self._start_snmp_engine()
            logging.info("SNMP engine started")
            self._threshold_monitor.start()
            logging.info("Threshold monitor started")
            logging.info("Running SNMP engine dispatcher...")
            self.snmp_engine.transportDispatcher.runDispatcher()
        except Exception as e:
            self.error_handler(f"Failed to start server: {str(e)}")
            raise

    def stop(self):
        """Stop the SNMP agent server."""
        try:
            logging.info("Stopping SNMP Agent server...")
            self._threshold_monitor.stop()
            self._stop_snmp_engine()
        except Exception as e:
            self.error_handler(f"Failed to stop server: {str(e)}")
            raise
