let keyPressTimer = null;
let navigationInterval = null;

function goToHref(el) {
  if (!el) return;
  const href = el.getAttribute("href");
  if (href === "#") return;
  window.location.href = href;
}

function startNavigation(direction) {
  if (direction === "left") {
    keyPressTimer = setTimeout(() => {
      navigationInterval = setInterval(() => {
        goToHref(document.querySelector("a.prev-button"));
      }, 50);
    }, 100);
  } else if (direction === "right") {
    keyPressTimer = setTimeout(() => {
      navigationInterval = setInterval(() => {
        goToHref(document.querySelector("a.next-button"));
      }, 50);
    }, 100);
  }
}

function stopNavigation() {
  clearTimeout(keyPressTimer);
  clearInterval(navigationInterval);
}

window.addEventListener("keydown", function (evt) {
  switch (evt.key) {
    case "ArrowLeft":
      if (!keyPressTimer && !navigationInterval) {
        startNavigation("left");
      }
      break;
    case "ArrowRight":
      if (!keyPressTimer && !navigationInterval) {
        startNavigation("right");
      }
      break;
    default:
      break;
  }
});

window.addEventListener("keyup", function (evt) {
  stopNavigation();
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
let debounceTimeout;
function debouncedUpdate(evt) {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    var scroll = window.scrollY;
    var height = document.body.scrollHeight - window.innerHeight + 10;
    var percent = Math.round((100.0 * scroll) / height);
    document.getElementById("readpos").innerText = percent + "%";
  }, 100); // 100ms delay
}

window.addEventListener("scroll", debouncedUpdate);

window.addEventListener("load", function (evt) {
  addTocSelectListener();
});
