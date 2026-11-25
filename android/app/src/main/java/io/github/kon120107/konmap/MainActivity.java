package io.github.kon120107.konmap;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.GeolocationPermissions;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * KonMap in a full-screen WebView. The page is served from inside the app at
 * https://appassets.androidplatform.net/konmap/ (downloaded updates first, then the bundled copy),
 * and the map libraries and fonts the engine asks the web for are answered from the APK, so
 * everything works offline. Links to other sites open in their own apps.
 */
public class MainActivity extends Activity {
    static final String HOST = "appassets.androidplatform.net";
    static final String START = "https://" + HOST + "/konmap/index.html";
    static final long RECHECK_MS = 60 * 60 * 1000L;

    private WebView web;
    private Site site;
    private SharedPreferences prefs;
    private volatile boolean updating;
    private long lastCheck;
    private GeolocationPermissions.Callback geoCallback;
    private String geoOrigin;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);
        prefs = getSharedPreferences("konmap", MODE_PRIVATE);
        site = new Site(this);

        web = new WebView(this);
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setGeolocationEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setSupportMultipleWindows(false);   // target=_blank opens in place, then goes out below
        s.setMediaPlaybackRequiresUserGesture(true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                return serve(req);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (HOST.equals(u.getHost())) return false;
                String scheme = u.getScheme() == null ? "" : u.getScheme();
                if (scheme.equals("about") || scheme.equals("blob") || scheme.equals("data")) return false;
                openOutside(u);
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback cb) {
                if (hasLocation()) { cb.invoke(origin, true, false); return; }
                geoOrigin = origin;
                geoCallback = cb;
                requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION}, 1);
            }
        });

        if (saved == null || web.restoreState(saved) == null) web.loadUrl(START);
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        long now = System.currentTimeMillis();
        if (!updating && now - lastCheck > RECHECK_MS) {
            lastCheck = now;
            updating = true;
            new Thread(() -> {
                int n = new Updater(site, prefs).run();
                updating = false;
                if (n > 0) runOnUiThread(this::showUpdated);
            }, "konmap-update").start();
        }
    }

    @Override
    protected void onPause() {
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        // The page closes its own open layer (guide, help, place card) if it has one; see konmapBack in the engine.
        web.evaluateJavascript("(function(){try{return !!(window.konmapBack&&window.konmapBack());}catch(e){return false;}})()",
                v -> { if (!"true".equals(v)) goBackOrLeave(); });
    }

    @SuppressWarnings("deprecation")
    private void goBackOrLeave() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] results) {
        if (geoCallback != null) {
            geoCallback.invoke(geoOrigin, hasLocation(), false);
            geoCallback = null;
        }
    }

    private boolean hasLocation() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private void openOutside(Uri u) {
        try {
            Intent i = "intent".equals(u.getScheme())
                    ? Intent.parseUri(u.toString(), Intent.URI_INTENT_SCHEME)
                    : new Intent(Intent.ACTION_VIEW, u);
            i.addCategory(Intent.CATEGORY_BROWSABLE);
            startActivity(i);
        } catch (ActivityNotFoundException | java.net.URISyntaxException ignored) { }
    }

    /** A small bar at the bottom of the page: new files are in, reload to use them. */
    private void showUpdated() {
        web.evaluateJavascript("(function(){if(document.getElementById('kmUpd'))return;"
                + "var d=document.createElement('div');d.id='kmUpd';"
                + "d.style.cssText='position:fixed;left:12px;right:12px;bottom:16px;z-index:2147483647;background:#1d1d1f;color:#fff;"
                + "font:14px system-ui,sans-serif;padding:10px 8px 10px 14px;border-radius:10px;display:flex;align-items:center;gap:4px;box-shadow:0 4px 16px rgba(0,0,0,.35)';"
                + "var t=document.createElement('span');t.textContent='Map updated';t.style.flex='1';d.appendChild(t);"
                + "function btn(l,f){var b=document.createElement('button');b.textContent=l;"
                + "b.style.cssText='background:none;border:0;color:#7cc4ff;font:600 14px system-ui,sans-serif;padding:6px 10px';b.onclick=f;d.appendChild(b);}"
                + "btn('Later',function(){d.remove();});btn('Reload',function(){location.reload();});"
                + "document.body.appendChild(d);})()", null);
    }

    private WebResourceResponse serve(WebResourceRequest req) {
        if (!"GET".equalsIgnoreCase(req.getMethod())) return null;
        Uri u = req.getUrl();
        String host = u.getHost(), path = u.getPath();
        if (host == null || path == null) return null;
        try {
            if (HOST.equals(host)) {
                if (!path.startsWith("/konmap/")) return missing();
                String rel = path.substring("/konmap/".length());
                if (rel.isEmpty() || rel.endsWith("/")) rel += "index.html";
                return ok(mime(rel), site.open(rel));
            }
            // Libraries and fonts the engine loads from the web, kept in the APK under their URL.
            InputStream in;
            try {
                in = getAssets().open("vendor/web/" + host + path);
            } catch (IOException notBundled) {
                return null;   // let the network have it
            }
            return ok(host.equals("fonts.googleapis.com") ? "text/css" : mime(path), in);
        } catch (IOException e) {
            return missing();
        }
    }

    private static WebResourceResponse ok(String mime, InputStream in) {
        Map<String, String> h = new HashMap<>();
        h.put("Access-Control-Allow-Origin", "*");
        h.put("Cache-Control", "no-cache");
        return new WebResourceResponse(mime, "UTF-8", 200, "OK", h, in);
    }

    private static WebResourceResponse missing() {
        Map<String, String> h = new HashMap<>();
        h.put("Access-Control-Allow-Origin", "*");
        return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", h, new ByteArrayInputStream(new byte[0]));
    }

    private static String mime(String p) {
        p = p.toLowerCase();
        if (p.endsWith(".html")) return "text/html";
        if (p.endsWith(".json")) return "application/json";
        if (p.endsWith(".js")) return "application/javascript";
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".woff2")) return "font/woff2";
        if (p.endsWith(".png")) return "image/png";
        if (p.endsWith(".jpg") || p.endsWith(".jpeg")) return "image/jpeg";
        if (p.endsWith(".svg")) return "image/svg+xml";
        if (p.endsWith(".webp")) return "image/webp";
        return "application/octet-stream";
    }
}
