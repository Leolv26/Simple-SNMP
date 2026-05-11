"""SNMP Agent module entry point.

Run with: python -m snmp_monitor.agent
"""
import signal
import sys
import logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    from snmp_monitor.agent.server import SNMPAgentServer

    server = SNMPAgentServer()

    def shutdown(signum, frame):
        logger.info("Received signal, shutting down...")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Starting SNMP Agent server...")
    server.start()


if __name__ == "__main__":
    main()
