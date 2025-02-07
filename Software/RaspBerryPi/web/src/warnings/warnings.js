document.addEventListener("DOMContentLoaded", function () {
  const urlParams = new URLSearchParams(window.location.search);

  // Gestione degli errori
  const errorParam = urlParams.get("error");
  if (errorParam && errorParam !== "") {
    showMessagePopup(errorParam, "error");
    clearUrlParam("error");
  }

  // Gestione dei successi
  const successParam = urlParams.get("success");
  if (successParam && successParam !== "") {
    showMessagePopup(successParam, "success");
    clearUrlParam("success");
  }

  // Gestione dei successi con display
  const displayParam = urlParams.get("display");
  if (displayParam && displayParam !== "") {
    showDisplay();
    clearUrlParam("display");
  }
});

function showMessagePopup(message, messageType) {
  const modal = document.createElement("div");
  modal.className = `${messageType}-modal`;
  modal.innerHTML = `<p>${message}</p>`;

  document.body.appendChild(modal);
  modal.style.display = "block";

  setTimeout(function () {
    modal.style.top = "10px";
  }, 50);

  setTimeout(function () {
    modal.style.top = "-100px";
  }, 2000);
}

function showDisplay() {
  const overlay = document.createElement("div");
  overlay.className = "overlay";
  document.body.appendChild(overlay);
  overlay.style.display = "block";

  setTimeout(function () {
    overlay.style.display = "none";
  }, 5000);
}

function clearUrlParam(paramName) {
  const newUrl = window.location.pathname + window.location.search.replace(new RegExp(`(\\?|&)${paramName}=[^&]*(&|$)`), '$1');
  history.replaceState({}, document.title, newUrl);
}