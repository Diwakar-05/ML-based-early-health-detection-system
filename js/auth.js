// Login state (JWT in localStorage) and the navbar's auth-aware links.

const getToken = () => { try { return localStorage.getItem("token"); } catch (e) { return null; } };
const getUser  = () => { try { return JSON.parse(localStorage.getItem("user")); } catch (e) { return null; } };

function saveSession(token, user) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "login.html";
}
/** Call at the top of protected pages (dashboard, history). */
function requireAuth() {
  if (!getToken()) window.location.href = "login.html";
}

/** Fills <ul id="navAuth"> with Login/Register or Dashboard/Logout. */
function renderNav() {
  const slot = document.getElementById("navAuth");
  if (!slot) return;
  const user = getUser();
  slot.innerHTML = user
    ? `<li class="nav-item"><a class="nav-link" href="dashboard.html">Dashboard</a></li>
       <li class="nav-item"><button class="btn btn-sm btn-outline-secondary ms-lg-2" onclick="logout()">Log out</button></li>`
    : `<li class="nav-item"><a class="nav-link" href="login.html">Log in</a></li>
       <li class="nav-item"><a class="btn btn-sm btn-brand ms-lg-2" href="register.html">Create account</a></li>`;
}
document.addEventListener("DOMContentLoaded", renderNav);