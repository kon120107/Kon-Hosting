package io.github.kon120107.konmap;

import android.content.SharedPreferences;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * Brings the app's copy of konmap/ up to date with GitHub.
 *
 * One request lists every file in the repo with its git blob sha (answered with 304, and not
 * counted against GitHub's rate limit, when nothing changed since the last complete update).
 * Files whose sha differs from the app's copy are downloaded from the GitHub Pages site,
 * checked against that sha, and only then put in place. Anything that fails is retried next time.
 */
final class Updater {
    static final String OWNER_REPO = "kon120107/Kon-Hosting";
    static final String BRANCH = "main";
    static final String FOLDER = "konmap/";
    static final String PAGES = "https://kon120107.github.io/Kon-Hosting/konmap/";
    static final String RAW = "https://raw.githubusercontent.com/" + OWNER_REPO + "/" + BRANCH + "/konmap/";

    private final Site site;
    private final SharedPreferences prefs;

    Updater(Site site, SharedPreferences prefs) {
        this.site = site;
        this.prefs = prefs;
    }

    /** Same filter as the Gradle task that bundles the site. */
    static boolean wanted(String rel) {
        return !(rel.startsWith("raw/") || rel.startsWith("tools/") || rel.endsWith(".md")
                || rel.endsWith("curation.json") || rel.contains("__pycache__") || rel.endsWith(".py") || rel.endsWith(".pyc"));
    }

    /** Returns how many files changed. Never throws. */
    int run() {
        int changed = 0;
        try {
            String etagKey = "treeEtag." + BuildConfig.VERSION_CODE;
            HttpURLConnection c = open("https://api.github.com/repos/" + OWNER_REPO + "/git/trees/" + BRANCH + "?recursive=1");
            c.setRequestProperty("Accept", "application/vnd.github+json");
            String etag = prefs.getString(etagKey, null);
            if (etag != null) c.setRequestProperty("If-None-Match", etag);
            int code = c.getResponseCode();
            if (code == 304) { c.disconnect(); return 0; }
            if (code != 200) { c.disconnect(); return 0; }
            String newEtag = c.getHeaderField("ETag");
            JSONObject tree = new JSONObject(new String(Site.readAll(c.getInputStream()), StandardCharsets.UTF_8));
            c.disconnect();

            boolean complete = !tree.optBoolean("truncated", false);
            JSONArray items = tree.getJSONArray("tree");
            for (int i = 0; i < items.length(); i++) {
                JSONObject it = items.getJSONObject(i);
                String path = it.optString("path");
                if (!"blob".equals(it.optString("type")) || !path.startsWith(FOLDER)) continue;
                String rel = path.substring(FOLDER.length());
                if (!wanted(rel)) continue;
                String sha = it.getString("sha");
                if (sha.equals(site.currentSha(rel))) continue;
                if (sha.equals(site.bundled.get(rel))) { site.drop(rel); changed++; continue; }
                if (fetch(rel, sha, PAGES) || fetch(rel, sha, RAW)) changed++;
                else complete = false;
            }
            if (complete && newEtag != null) prefs.edit().putString(etagKey, newEtag).apply();
        } catch (Exception ignored) {
            // offline or bad network: keep what we have
        }
        return changed;
    }

    private boolean fetch(String rel, String sha, String base) {
        File tmp = new File(site.dir.getParentFile(), "download.tmp");
        try {
            HttpURLConnection c = open(base + encodePath(rel));
            if (c.getResponseCode() != 200) { c.disconnect(); return false; }
            long len = 0;
            try (InputStream in = c.getInputStream(); FileOutputStream out = new FileOutputStream(tmp)) {
                byte[] b = new byte[65536];
                int n;
                while ((n = in.read(b)) > 0) { out.write(b, 0, n); len += n; }
            } finally {
                c.disconnect();
            }
            // git blob sha = sha1("blob <length>\0" + content)
            MessageDigest blob = MessageDigest.getInstance("SHA-1");
            blob.update(("blob " + len + "\0").getBytes(StandardCharsets.UTF_8));
            try (InputStream in = new java.io.FileInputStream(tmp)) {
                byte[] b = new byte[65536];
                int n;
                while ((n = in.read(b)) > 0) blob.update(b, 0, n);
            }
            if (!sha.equals(hex(blob.digest()))) return false;   // stale cache or broken download
            site.install(rel, tmp, sha);
            return true;
        } catch (Exception e) {
            return false;
        } finally {
            //noinspection ResultOfMethodCallIgnored
            tmp.delete();
        }
    }

    private static HttpURLConnection open(String url) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(15000);
        c.setReadTimeout(30000);
        c.setRequestProperty("User-Agent", "KonMap-Android");
        c.setUseCaches(false);
        return c;
    }

    private static String encodePath(String rel) throws IOException {
        StringBuilder s = new StringBuilder();
        for (String part : rel.split("/")) {
            if (s.length() > 0) s.append('/');
            s.append(java.net.URLEncoder.encode(part, "UTF-8").replace("+", "%20"));
        }
        return s.toString();
    }

    private static String hex(byte[] d) {
        StringBuilder s = new StringBuilder();
        for (byte x : d) s.append(String.format("%02x", x));
        return s.toString();
    }
}
