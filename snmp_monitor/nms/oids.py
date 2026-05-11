"""SNMP OID constant definitions for network management system."""

# SNMP Version constants
SNMP_VERSION_1 = 0
SNMP_VERSION_2C = 1
SNMP_VERSION_3 = 3

# System OIDs (RFC 1213-MIB)
SNMP_SYSTEM_DESCR = (1, 3, 6, 1, 2, 1, 1, 1, 0)  # sysDescr
SNMP_SYSTEM_UPTIME = (1, 3, 6, 1, 2, 1, 1, 3, 0)  # sysUpTime
SNMP_SYSTEM_CONTACT = (1, 3, 6, 1, 2, 1, 1, 4, 0)  # sysContact
SNMP_SYSTEM_NAME = (1, 3, 6, 1, 2, 1, 1, 5, 0)    # sysName
SNMP_SYSTEM_LOCATION = (1, 3, 6, 1, 2, 1, 1, 6, 0)  # sysLocation

# Interface OIDs (RFC 1213-MIB)
SNMP_IF_DESCR = (1, 3, 6, 1, 2, 1, 2, 2, 1, 2)      # ifDescr table
SNMP_IF_TYPE = (1, 3, 6, 1, 2, 1, 2, 2, 1, 3)       # ifType table
SNMP_IF_SPEED = (1, 3, 6, 1, 2, 1, 2, 2, 1, 5)      # ifSpeed table
SNMP_IF_ADMIN_STATUS = (1, 3, 6, 1, 2, 1, 2, 2, 1, 7)  # ifAdminStatus table
SNMP_IF_OPER_STATUS = (1, 3, 6, 1, 2, 1, 2, 2, 1, 8)   # ifOperStatus table
SNMP_IF_IN_OCTETS = (1, 3, 6, 1, 2, 1, 2, 2, 1, 10)  # ifInOctets table
SNMP_IF_OUT_OCTETS = (1, 3, 6, 1, 2, 1, 2, 2, 1, 16)  # ifOutOctets table

# Process OIDs
SNMP_PROC_COUNT = (1, 3, 6, 1, 4, 1, 9, 9, 10, 1, 1, 1, 1)  # hrProcesses

# Storage OIDs (RFC 1213-MIB)
SNMP_STORAGE_DESCR = (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 3)  # hrStorageDescr table
SNMP_STORAGE_SIZE = (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 5)   # hrStorageSize table
SNMP_STORAGE_USED = (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 6)   # hrStorageUsed table

# Custom Private MIB Base (under private enterprise OID)
CUSTOM_PRIVATE_MIB_BASE = (1, 3, 6, 1, 4, 1, 99999)

# Custom OIDs for extended monitoring
CUSTOM_IF_ERROR_COUNT = CUSTOM_PRIVATE_MIB_BASE + (1, 1)      # Interface error count
CUSTOM_IF_DISCARD_COUNT = CUSTOM_PRIVATE_MIB_BASE + (1, 2)    # Interface discard count
CUSTOM_SYSTEM_LOAD = CUSTOM_PRIVATE_MIB_BASE + (2, 1)         # Custom system load metric
