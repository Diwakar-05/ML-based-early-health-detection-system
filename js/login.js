// Login form: validate, call the API, store the token, go to the dashboard.
document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  const btn = document.getElementById("submitBtn");

  setFieldError(email, isEmail(email.value.trim()) ? "" : "Enter a valid email address.");
  setFieldError(password, password.value.length >= 8 ? "" : "Password must be at least 8 characters.");
  if (document.querySelector(".is-invalid")) return;

  setLoading(btn, true, "Logging in...");
  try {
    const data = await Api.login({ email: email.value.trim(), password: password.value });
    saveSession(data.token, data.user);
    window.location.href = "dashboard.html";
  } catch (err) {
    showToast(err.message, "danger");
    setLoading(btn, false);
  }
});