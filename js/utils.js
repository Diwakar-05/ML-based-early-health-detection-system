// Small helpers shared by every page.

/** Show a Bootstrap toast. type: success | danger | warning | info */
function showToast(message, type = "info") {
  let box = document.getElementById("toastBox");
  if (!box) {
    box = document.createElement("div");
    box.id = "toastBox";
    box.className = "toast-container position-fixed top-0 end-0 p-3";
    document.body.appendChild(box);
  }
  const el = document.createElement("div");
  el.className = `toast align-items-center text-bg-${type} border-0`;
  el.setAttribute("role", "alert");
  el.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div>
    <button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
  box.appendChild(el);
  const t = new bootstrap.Toast(el, { delay: 3500 });
  t.show();
  el.addEventListener("hidden.bs.toast", () => el.remove());
}

/** Put a button into / out of a loading state. */
function setLoading(btn, isLoading, text = "Please wait...") {
  if (isLoading) {
    btn.dataset.label = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.label || btn.innerHTML;
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

const isEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);

/** Mark an input valid/invalid and show a message under it. */
function setFieldError(input, message) {
  input.classList.toggle("is-invalid", !!message);
  const fb = input.closest(".mb-3").querySelector(".invalid-feedback");
  if (fb) fb.textContent = message || "";
}

/** Light / dark theme, remembered in localStorage. */
function applyTheme() {
  let saved = "light";
  try { saved = localStorage.getItem("theme") || "light"; } catch (e) {}
  document.documentElement.setAttribute("data-bs-theme", saved);
}
function toggleTheme() {
  const next = document.documentElement.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-bs-theme", next);
  try { localStorage.setItem("theme", next); } catch (e) {}
}
applyTheme();

/** Show/hide password toggle: <button data-toggle-pw="#passwordId"> */
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-toggle-pw]");
  if (!b) return;
  const input = document.querySelector(b.dataset.togglePw);
  input.type = input.type === "password" ? "text" : "password";
  b.querySelector("i").className = input.type === "password" ? "bi bi-eye" : "bi bi-eye-slash";
});