document.querySelectorAll("a[data-visit-form]").forEach(function (link) {
  link.addEventListener("click", function (e) {
    if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    var form = document.getElementById(link.dataset.visitForm);
    if (!form) return;
    e.preventDefault();
    form.submit();
  });
});