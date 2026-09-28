<%@ page contentType="text/html; charset=UTF-8" import="java.io.*" %><%
    // Sandbox page. Two jobs:
    //  1. show which build is live (BUILD_INFO is written into the WAR by build.xml)
    //  2. simulate a bad release: if the WAR contains a file named BROKEN, answer 500,
    //     so the deploy health check fails and the pipeline auto-rolls back.
    String info = "unknown";
    InputStream in = application.getResourceAsStream("/BUILD_INFO");
    if (in != null) {
        BufferedReader r = new BufferedReader(new InputStreamReader(in, "UTF-8"));
        try { info = r.readLine(); } finally { r.close(); }
    }
    boolean broken = application.getResource("/BROKEN") != null;
    if (broken) {
        response.setStatus(500);
    }
%><!doctype html>
<html>
<head><meta charset="utf-8"><title>ADS Web Tools (sandbox)</title></head>
<body style="font-family: sans-serif; margin: 3rem;">
  <h1>ADS Web Tools <small>(sandbox)</small></h1>
  <p><strong>Build:</strong> <code><%= info %></code></p>
  <p><strong>Status:</strong> <%= broken ? "BROKEN build (returns HTTP 500 on purpose)" : "OK" %></p>
  <p><strong>Served at:</strong> <code><%= new java.util.Date() %></code></p>
</body>
</html>
<!-- v2 -->
