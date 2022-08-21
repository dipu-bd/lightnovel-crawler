// Handle key events
window.addEventListener("keyup", function (evt) {
  function goToHref(el) {
    if (!el) return;
    const href = el.getAttribute("href");
    if (href === "#") return;
    window.location.href = href;
  }

  switch (evt.key) {
    case "ArrowLeft":
      goToHref(document.querySelector("a.prev-button"));
      break;
    case "ArrowRight":
      goToHref(document.querySelector("a.next-button"));
      break;
    default:
      break;
  }
});

// Handle next TOC select
function addTocSelectListener() {
  document.querySelectorAll("select.toc").forEach((select) => {
    select.addEventListener("input", (evt) => {
      window.location.href = evt.currentTarget.value;
    });
  });
}

// Handle update reading progress on scroll
window.addEventListener("scroll", function (e) {
  try {
    var scroll = window.scrollY;
    var height = document.body.scrollHeight - window.innerHeight + 10;
    var percent = Math.round((100.0 * scroll) / height);
    document.getElementById("readpos").innerText = percent + "%";
  } catch (err) {
    // ignore
  }
});

// Add element wise listeners after page load
window.addEventListener("load", function (evt) {
  addTocSelectListener();
});
