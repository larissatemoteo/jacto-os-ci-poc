#include <assert.h>
#include <stdio.h>

float saturate(float value, float min_limit, float max_limit);

void test_within_limits() {
    float result = saturate(50.0f, -100.0f, 100.0f);
    assert(result == 50.0f);
    printf("test_within_limits: PASS\n");
}

void test_above_max() {
    float result = saturate(150.0f, -100.0f, 100.0f);
    assert(result == 100.0f);
    printf("test_above_max: PASS\n");
}

void test_below_min() {
    float result = saturate(-150.0f, -100.0f, 100.0f);
    assert(result == -100.0f);
    printf("test_below_min: PASS\n");
}

int main() {
    test_within_limits();
    test_above_max();
    test_below_min();
    printf("Todos os testes passaram.\n");
    return 0;
}
