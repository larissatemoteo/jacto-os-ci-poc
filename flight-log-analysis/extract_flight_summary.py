#!/usr/bin/env python3
"""
Extrator de resumo de log de voo (ULog / PX4-SITL).

Le um arquivo .ulg, extrai os campos relevantes de telemetria, reduz os
milhares de amostras a um resumo estruturado com estatisticas e pontos de
atencao, e emite um JSON compacto pronto para analise por IA.

Uso:
    python extract_flight_summary.py <caminho_do_log.ulg> [--out resumo.json]

Projeto Jacto Drones OS v0.1 - prova de conceito de analise de voo por IA.
"""

import sys
import json
import argparse
import numpy as np
from pyulog import ULog

# Mapeamento de nav_state do PX4 (principais estados)
NAV_STATES = {
    0: "MANUAL", 1: "ALTCTL", 2: "POSCTL", 3: "AUTO_MISSION",
    4: "AUTO_LOITER", 5: "AUTO_RTL", 6: "AUTO_LANDENGFAIL",
    8: "AUTO_LAND", 10: "ACRO", 14: "OFFBOARD", 17: "AUTO_TAKEOFF",
    18: "AUTO_LAND", 19: "AUTO_FOLLOW_TARGET", 20: "AUTO_PRECLAND",
}


def safe_time(raw_ts, start, duration_guard):
    """Converte timestamps para segundos relativos, filtrando invalidos."""
    t = (raw_ts - start) / 1e6
    valid = (t >= 0) & (t < duration_guard)
    return t, valid


def extract(path):
    ulog = ULog(path)
    start = ulog.start_timestamp
    duration = (ulog.last_timestamp - start) / 1e6
    guard = duration + 5  # margem para descartar timestamps zerados/overflow

    summary = {
        "arquivo": path.split("/")[-1],
        "duracao_s": round(duration, 1),
        "sw_version": None,
        "dropouts": len(ulog.dropouts),
        "fases_de_voo": [],
        "altitude": {},
        "velocidade_vertical": {},
        "atitude": {},
        "vibracao": {},
        "bateria": {},
        "gps": {},
        "pontos_de_atencao": [],
    }

    # versao de software
    for k, v in ulog.msg_info_dict.items():
        if k == "ver_sw_release":
            summary["sw_version"] = str(v)

    # --- Fases de voo (transicoes de nav_state) ---
    try:
        vs = ulog.get_dataset("vehicle_status")
        t, valid = safe_time(vs.data["timestamp"], start, guard)
        nav = vs.data["nav_state"][valid]
        t = t[valid]
        prev = None
        for i in range(len(nav)):
            if nav[i] != prev:
                summary["fases_de_voo"].append({
                    "t_s": round(float(t[i]), 1),
                    "estado": NAV_STATES.get(int(nav[i]), f"state_{int(nav[i])}"),
                })
                prev = nav[i]
    except Exception as e:
        summary["fases_de_voo"] = f"indisponivel: {e}"

    # --- Altitude e velocidade vertical ---
    try:
        lp = ulog.get_dataset("vehicle_local_position")
        t, valid = safe_time(lp.data["timestamp"], start, guard)
        alt = -lp.data["z"][valid]  # NED: z negativo = acima
        vz = lp.data["vz"][valid]
        summary["altitude"] = {
            "max_m": round(float(alt.max()), 2),
            "min_m": round(float(alt.min()), 2),
            "media_m": round(float(alt.mean()), 2),
            "inicial_m": round(float(alt[0]), 2),
            "final_m": round(float(alt[-1]), 2),
        }
        summary["velocidade_vertical"] = {
            "max_subida_m_s": round(float(-vz.min()), 2),
            "max_descida_m_s": round(float(vz.max()), 2),
        }
        # ponto de atencao: pouso com altitude final muito acima de zero
        if abs(float(alt[-1])) > 1.0:
            summary["pontos_de_atencao"].append(
                f"Altitude final de {alt[-1]:.2f} m acima da referencia; verificar deteccao de pouso."
            )
    except Exception as e:
        summary["altitude"] = f"indisponivel: {e}"

    # --- Atitude (roll/pitch/yaw em graus, via quaternion) ---
    try:
        att = ulog.get_dataset("vehicle_attitude")
        t, valid = safe_time(att.data["timestamp"], start, guard)
        q0 = att.data["q[0]"][valid]
        q1 = att.data["q[1]"][valid]
        q2 = att.data["q[2]"][valid]
        q3 = att.data["q[3]"][valid]
        # conversao quaternion -> roll, pitch (graus)
        roll = np.degrees(np.arctan2(2*(q0*q1+q2*q3), 1-2*(q1**2+q2**2)))
        pitch = np.degrees(np.arcsin(np.clip(2*(q0*q2-q3*q1), -1, 1)))
        summary["atitude"] = {
            "roll_max_abs_deg": round(float(np.abs(roll).max()), 1),
            "pitch_max_abs_deg": round(float(np.abs(pitch).max()), 1),
        }
        # ponto de atencao: inclinacao agressiva
        max_tilt = max(float(np.abs(roll).max()), float(np.abs(pitch).max()))
        if max_tilt > 30:
            summary["pontos_de_atencao"].append(
                f"Inclinacao maxima de {max_tilt:.1f} graus; acima de 30 graus em voo nominal merece verificacao."
            )
    except Exception as e:
        summary["atitude"] = f"indisponivel: {e}"

    # --- Vibracao (accelerometer magnitude + clipping) ---
    try:
        sc = ulog.get_dataset("sensor_combined")
        ax = sc.data["accelerometer_m_s2[0]"]
        ay = sc.data["accelerometer_m_s2[1]"]
        az = sc.data["accelerometer_m_s2[2]"]
        accel_mag = np.sqrt(ax**2 + ay**2 + az**2)
        clip = int(sc.data["accelerometer_clipping"].sum())
        summary["vibracao"] = {
            "accel_magnitude_media_m_s2": round(float(accel_mag.mean()), 2),
            "accel_magnitude_desvio_padrao": round(float(accel_mag.std()), 2),
            "clipping_accel_eventos": clip,
        }
        # pontos de atencao
        if clip > 0:
            summary["pontos_de_atencao"].append(
                f"{clip} eventos de clipping no acelerometro; indica vibracao excessiva."
            )
        if float(accel_mag.std()) > 2.0:
            summary["pontos_de_atencao"].append(
                f"Desvio padrao de aceleracao de {accel_mag.std():.2f} m/s2; vibracao acima do tipico."
            )
    except Exception as e:
        summary["vibracao"] = f"indisponivel: {e}"

    # --- Bateria ---
    try:
        bat = ulog.get_dataset("battery_status")
        rem = bat.data["remaining"]
        volt = bat.data["voltage_v"]
        summary["bateria"] = {
            "remaining_inicial_pct": round(float(rem[0]) * 100, 1),
            "remaining_final_pct": round(float(rem[-1]) * 100, 1),
            "consumo_pct": round(float(rem[0] - rem[-1]) * 100, 1),
            "voltagem_inicial_v": round(float(volt[0]), 2),
            "voltagem_final_v": round(float(volt[-1]), 2),
        }
        if float(rem[-1]) < 0.2:
            summary["pontos_de_atencao"].append(
                f"Bateria final em {rem[-1]*100:.0f}%; abaixo de 20% e zona de risco."
            )
    except Exception as e:
        summary["bateria"] = f"indisponivel: {e}"

    # --- GPS (numero de satelites, qualidade) ---
    try:
        gps = ulog.get_dataset("vehicle_gps_position")
        nsat = gps.data["satellites_used"]
        summary["gps"] = {
            "satelites_min": int(nsat.min()),
            "satelites_max": int(nsat.max()),
            "satelites_medio": round(float(nsat.mean()), 1),
        }
        if int(nsat.min()) < 6:
            summary["pontos_de_atencao"].append(
                f"Minimo de {int(nsat.min())} satelites; abaixo de 6 compromete a precisao de posicao."
            )
    except Exception as e:
        summary["gps"] = f"indisponivel: {e}"

    if not summary["pontos_de_atencao"]:
        summary["pontos_de_atencao"].append(
            "Nenhum ponto de atencao automatico detectado; metricas dentro de faixas tipicas para voo nominal."
        )

    return summary


def main():
    ap = argparse.ArgumentParser(description="Extrai resumo de log de voo ULog.")
    ap.add_argument("log", help="Caminho do arquivo .ulg")
    ap.add_argument("--out", help="Caminho do JSON de saida (opcional)")
    args = ap.parse_args()

    summary = extract(args.log)
    output = json.dumps(summary, indent=2, ensure_ascii=False)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Resumo salvo em {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
