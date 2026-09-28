package com.example.pit;

/**
 * Minimal compiled class so the WAR has real bytecode for the Java 8 guardrail
 * (war_guardrails.py) to inspect, just like the real app's WEB-INF/classes.
 * Uses only JDK classes, so no servlet-api jar is needed to compile.
 */
public final class BuildInfo {

    private BuildInfo() {
    }

    public static String describe() {
        return "pi-web-tools sandbox, compiled for Java " + System.getProperty("java.specification.version", "?");
    }
}
