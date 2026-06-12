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

int main() {
    float test_value = 150.0f;
    float result = apply_control_output(test_value);
    printf("Output limitado: %f\n", result);
    return 0;
}
