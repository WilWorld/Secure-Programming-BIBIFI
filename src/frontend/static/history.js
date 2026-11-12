(function () {
  function cameFromHistory() {
    var e = performance.getEntriesByType && performance.getEntriesByType("navigation");
    if (e && e.length) return e[0].type === "back_forward";
    return performance.navigation && performance.navigation.type === 2;
  }

  function leaveGalleryIfNeeded() {
    if (window.location.pathname !== "/") return;
    var form = document.getElementById("leave");
    if (!form) return;
    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      credentials: "same-origin",
      keepalive: true
    }).catch(function () {});
  }

  window.addEventListener("pageshow", function (e) {
    if (e.persisted) leaveGalleryIfNeeded();
  });

  document.addEventListener("DOMContentLoaded", function () {
    if (cameFromHistory()) leaveGalleryIfNeeded();
  });
})();