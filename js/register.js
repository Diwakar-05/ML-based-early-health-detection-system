// Register form: validate, call the API, then log the user in.
document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = (id) => document.getElementById(id);
  const btn = f("submitBtn");

  setFieldError(f("name"), f("name").value.trim().length >= 2 ? "" : "Enter your full name.");
  setFieldError(f("email"), isEmail(f("email").value.trim()) ? "" : "Enter a valid email address.");
  setFieldError(f("password"), f("password").value.length >= 8 ? "" : "Password must be at least 8 characters.");
  setFieldError(f("confirm"), f("confirm").value === f("password").value ? "" : "Passwords do not match.");
  if (document.querySelector(".is-invalid")) return;

  setLoading(btn, true, "Creating account...");
  try {
    const data = await Api.register({
      name: f("name").value.trim(), email: f("email").value.trim(), password: f("password").value
    });
    saveSession(data.token, data.user);
    window.location.href = "dashboard.html";
  } catch (err) {
    showToast(err.message, "danger");
    setLoading(btn, false);
  }
});