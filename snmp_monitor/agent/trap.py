"""SNMP Trap 发送器与阈值监控器"""
import asyncio
import logging
import time
import threading
from typing import Dict, List, Tuple, Optional

from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, NotificationType, ObjectIdentity, ObjectType, OctetString,
    sendNotification
)

logger = logging.getLogger(__name__)

# SNMPv2c Trap OID (snmpTrapOID)
TRAP_OID = "1.3.6.1.6.3.1.1.5.1"


class TrapSender:
    """Trap 发送器

    使用 pysnmp.hlapi 同步发送，每次调用自带完整引擎生命周期。
    """

    def __init__(self, config_file="config.yaml"):
        self.config = self._load_config(config_file)
        self.target_host = self.config['nms']['agent_host']
        self.target_port = self.config['nms']['trap_port']
        self.community = self.config.get('nms', {}).get('community', 'public')
        logger.info(f"TrapSender: 目标地址 {self.target_host}:{self.target_port}, community={self.community}")

    def _load_config(self, config_file):
        """加载配置文件"""
        import yaml
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def send(self, trap_oid: str, message: str) -> bool:
        """发送 SNMPv2c Trap（同步包装）"""
        try:
            logger.info(f"TrapSender.send: trap_oid={trap_oid}, message={message}")

            async def _async_send():
                return await sendNotification(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.target_host, self.target_port), timeout=5, retries=1),
                    ContextData(),
                    'trap',
                    NotificationType(
                        ObjectIdentity(trap_oid)
                    ).addVarBinds(
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.0'), OctetString(message.encode('ascii')))
                    )
                )

            errorIndication, errorStatus, errorIndex, varBinds = asyncio.run(_async_send())

            if errorIndication:
                logger.error(f"Trap 发送失败 (内部错误): {errorIndication}")
                return False
            elif errorStatus:
                logger.error(f"Trap 发送失败 (协议错误): {errorStatus.prettyPrint()}")
                return False
            else:
                logger.info(f"Trap 发送成功: {trap_oid}")
                return True

        except Exception as e:
            import traceback
            logger.error(f"Trap 发送失败: {type(e).__name__}: {e}")
            logger.error(f"完整堆栈:\n{traceback.format_exc()}")
            return False

    def send_threshold_alert(self, metric: str, value: float, threshold: float):
        """发送阈值告警 Trap"""
        message = f"ALERT: {metric} exceeded threshold! value={value}, threshold={threshold}"
        logger.info(f"TrapSender.send_threshold_alert: metric={metric}, value={value}, threshold={threshold}")
        return self.send(TRAP_OID, message)


class ThresholdMonitor:
    """后台阈值监控线程"""

    def __init__(self, data_collector, trap_sender, thresholds: Dict[str, float],
                 check_interval: float = 10.0, cooldown_duration: float = 300.0):
        self._data_collector = data_collector
        self._trap_sender = trap_sender
        self._thresholds = thresholds
        self._check_interval = check_interval
        self._cooldown_duration = cooldown_duration
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cooldown: Dict[str, float] = {}

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("ThresholdMonitor started")

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("ThresholdMonitor stopped")

    def _run(self):
        logger.info(f"ThresholdMonitor._run 开始循环: interval={self._check_interval}s")
        while self._running:
            logger.info("ThresholdMonitor._run: 执行 _check_once...")
            alerts = self._check_once()
            logger.info(f"ThresholdMonitor._run: 检查结果 alerts={alerts}")
            for metric, value, threshold in alerts:
                logger.info(f"ThresholdMonitor._run: 发送告警 metric={metric}, value={value}, threshold={threshold}")
                result = self._trap_sender.send_threshold_alert(metric, value, threshold)
                logger.info(f"ThresholdMonitor._run: send_threshold_alert 返回 {result}")
            time.sleep(self._check_interval)

    def _check_once(self) -> List[Tuple[str, float, float]]:
        logger.info("ThresholdMonitor._check_once: 采集数据...")
        data = self._data_collector.collect_all_data()
        alerts = []
        system = data.get('system', {})
        current_time = time.time()
        logger.info(f"ThresholdMonitor._check_once: system data={system}")

        cpu = system.get('cpu_percent', 0)
        cpu_threshold = self._thresholds.get('cpu', 100)
        logger.info(f"ThresholdMonitor._check_once: cpu={cpu}, cpu_threshold={cpu_threshold}")
        if cpu > cpu_threshold:
            if self._can_send_alert('cpu', current_time):
                alerts.append(('cpu', cpu, cpu_threshold))
                self._cooldown['cpu'] = current_time
                logger.info(f"ThresholdMonitor._check_once: CPU 超阈值! {cpu} > {cpu_threshold}")

        memory = system.get('memory', {}).get('percent', 0)
        memory_threshold = self._thresholds.get('memory', 100)
        logger.info(f"ThresholdMonitor._check_once: memory={memory}, memory_threshold={memory_threshold}")
        if memory > memory_threshold:
            if self._can_send_alert('memory', current_time):
                alerts.append(('memory', memory, memory_threshold))
                self._cooldown['memory'] = current_time
                logger.info(f"ThresholdMonitor._check_once: Memory 超阈值! {memory} > {memory_threshold}")

        disk = system.get('disk', {}).get('percent', 0)
        disk_threshold = self._thresholds.get('disk', 100)
        logger.info(f"ThresholdMonitor._check_once: disk={disk}, disk_threshold={disk_threshold}")
        if disk > disk_threshold:
            if self._can_send_alert('disk', current_time):
                alerts.append(('disk', disk, disk_threshold))
                self._cooldown['disk'] = current_time
                logger.info(f"ThresholdMonitor._check_once: Disk 超阈值! {disk} > {disk_threshold}")

        logger.info(f"ThresholdMonitor._check_once: 返回 {len(alerts)} 个告警")
        return alerts

    def _can_send_alert(self, metric: str, current_time: float) -> bool:
        last_sent = self._cooldown.get(metric, 0)
        return (current_time - last_sent) >= self._cooldown_duration
