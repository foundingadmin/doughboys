/**
 * Drive drop · The First Batch
 *
 * A tiny Apps Script web app that lets a Claude Code session save big files (4K renders, 6704
 * masters, 13 to 20 MB) into the Track Covers folders on Josh's Drive. The Drive connector cannot
 * carry files that size, so pipeline/drive.py posts them here instead.
 *
 * It only writes inside the Track Covers folder tree, and only for a caller that sends the key.
 * Setup is in the-first-batch/docs/drive.md. Script properties:
 *   KEY   a long random string, the same value as the TFB_DRIVE_KEY environment variable
 *   ROOT  the Track Covers folder id, 1g-RHVswNtj1Jp1VKjKmd3OZwDprvnKfB
 *
 * Request body (JSON):
 *   { key, action: "put", folderId, name, mimeType, data (base64), replace (bool) }
 *   { key, action: "list", folderId }
 */

function doPost(e) {
  try {
    var req = JSON.parse(e.postData.contents);
    var props = PropertiesService.getScriptProperties();
    if (!req.key || req.key !== props.getProperty('KEY')) return out({ ok: false, error: 'bad key' });
    var folder = DriveApp.getFolderById(req.folderId);
    if (!insideRoot(folder, props.getProperty('ROOT'))) return out({ ok: false, error: 'folder is outside Track Covers' });

    if (req.action === 'list') {
      var files = [], it = folder.getFiles();
      while (it.hasNext()) {
        var f = it.next();
        files.push({ id: f.getId(), name: f.getName(), bytes: f.getSize(), updated: f.getLastUpdated() });
      }
      return out({ ok: true, folder: folder.getName(), files: files });
    }

    if (req.action === 'put') {
      if (!/^image\/(jpeg|png)$/.test(req.mimeType)) return out({ ok: false, error: 'only jpeg or png' });
      if (!/^[\w .\-]+$/.test(req.name)) return out({ ok: false, error: 'bad file name' });
      var replaced = [];
      if (req.replace) {
        var same = folder.getFilesByName(req.name);
        while (same.hasNext()) { var old = same.next(); replaced.push(old.getId()); old.setTrashed(true); }
      }
      var blob = Utilities.newBlob(Utilities.base64Decode(req.data), req.mimeType, req.name);
      var file = folder.createFile(blob);
      return out({ ok: true, id: file.getId(), name: file.getName(), bytes: file.getSize(), url: file.getUrl(), folder: folder.getName(), trashed: replaced });
    }
    return out({ ok: false, error: 'unknown action' });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

// true when the folder is ROOT or sits below it (track folder, then Masters / Exports / Archive)
function insideRoot(folder, rootId) {
  var queue = [folder];
  for (var depth = 0; depth < 5 && queue.length; depth++) {
    var next = [];
    for (var i = 0; i < queue.length; i++) {
      if (queue[i].getId() === rootId) return true;
      var parents = queue[i].getParents();
      while (parents.hasNext()) next.push(parents.next());
    }
    queue = next;
  }
  return false;
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
