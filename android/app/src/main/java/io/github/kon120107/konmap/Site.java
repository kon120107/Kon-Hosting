package io.github.kon120107.konmap;

import android.content.Context;
import android.content.res.AssetManager;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * The KonMap site as the app sees it: files downloaded from GitHub (newer) over the
 * files bundled in the APK (built from the same konmap/ folder).
 * Paths are relative to konmap/, e.g. "cities/turin/city.json".
 */
final class Site {
    final File dir;                 // downloaded files
    private final File stateFile;   // path -> git blob sha of each downloaded file
    private final AssetManager assets;
    final Map<String, String> bundled = new ConcurrentHashMap<>();
    final Map<String, String> downloaded = new ConcurrentHashMap<>();

    Site(Context c) {
        assets = c.getAssets();
        dir = new File(c.getFilesDir(), "site");
        stateFile = new File(c.getFilesDir(), "site-state.json");
        try {
            readInto(bundled, new String(readAll(assets.open("konmap-manifest.json")), StandardCharsets.UTF_8));
        } catch (Exception ignored) { }
        try {
            readInto(downloaded, new String(readAll(new FileInputStream(stateFile)), StandardCharsets.UTF_8));
        } catch (Exception ignored) { }
    }

    private static void readInto(Map<String, String> m, String json) throws Exception {
        JSONObject files = new JSONObject(json).getJSONObject("files");
        for (Iterator<String> it = files.keys(); it.hasNext(); ) {
            String k = it.next();
            m.put(k, files.getString(k));
        }
    }

    /** The sha of the copy the app would serve, or null if it has none. */
    String currentSha(String rel) {
        String d = downloaded.get(rel);
        if (d != null && new File(dir, rel).isFile()) return d;
        return bundled.get(rel);
    }

    InputStream open(String rel) throws IOException {
        if (rel.contains("..")) throw new IOException("bad path");
        File f = new File(dir, rel);
        if (downloaded.containsKey(rel) && f.isFile()) return new FileInputStream(f);
        return assets.open("konmap/" + rel);
    }

    /** Puts a verified download in place (tmp is renamed over the old copy). */
    synchronized void install(String rel, File tmp, String sha) throws IOException {
        File f = new File(dir, rel);
        File parent = f.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new IOException("mkdir " + parent);
        if (!tmp.renameTo(f)) throw new IOException("rename " + f);
        downloaded.put(rel, sha);
        save();
    }

    /** Drops a downloaded copy (the bundled one is current again). */
    synchronized void drop(String rel) {
        downloaded.remove(rel);
        //noinspection ResultOfMethodCallIgnored
        new File(dir, rel).delete();
        save();
    }

    private void save() {
        try {
            JSONObject files = new JSONObject();
            for (Map.Entry<String, String> e : downloaded.entrySet()) files.put(e.getKey(), e.getValue());
            File tmp = new File(stateFile.getPath() + ".tmp");
            try (FileOutputStream o = new FileOutputStream(tmp)) {
                o.write(new JSONObject().put("files", files).toString().getBytes(StandardCharsets.UTF_8));
            }
            //noinspection ResultOfMethodCallIgnored
            tmp.renameTo(stateFile);
        } catch (Exception ignored) { }
    }

    static byte[] readAll(InputStream in) throws IOException {
        try (InputStream i = in) {
            ByteArrayOutputStream o = new ByteArrayOutputStream();
            byte[] b = new byte[16384];
            int n;
            while ((n = i.read(b)) > 0) o.write(b, 0, n);
            return o.toByteArray();
        }
    }
}
