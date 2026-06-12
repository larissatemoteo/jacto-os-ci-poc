"""
Parser de log de telemetria sintetico para demonstracao de CI.
Nao processa dados reais da Jacto Drones.
"""


def parse_telemetry_line(line):
    """Converte uma linha de log em dicionario de telemetria."""
    parts = line.strip().split(",")
    if len(parts) != 3:
        return None
    return {
        "timestamp": float(parts[0]),
        "altitude": float(parts[1]),
        "vibration": float(parts[2]),
    }


def detect_anomaly(record, vibration_threshold=5.0):
    """Retorna True se a vibracao exceder o limiar definido."""
    if record is None:
        return False
    return record["vibration"] > vibration_threshold


def process_log(lines):
    """Processa uma lista de linhas e retorna registros anomalos."""
    anomalies = []
    for line in lines:
        record = parse_telemetry_line(line)
        if detect_anomaly(record):
            anomalies.append(record)
    return anomalies
