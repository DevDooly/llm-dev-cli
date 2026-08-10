package com.example.ai.logging;

import lombok.extern.slf4j.Slf4j;
import net.logstash.logback.argument.StructuredArguments;
import org.springframework.stereotype.Component;
import java.util.Map;

@Slf4j
@Component
public class LlmAuditLogger {

    public void logLlmTransaction(
            String model,
            String prompt,
            String response,
            int promptTokens,
            int completionTokens,
            long durationMs,
            double costUsd) {

        Map<String, Object> llmData = Map.of(
            "provider", "google",
            "model", model,
            "prompt", maskPii(prompt),
            "completion", maskPii(response),
            "usage", Map.of(
                "prompt_tokens", promptTokens,
                "completion_tokens", completionTokens,
                "total_tokens", promptTokens + completionTokens,
                "estimated_cost_usd", costUsd
            ),
            "latency_ms", durationMs
        );

        log.info("LLM Transaction Completed", StructuredArguments.entries(Map.of("llm", llmData)));
    }

    private String maskPii(String text) {
        if (text == null) return "";
        return text.replaceAll("(?i)\\b\\d{6}-[1-4]\\d{6}\\b", "[REDACTED_RRN]");
    }
}
