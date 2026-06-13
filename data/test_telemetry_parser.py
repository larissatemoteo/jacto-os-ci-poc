"""Testes do parser de telemetria."""

from telemetry_parser import (
    parse_telemetry_line,
    detect_anomaly,
    process_log,
    max_altitude,
)


def test_parse_valid_line():
    result = parse_telemetry_line("1.0,120.5,2.3")
    assert result["timestamp"] == 1.0
    assert result["altitude"] == 120.5
    assert result["vibration"] == 2.3


def test_parse_invalid_line():
    result = parse_telemetry_line("dados,incompletos")
    assert result is None


def test_detect_anomaly_true():
    record = {"timestamp": 1.0, "altitude": 100.0, "vibration": 8.0}
    assert detect_anomaly(record) is True


def test_detect_anomaly_false():
    record = {"timestamp": 1.0, "altitude": 100.0, "vibration": 3.0}
    assert detect_anomaly(record) is False


def test_process_log():
    lines = ["1.0,100.0,2.0", "2.0,101.0,7.5", "3.0,102.0,1.0"]
    anomalies = process_log(lines)
    assert len(anomalies) == 1
    assert anomalies[0]["vibration"] == 7.5


def test_max_altitude():
    records = [
        {"timestamp": 1.0, "altitude": 100.0, "vibration": 2.0},
        {"timestamp": 2.0, "altitude": 130.5, "vibration": 1.0},
        {"timestamp": 3.0, "altitude": 95.0, "vibration": 3.0},
    ]
    assert max_altitude(records) == 130.5


def test_max_altitude_empty():
    assert max_altitude([]) is None


if __name__ == "__main__":
    test_parse_valid_line()
    test_parse_invalid_line()
    test_detect_anomaly_true()
    test_detect_anomaly_false()
    test_process_log()
    test_max_altitude()
    test_max_altitude_empty()
    print("Todos os testes passaram.")
