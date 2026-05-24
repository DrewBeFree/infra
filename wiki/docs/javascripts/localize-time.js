function localizeDates() {
  function parseUTC(text) {
    var m = text.match(/(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+UTC/);
    if (!m) return null;
    return new Date(m[1] + "T" + m[2] + ":00Z");
  }

  function toLocal(d) {
    return d.toLocaleString(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit", timeZoneName: "short"
    });
  }

  // Footer "Last update" line on every page
  document.querySelectorAll(".md-source-file__fact").forEach(function (el) {
    var d = parseUTC(el.textContent);
    if (!d) return;
    var icon = el.querySelector(".md-icon");
    Array.from(el.childNodes).forEach(function (n) {
      if (n !== icon) el.removeChild(n);
    });
    el.appendChild(document.createTextNode(" " + toLocal(d)));
  });

  // Home page content header: _Last updated: ..._
  document.querySelectorAll("article em").forEach(function (el) {
    var text = el.textContent;
    var d = parseUTC(text);
    if (!d || !/last updated/i.test(text)) return;
    el.textContent = "Last updated: " + toLocal(d);
  });
}

// MkDocs Material with navigation.instant replaces the DOM on every nav —
// document$ fires after each page render; fall back to DOMContentLoaded otherwise.
if (typeof document$ !== "undefined") {
  document$.subscribe(localizeDates);
} else {
  document.addEventListener("DOMContentLoaded", localizeDates);
}
