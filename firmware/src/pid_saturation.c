#include <stdio.h>

/*
 * Funcao de saturacao para limitar a saida de um controlador.
 * Codigo sintetico para demonstracao de CI. Nao representa
 * algoritmo real de controle de voo da Jacto Drones.
 */

float saturate(float value, float min_limit, float max_limit) {
    if (value > max_limit) {
        return max_limit;
    }
    if (value < min_limit) {
        return min_limit;
    }
    return value;
}

float apply_control_output(float raw_output) {
    float limited = saturate(raw_output, -100.0f, 100.0f);
    return limited;
}

/*
 * Rate limiter (slew rate) para a saida do controlador.
 *
 * Limita a taxa de variacao entre dois ciclos de controle para evitar
 * degraus abruptos no comando do atuador, que podem excitar modos
 * mecanicos da estrutura ou saturar a fonte de potencia.
 *
 * Parametros:
 *   previous_output - saida aplicada no ciclo anterior.
 *   target_output   - saida desejada calculada pelo PID neste ciclo.
 *   max_delta       - variacao maxima permitida por ciclo (mesma unidade
 *                     da saida do controlador).
 *
 * Retorna a saida ajustada de modo que |saida - previous_output| <= max_delta.
 */
float rate_limit_output(float previous_output, float target_output, float max_delta) {
    float delta = target_output - previous_output;

    if (delta > max_delta) {
        return previous_output + max_delta;
    }
    if (delta < -max_delta) {
        return previous_output - max_delta;
    }
    return target_output;
}

int main() {
    float test_value = 150.0f;
    float result = apply_control_output(test_value);
    printf("Output limitado: %f\n", result);

    /* Exemplo: saida anterior 0, alvo 100, variacao maxima de 10 por ciclo. */
    float previous = 0.0f;
    float target = 100.0f;
    float max_delta = 10.0f;
    float ramped = rate_limit_output(previous, target, max_delta);
    printf("Output com rate limit: %f\n", ramped);

    return 0;
}
