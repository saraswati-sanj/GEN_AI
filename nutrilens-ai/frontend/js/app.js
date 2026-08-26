/**
 * NutriLens AI — Frontend Master Application Logic
 * Integrates Barcode Scanner, Gemini AI Clinical Analysis, JWT Authentication, and Cloud Sync.
 */

const API_BASE = "/api/v1";

// Application State
const state = {
  token: localStorage.getItem("nutrilens_token") || null,
  currentUser: JSON.parse(localStorage.getItem("nutrilens_user") || "null"),
  language: "en",
  scanData: null,
  userProfile: {
    age: 30,
    health_conditions: {
      diabetes: false,
      hypertension: false,
      kidney_disease: false,
      pregnancy: false,
      heart_disease: false,
      obesity: false,
      celiac_disease: false,
    },
    allergies: [],
    preferred_language: "en",
  },
  history: [],
  isCameraActive: false,
};

// DOM Elements Cache
const elements = {
  // Navigation & Language
  languageSelect: document.getElementById("language-select"),
  btnOpenProfile: document.getElementById("btn-open-profile"),
  btnToggleHistory: document.getElementById("btn-toggle-history"),
  profileBadge: document.getElementById("profile-badge"),
  
  // Auth Buttons & Nav Elements
  btnOpenAuth: document.getElementById("btn-open-auth"),
  userNavMenu: document.getElementById("user-nav-menu"),
  btnUserDropdown: document.getElementById("btn-user-dropdown"),
  userDropdownPopover: document.getElementById("user-dropdown-popover"),
  navUserName: document.getElementById("nav-user-name"),
  navUserAvatar: document.getElementById("nav-user-avatar"),
  popoverUserName: document.getElementById("popover-user-name"),
  popoverUserEmail: document.getElementById("popover-user-email"),
  popoverUserAvatar: document.getElementById("popover-user-avatar"),
  btnNavProfile: document.getElementById("btn-nav-profile"),
  btnNavHistory: document.getElementById("btn-nav-history"),
  btnLogout: document.getElementById("btn-logout"),

  // Auth Modal Elements
  authModal: document.getElementById("auth-modal"),
  btnCloseAuth: document.getElementById("btn-close-auth"),
  tabBtnLogin: document.getElementById("tab-btn-login"),
  tabBtnRegister: document.getElementById("tab-btn-register"),
  authAlert: document.getElementById("auth-alert"),
  loginForm: document.getElementById("login-form"),
  registerForm: document.getElementById("register-form"),
  loginEmail: document.getElementById("login-email"),
  loginPassword: document.getElementById("login-password"),
  btnLoginSubmit: document.getElementById("btn-login-submit"),
  linkToRegister: document.getElementById("link-to-register"),
  linkToLogin: document.getElementById("link-to-login"),
  
  regFullname: document.getElementById("reg-fullname"),
  regEmail: document.getElementById("reg-email"),
  regPassword: document.getElementById("reg-password"),
  regAge: document.getElementById("reg-age"),
  regLanguage: document.getElementById("reg-language"),
  regAllergies: document.getElementById("reg-allergies"),
  btnRegisterSubmit: document.getElementById("btn-register-submit"),
  passwordToggleBtns: document.querySelectorAll(".btn-password-toggle"),

  // Scanner Tabs & Viewports
  scanTabBtns: document.querySelectorAll(".scan-tab-btn"),
  modeCamera: document.getElementById("mode-camera"),
  modeUpload: document.getElementById("mode-upload"),
  modeManual: document.getElementById("mode-manual"),
  
  btnStartCamera: document.getElementById("btn-start-camera"),
  btnStopCamera: document.getElementById("btn-stop-camera"),
  cameraOverlayStatus: document.getElementById("camera-overlay-status"),
  
  dropzone: document.getElementById("dropzone"),
  fileInput: document.getElementById("file-input"),
  btnBrowseFile: document.getElementById("btn-browse-file"),
  
  manualForm: document.getElementById("manual-form"),
  manualInput: document.getElementById("manual-barcode-input"),
  sampleChips: document.querySelectorAll(".chip"),
  
  // Loading & Results
  loadingOverlay: document.getElementById("loading-overlay"),
  loadingText: document.getElementById("loading-text"),
  resultsSection: document.getElementById("results-section"),
  
  // Product Header & Gauge
  productImg: document.getElementById("product-img"),
  productName: document.getElementById("product-name"),
  productBrand: document.getElementById("product-brand"),
  productCategory: document.getElementById("product-category"),
  nutriscoreBadge: document.getElementById("nutriscore-badge"),
  novaBadge: document.getElementById("nova-badge"),
  barcodeDisplayBadge: document.getElementById("barcode-display-badge"),
  
  scoreNumber: document.getElementById("score-number"),
  gaugeFill: document.getElementById("gauge-fill"),
  verdictTitle: document.getElementById("verdict-title"),
  adviceBadge: document.getElementById("advice-badge"),
  
  // Result Tabs
  resultTabs: document.querySelectorAll(".result-tab"),
  tabContents: document.querySelectorAll(".tab-content"),
  
  // Tab Containers
  userProfileSummaryBanner: document.getElementById("user-profile-summary-banner"),
  healthRisksGrid: document.getElementById("health-risks-grid"),
  rawIngredientsText: document.getElementById("raw-ingredients-text"),
  ingredientsListContainer: document.getElementById("ingredients-list-container"),
  harmfulIngredientsContainer: document.getElementById("harmful-ingredients-container"),
  additivesContainer: document.getElementById("additives-container"),
  nutritionGrid: document.getElementById("nutrition-grid"),
  fssaiSummaryText: document.getElementById("fssai-summary-text"),
  recommendationsList: document.getElementById("recommendations-list"),
  alternativesContainer: document.getElementById("alternatives-container"),
  
  // Organ Impacts & Toxicity
  organImpactGrid: document.getElementById("organ-impact-grid"),
  impactSeverityPill: document.getElementById("impact-severity-pill"),
  acuteEffectsList: document.getElementById("acute-effects-list"),
  chronicEffectsList: document.getElementById("chronic-effects-list"),
  
  // History & Profile Modals
  historySection: document.getElementById("history-section"),
  historyListContainer: document.getElementById("history-list-container"),
  btnClearHistory: document.getElementById("btn-clear-history"),
  
  profileModal: document.getElementById("profile-modal"),
  btnCloseProfile: document.getElementById("btn-close-profile"),
  profileForm: document.getElementById("profile-form"),
  profileAge: document.getElementById("profile-age"),
  profileAllergies: document.getElementById("profile-allergies"),
  
  toastContainer: document.getElementById("toast-container"),
};

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", async () => {
  loadStoredLocalProfile();
  initEventListeners();
  fetchSampleBarcodes();
  await checkAuthState();
});

// Helper for Authorization Headers
function getAuthHeaders() {
  const headers = {};
  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }
  return headers;
}

// ═══════════════════════════════════════════════════════════════════════════════
// AUTHENTICATION MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════

async function checkAuthState() {
  if (!state.token) {
    updateAuthUI();
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/users/me`, {
      headers: getAuthHeaders(),
    });

    if (res.ok) {
      const userData = await res.json();
      state.currentUser = userData;
      localStorage.setItem("nutrilens_user", JSON.stringify(userData));

      // Sync user profile from server
      state.userProfile.age = userData.age || 30;
      state.userProfile.allergies = userData.allergies || [];
      state.userProfile.health_conditions = userData.health_conditions || state.userProfile.health_conditions;
      state.userProfile.preferred_language = userData.preferred_language || "en";
      state.language = userData.preferred_language || "en";
      elements.languageSelect.value = state.language;

      elements.profileBadge.classList.remove("hidden");
      await loadHistoryFromBackend();
    } else {
      // Token expired or invalid
      handleLogout(false);
    }
  } catch (err) {
    console.warn("Could not verify session with backend:", err);
  } finally {
    updateAuthUI();
  }
}

function updateAuthUI() {
  const isLoggedIn = !!(state.token && state.currentUser);

  if (isLoggedIn) {
    elements.btnOpenAuth.classList.add("hidden");
    elements.userNavMenu.classList.remove("hidden");

    const displayName = state.currentUser.full_name || state.currentUser.email.split("@")[0];
    const initial = (displayName.charAt(0) || "U").toUpperCase();

    elements.navUserName.textContent = displayName;
    elements.popoverUserName.textContent = displayName;
    elements.popoverUserEmail.textContent = state.currentUser.email;

    elements.navUserAvatar.textContent = initial;
    elements.popoverUserAvatar.textContent = initial;
  } else {
    elements.btnOpenAuth.classList.remove("hidden");
    elements.userNavMenu.classList.add("hidden");
    elements.userDropdownPopover.classList.add("hidden");
  }
}

function openAuthModal(defaultTab = "login") {
  hideAuthAlert();
  switchAuthTab(defaultTab);
  elements.authModal.classList.remove("hidden");
  if (defaultTab === "login") {
    elements.loginEmail.focus();
  } else {
    elements.regFullname.focus();
  }
}

function closeAuthModal() {
  elements.authModal.classList.add("hidden");
  hideAuthAlert();
}

function switchAuthTab(tab) {
  hideAuthAlert();
  if (tab === "login") {
    elements.tabBtnLogin.classList.add("active");
    elements.tabBtnRegister.classList.remove("active");
    elements.loginForm.classList.remove("hidden");
    elements.registerForm.classList.add("hidden");
  } else {
    elements.tabBtnRegister.classList.add("active");
    elements.tabBtnLogin.classList.remove("active");
    elements.registerForm.classList.remove("hidden");
    elements.loginForm.classList.add("hidden");
  }
}

function showAuthAlert(message, type = "error") {
  elements.authAlert.className = `auth-alert auth-alert-${type}`;
  elements.authAlert.innerHTML = `<i class="fa-solid ${type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-check'}"></i> <span>${message}</span>`;
  elements.authAlert.classList.remove("hidden");
}

function hideAuthAlert() {
  elements.authAlert.classList.add("hidden");
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = elements.loginEmail.value.trim();
  const password = elements.loginPassword.value;

  if (!email || !password) {
    showAuthAlert("Please enter both email and password.");
    return;
  }

  const submitBtn = elements.btnLoginSubmit;
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Signing in...`;
  hideAuthAlert();

  try {
    const res = await fetch(`${API_BASE}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Authentication failed. Check credentials.");
    }

    // Save token and user details
    state.token = data.access_token;
    state.currentUser = data.user;
    localStorage.setItem("nutrilens_token", data.access_token);
    localStorage.setItem("nutrilens_user", JSON.stringify(data.user));

    // Update profile in state
    state.userProfile.age = data.user.age || 30;
    state.userProfile.allergies = data.user.allergies || [];
    state.userProfile.health_conditions = data.user.health_conditions || state.userProfile.health_conditions;
    state.userProfile.preferred_language = data.user.preferred_language || "en";
    state.language = data.user.preferred_language || "en";
    elements.languageSelect.value = state.language;

    updateAuthUI();
    closeAuthModal();
    showToast(`Welcome back, ${data.user.full_name || email.split("@")[0]}!`, "success");

    // Fetch synced history
    await loadHistoryFromBackend();
  } catch (err) {
    showAuthAlert(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const fullName = elements.regFullname.value.trim();
  const email = elements.regEmail.value.trim();
  const password = elements.regPassword.value;
  const age = parseInt(elements.regAge.value) || 30;
  const language = elements.regLanguage.value || "en";
  const allergies = elements.regAllergies.value.split(",").map(s => s.trim()).filter(Boolean);

  const healthConditions = {
    diabetes: document.getElementById("reg-cond-diabetes").checked,
    hypertension: document.getElementById("reg-cond-hypertension").checked,
    kidney_disease: document.getElementById("reg-cond-kidney").checked,
    pregnancy: document.getElementById("reg-cond-pregnancy").checked,
    heart_disease: document.getElementById("reg-cond-heart").checked,
    celiac_disease: document.getElementById("reg-cond-celiac").checked,
    obesity: false,
  };

  if (!email || !password) {
    showAuthAlert("Please provide both email and password.");
    return;
  }

  if (password.length < 8) {
    showAuthAlert("Password must be at least 8 characters long.");
    return;
  }

  const submitBtn = elements.btnRegisterSubmit;
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Creating account...`;
  hideAuthAlert();

  try {
    const res = await fetch(`${API_BASE}/users/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName || null,
        age,
        health_conditions: healthConditions,
        allergies,
        preferred_language: language,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Registration failed. Please check inputs.");
    }

    state.token = data.access_token;
    state.currentUser = data.user;
    localStorage.setItem("nutrilens_token", data.access_token);
    localStorage.setItem("nutrilens_user", JSON.stringify(data.user));

    state.userProfile.age = age;
    state.userProfile.allergies = allergies;
    state.userProfile.health_conditions = healthConditions;
    state.userProfile.preferred_language = language;
    state.language = language;
    elements.languageSelect.value = language;

    updateAuthUI();
    closeAuthModal();
    showToast(`Account created! Welcome, ${fullName || email.split("@")[0]}!`, "success");
    
    await loadHistoryFromBackend();
  } catch (err) {
    showAuthAlert(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

function handleLogout(showNotification = true) {
  state.token = null;
  state.currentUser = null;
  localStorage.removeItem("nutrilens_token");
  localStorage.removeItem("nutrilens_user");

  state.history = [];
  updateAuthUI();

  if (showNotification) {
    showToast("You have been signed out.", "info");
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// USER PROFILE MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════

function loadStoredLocalProfile() {
  const saved = localStorage.getItem("nutrilens_profile");
  if (saved) {
    try {
      state.userProfile = JSON.parse(saved);
      elements.profileBadge.classList.remove("hidden");
    } catch (e) {
      console.warn("Could not parse saved profile.");
    }
  }
}

async function saveProfile() {
  localStorage.setItem("nutrilens_profile", JSON.stringify(state.userProfile));
  elements.profileBadge.classList.remove("hidden");

  // If user is authenticated, sync to database via PUT /api/v1/users/me
  if (state.token) {
    try {
      const res = await fetch(`${API_BASE}/users/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          age: state.userProfile.age,
          health_conditions: state.userProfile.health_conditions,
          allergies: state.userProfile.allergies,
          preferred_language: state.userProfile.preferred_language || state.language,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        state.currentUser = updated;
        localStorage.setItem("nutrilens_user", JSON.stringify(updated));
        showToast("Profile updated and synced with cloud!", "success");
        return;
      }
    } catch (err) {
      console.warn("Failed to sync profile to server:", err);
    }
  }

  showToast("Health Profile Saved!", "info");
}

function openProfileModal() {
  elements.profileAge.value = state.userProfile.age || 30;
  elements.profileAllergies.value = (state.userProfile.allergies || []).join(", ");
  
  const hc = state.userProfile.health_conditions || {};
  document.getElementById("cond-diabetes").checked = !!hc.diabetes;
  document.getElementById("cond-hypertension").checked = !!hc.hypertension;
  document.getElementById("cond-kidney").checked = !!hc.kidney_disease;
  document.getElementById("cond-pregnancy").checked = !!hc.pregnancy;
  document.getElementById("cond-heart").checked = !!hc.heart_disease;
  document.getElementById("cond-celiac").checked = !!hc.celiac_disease;

  elements.profileModal.classList.remove("hidden");
}

function closeProfileModal() {
  elements.profileModal.classList.add("hidden");
}

async function handleProfileFormSubmit(e) {
  e.preventDefault();
  state.userProfile.age = parseInt(elements.profileAge.value) || 30;
  state.userProfile.allergies = elements.profileAllergies.value.split(",").map(s => s.trim()).filter(Boolean);
  
  state.userProfile.health_conditions = {
    diabetes: document.getElementById("cond-diabetes").checked,
    hypertension: document.getElementById("cond-hypertension").checked,
    kidney_disease: document.getElementById("cond-kidney").checked,
    pregnancy: document.getElementById("cond-pregnancy").checked,
    heart_disease: document.getElementById("cond-heart").checked,
    celiac_disease: document.getElementById("cond-celiac").checked,
    obesity: false,
  };

  await saveProfile();
  closeProfileModal();
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCANNING PIPELINE
// ═══════════════════════════════════════════════════════════════════════════════

// Scan Mode Switching
function switchScanMode(mode) {
  stopCameraScan();
  elements.modeCamera.classList.add("hidden");
  elements.modeUpload.classList.add("hidden");
  elements.modeManual.classList.add("hidden");

  if (mode === "camera") elements.modeCamera.classList.remove("hidden");
  if (mode === "upload") elements.modeUpload.classList.remove("hidden");
  if (mode === "manual") elements.modeManual.classList.remove("hidden");
}

// Camera Scanner
async function startCameraScan() {
  try {
    elements.cameraOverlayStatus.textContent = "Accessing camera...";
    await window.barcodeScanner.startCamera("camera-video", (code) => {
      elements.cameraOverlayStatus.textContent = `Detected Code: ${code}`;
      stopCameraScan();
      executeBarcodeScan(code);
    });
    elements.btnStartCamera.classList.add("hidden");
    elements.btnStopCamera.classList.remove("hidden");
    elements.cameraOverlayStatus.textContent = "Scanning... Point camera at barcode";
  } catch (err) {
    showToast(err.message || "Failed to start camera.", "danger");
    elements.cameraOverlayStatus.textContent = "Camera unavailable";
  }
}

function stopCameraScan() {
  if (window.barcodeScanner) {
    window.barcodeScanner.stopCamera();
  }
  elements.btnStartCamera.classList.remove("hidden");
  elements.btnStopCamera.classList.add("hidden");
}

// Upload Scanner
function handleFileUpload(e) {
  if (e.target.files && e.target.files[0]) {
    processUploadedFile(e.target.files[0]);
  }
}

async function processUploadedFile(file) {
  showLoading("Decoding image barcode & generating AI assessment...");
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", state.language);

  try {
    const resp = await fetch(`${API_BASE}/scan/image`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData,
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Barcode image decoding failed.");
    }

    const data = await resp.json();
    renderAnalysisResults(data);
    addToHistoryLocal(data);
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    hideLoading();
  }
}

// Manual Or Barcode Pipeline
async function executeBarcodeScan(barcode) {
  showLoading(`Analyzing barcode: ${barcode}...`);

  try {
    const resp = await fetch(`${API_BASE}/scan/manual`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        barcode: barcode,
        language: state.language,
        user_profile: state.userProfile,
      }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Scan request failed.");
    }

    const data = await resp.json();
    renderAnalysisResults(data);
    addToHistoryLocal(data);
  } catch (err) {
    showToast(err.message, "danger");
  } finally {
    hideLoading();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// RESULTS DASHBOARD RENDERING
// ═══════════════════════════════════════════════════════════════════════════════

function renderAnalysisResults(scanData) {
  state.scanData = scanData;
  const p = scanData.product;
  const a = scanData.analysis;

  // Show Results Section
  elements.historySection.classList.add("hidden");
  elements.resultsSection.classList.remove("hidden");
  elements.resultsSection.scrollIntoView({ behavior: "smooth" });

  // Product Details
  elements.productName.textContent = p.product_name || "Unknown Product";
  elements.productBrand.innerHTML = `<i class="fa-solid fa-industry"></i> ${p.brand || "Brand Unknown"}`;
  elements.productCategory.innerHTML = `<i class="fa-solid fa-tags"></i> ${p.categories || "Packaged Food"}`;
  elements.barcodeDisplayBadge.textContent = `Barcode: ${p.barcode}`;

  // Image
  if (p.image_url) {
    elements.productImg.src = p.image_url;
  } else {
    elements.productImg.src = "https://placehold.co/150x150/1e293b/fff?text=Food+Item";
  }

  // Nutri-Score & NOVA Badges
  if (p.nutri_score) {
    elements.nutriscoreBadge.textContent = `Nutri-Score: Grade ${p.nutri_score.toUpperCase()}`;
    elements.nutriscoreBadge.className = `badge badge-nutri score-${p.nutri_score.toLowerCase()}`;
  } else {
    elements.nutriscoreBadge.textContent = `Nutri-Score: N/A`;
  }

  if (p.nova_group) {
    elements.novaBadge.textContent = `NOVA Group ${p.nova_group}`;
  } else {
    elements.novaBadge.textContent = `NOVA: Unclassified`;
  }

  // Health Score Radial Gauge Animation
  animateScoreGauge(a.overall_health_score);

  // Verdict & Advice
  elements.verdictTitle.textContent = a.product_summary.verdict || "Health Evaluation";
  elements.adviceBadge.textContent = a.daily_consumption_advice || "Consume in moderation";

  // Tab 1: Health Risks & User Fit
  renderHealthRisksTab(a);

  // Tab 2: Ingredients Breakdown
  renderIngredientsTab(p, a);

  // Tab 3: Harmful & Additives
  renderAdditivesTab(p, a);

  // Tab 4: Nutrition & FSSAI
  renderNutritionTab(p, a);

  // Tab 5: Harmful Health Effects & Organ Toxicity
  renderOrganImpactsTab(p, a);

  // Tab 6: Alternatives & Recommendations
  renderAlternativesTab(a);
}

function renderOrganImpactsTab(product, analysis) {
  if (!elements.organImpactGrid) return;

  const n = product.nutriments || {};
  const sodium_mg = (n.sodium_100g ? n.sodium_100g * 1000 : (n.salt_100g ? (n.salt_100g / 2.5) * 1000 : 0));
  const sugars = n.sugars_100g || 0;
  const sat_fat = n.saturated_fat_100g || 0;
  const nova = product.nova_group || 0;
  const additives = analysis.additive_explanation || [];

  // Overall impact severity
  let maxSeverity = "Moderate Load";
  let maxPillClass = "badge-warning";
  if (sodium_mg > 800 || sugars > 18 || sat_fat > 6 || (analysis.overall_health_score && analysis.overall_health_score < 40)) {
    maxSeverity = "Critical Physiological Risk";
    maxPillClass = "badge-danger";
  } else if (sodium_mg > 400 || sugars > 8 || sat_fat > 3) {
    maxSeverity = "Elevated Toxicity Risk";
    maxPillClass = "badge-warning";
  } else {
    maxSeverity = "Low Adverse Vector";
    maxPillClass = "badge-safe";
  }

  if (elements.impactSeverityPill) {
    elements.impactSeverityPill.textContent = maxSeverity;
    elements.impactSeverityPill.className = `badge badge-lg ${maxPillClass}`;
  }

  // 1. Cardiovascular System (Heart & Arteries)
  const cardioRiskPct = Math.min(95, Math.max(15, Math.round((sodium_mg / 1500) * 100 + (sat_fat / 10) * 40)));
  const cardioLevel = cardioRiskPct > 65 ? "Severe Vascular Strain" : (cardioRiskPct > 35 ? "Moderate Load" : "Low Risk");
  const cardioConsequences = [];
  if (sodium_mg > 600) {
    cardioConsequences.push(`Elevated Sodium (${sodium_mg.toFixed(0)}mg/100g) triggers acute arterial vasoconstriction and systolic BP elevation.`);
  }
  if (sat_fat > 3) {
    cardioConsequences.push(`Saturated fat & palm oil (${sat_fat.toFixed(1)}g) elevates atherogenic ApoB and LDL cholesterol plaque.`);
  }
  if (!cardioConsequences.length) {
    cardioConsequences.push("Low direct vascular strain under moderate portion sizes.");
  }

  // 2. Metabolic & Liver (Glucose & NAFLD)
  const metaRiskPct = Math.min(95, Math.max(15, Math.round((sugars / 25) * 100 + (nova === 4 ? 30 : 0))));
  const metaLevel = metaRiskPct > 65 ? "Severe Glycemic Load" : (metaRiskPct > 35 ? "Moderate Glycemic Surge" : "Low Risk");
  const metaConsequences = [];
  if (sugars > 10) {
    metaConsequences.push(`High simple sugars (${sugars.toFixed(1)}g) stimulate rapid insulin surges followed by reactive hypoglycemia.`);
  }
  if (nova === 4) {
    metaConsequences.push("Ultra-processed refined carbohydrates bypass satiety hormones, accelerating de novo lipogenesis (fatty liver).");
  }
  if (!metaConsequences.length) {
    metaConsequences.push("Moderate carbohydrate and sugar profile within standard metabolic thresholds.");
  }

  // 3. Renal & Excretory (Kidneys)
  const renalRiskPct = Math.min(95, Math.max(15, Math.round((sodium_mg / 1400) * 90 + (additives.length * 8))));
  const renalLevel = renalRiskPct > 60 ? "Heavy Glomerular Burden" : (renalRiskPct > 30 ? "Moderate Filtration Stress" : "Low Risk");
  const renalConsequences = [
    `Glomerular filtration rate (GFR) burdened by sodium excretion load (${sodium_mg.toFixed(0)}mg).`,
    additives.some(a => a.ins_code && (a.ins_code.includes("451") || a.ins_code.includes("500"))) 
      ? "Inorganic phosphate / mineral additives place additional processing demand on renal tubule cells."
      : "Fluid retention and osmotic blood volume expansion."
  ];

  // 4. Gastrointestinal & Gut Microbiome (Gut Lining)
  const gutRiskPct = Math.min(95, Math.max(20, (nova === 4 ? 50 : 20) + (additives.length * 12)));
  const gutLevel = gutRiskPct > 60 ? "Mucosal Barrier Disruption" : "Mild Irritation";
  const gutConsequences = [
    nova === 4 ? "Industrial food emulsifiers & thickeners thin protective colonic mucus lining." : "Standard digestion profile.",
    additives.length ? `Contains ${additives.length} artificial additive(s) that alter the gut microbiome and reduce short-chain fatty acid synthesis.` : "Preserves gut microbial diversity."
  ];

  // 5. Neuro-Cognitive & Energy Homeostasis
  const neuroRiskPct = Math.min(90, Math.max(15, (sugars > 12 ? 65 : (sugars > 5 ? 40 : 20)) + (nova === 4 ? 20 : 0)));
  const neuroLevel = neuroRiskPct > 55 ? "Energy Crash & Cravings" : "Stable";
  const neuroConsequences = [
    sugars > 8 ? "Postprandial glycemic rollercoaster causes lethargy, irritability, and brain fog within 2 hours." : "Stable sustained cellular energy release.",
    "Engineered hyper-palatability triggers dopaminergic craving loops, encouraging overconsumption."
  ];

  const organCardsData = [
    {
      name: "Cardiovascular System",
      subtext: "Heart, Arteries & Blood Pressure",
      icon: "fa-heart-pulse",
      gradient: "linear-gradient(135deg, #f43f5e, #be123c)",
      cardAccent: "linear-gradient(90deg, #f43f5e, #fda4af)",
      level: cardioLevel,
      pct: cardioRiskPct,
      meterColor: cardioRiskPct > 60 ? "linear-gradient(90deg, #f59e0b, #f43f5e)" : "linear-gradient(90deg, #10b981, #06b6d4)",
      consequences: cardioConsequences
    },
    {
      name: "Metabolic & Hepatic System",
      subtext: "Pancreas, Insulin & Liver Fat",
      icon: "fa-cubes-stacked",
      gradient: "linear-gradient(135deg, #f59e0b, #b45309)",
      cardAccent: "linear-gradient(90deg, #f59e0b, #fbbf24)",
      level: metaLevel,
      pct: metaRiskPct,
      meterColor: metaRiskPct > 60 ? "linear-gradient(90deg, #f59e0b, #f43f5e)" : "linear-gradient(90deg, #10b981, #f59e0b)",
      consequences: metaConsequences
    },
    {
      name: "Renal & Excretory System",
      subtext: "Kidney Glomeruli & Fluid Balance",
      icon: "fa-kidney",
      gradient: "linear-gradient(135deg, #a855f7, #6d28d9)",
      cardAccent: "linear-gradient(90deg, #a855f7, #c084fc)",
      level: renalLevel,
      pct: renalRiskPct,
      meterColor: "linear-gradient(90deg, #06b6d4, #a855f7)",
      consequences: renalConsequences
    },
    {
      name: "Gastrointestinal & Gut Microbiome",
      subtext: "Mucosal Integrity & Microbiota",
      icon: "fa-bacteria",
      gradient: "linear-gradient(135deg, #06b6d4, #0e7490)",
      cardAccent: "linear-gradient(90deg, #06b6d4, #38bdf8)",
      level: gutLevel,
      pct: gutRiskPct,
      meterColor: "linear-gradient(90deg, #10b981, #06b6d4)",
      consequences: gutConsequences
    },
    {
      name: "Neuro-Cognitive & Energy",
      subtext: "Brain Fog, Mood & Cravings",
      icon: "fa-brain",
      gradient: "linear-gradient(135deg, #ec4899, #9d174d)",
      cardAccent: "linear-gradient(90deg, #ec4899, #f472b6)",
      level: neuroLevel,
      pct: neuroRiskPct,
      meterColor: "linear-gradient(90deg, #a855f7, #ec4899)",
      consequences: neuroConsequences
    }
  ];

  elements.organImpactGrid.innerHTML = organCardsData.map(c => `
    <div class="organ-card" style="--card-accent-gradient: ${c.cardAccent};">
      <div class="organ-card-top">
        <div class="organ-identity">
          <div class="organ-icon-circle" style="--organ-gradient: ${c.gradient};">
            <i class="fa-solid ${c.icon}"></i>
          </div>
          <div>
            <div class="organ-name">${c.name}</div>
            <div class="organ-subtext">${c.subtext}</div>
          </div>
        </div>
        <span class="badge badge-${c.pct > 60 ? 'danger' : (c.pct > 35 ? 'warning' : 'safe')}">${c.level}</span>
      </div>

      <ul class="organ-consequences">
        ${c.consequences.map(item => `<li>${item}</li>`).join("")}
      </ul>

      <div class="organ-meter-group">
        <div class="organ-meter-labels">
          <span>Physiological Load Index</span>
          <strong>${c.pct}%</strong>
        </div>
        <div class="organ-meter-bar">
          <div class="organ-meter-fill" style="width: ${c.pct}%; --meter-color: ${c.meterColor};"></div>
        </div>
      </div>
    </div>
  `).join("");

  // Populate Acute and Chronic Lists
  if (elements.acuteEffectsList) {
    const acuteItems = [
      sodium_mg > 500 ? `Rapid surge in blood pressure and vascular resistance from ${sodium_mg.toFixed(0)}mg sodium.` : "Mild osmotic fluid shift.",
      sugars > 10 ? `Sharp blood sugar spike followed by insulin surge and fatigue within 90-120 minutes.` : "Moderate carbohydrate absorption rate.",
      nova === 4 ? "Digestive heaviness and delayed gastric emptying from refined emulsified palm oil." : "Standard gastric transit."
    ];
    elements.acuteEffectsList.innerHTML = acuteItems.map(item => `<li>${item}</li>`).join("");
  }

  if (elements.chronicEffectsList) {
    const chronicItems = [
      sodium_mg > 600 ? "Persistent vascular endothelial micro-damage, leading to chronic hypertension and stroke risk." : "Manageable vascular impact under dietary guidelines.",
      sat_fat > 3 ? `Arterial plaque formation and elevated LDL particle count from recurring saturated fat intake.` : "Minimal lipid profile distortion.",
      nova === 4 ? "Chronic low-grade gut mucosal inflammation, microbial dysbiosis, and progressive insulin resistance." : "Preserved metabolic flexibility."
    ];
    elements.chronicEffectsList.innerHTML = chronicItems.map(item => `<li>${item}</li>`).join("");
  }
}

function animateScoreGauge(score) {
  const radius = 50;
  const circumference = 2 * Math.PI * radius; // 314.15
  const offset = circumference - (score / 100) * circumference;

  elements.scoreNumber.textContent = score;

  // Color Coding
  let strokeColor = "#10b981"; // Safe Green
  if (score < 45) strokeColor = "#ef4444"; // Danger Red
  else if (score < 70) strokeColor = "#f59e0b"; // Warning Amber

  elements.gaugeFill.style.stroke = strokeColor;
  elements.gaugeFill.style.strokeDasharray = circumference;
  elements.gaugeFill.style.strokeDashoffset = offset;
}

function renderHealthRisksTab(analysis) {
  const conds = [];
  const hc = state.userProfile.health_conditions || {};
  if (hc.diabetes) conds.push("Diabetes");
  if (hc.hypertension) conds.push("Hypertension");
  if (hc.kidney_disease) conds.push("CKD");
  if (hc.pregnancy) conds.push("Pregnancy");
  if (hc.heart_disease) conds.push("Heart Disease");
  if (hc.celiac_disease) conds.push("Celiac Disease");

  elements.userProfileSummaryBanner.innerHTML = `
    <i class="fa-solid fa-user-doctor"></i> <strong>Evaluated Profile:</strong> Age ${state.userProfile.age || 30} | 
    Conditions: ${conds.length ? conds.join(", ") : "None Specified"} | 
    Allergies: ${(state.userProfile.allergies || []).length ? state.userProfile.allergies.join(", ") : "None"}
  `;

  const risks = analysis.health_risk_assessment || [];
  elements.healthRisksGrid.innerHTML = risks.map(r => `
    <div class="risk-card ${r.risk_level}">
      <div class="risk-header">
        <span class="risk-condition">${r.condition}</span>
        <span class="badge badge-${r.risk_level === 'high' ? 'danger' : (r.risk_level === 'moderate' ? 'warning' : 'safe')}">${r.risk_level} risk</span>
      </div>
      <p class="risk-explanation">${r.explanation}</p>
    </div>
  `).join("");
}

function renderIngredientsTab(product, analysis) {
  elements.rawIngredientsText.textContent = product.ingredients_text || "No detailed raw ingredients declaration available.";

  const items = analysis.ingredient_explanations || [];
  elements.ingredientsListContainer.innerHTML = items.map(ing => `
    <div class="ingredient-item">
      <div>
        <div class="ing-name">${ing.name}</div>
        <div class="ing-purpose">${ing.purpose} — ${ing.notes}</div>
      </div>
      <span class="badge badge-${ing.safety_level === 'high_concern' ? 'danger' : (ing.safety_level === 'moderate_concern' ? 'warning' : 'safe')}">
        ${ing.safety_level.replace('_', ' ')}
      </span>
    </div>
  `).join("");
}

function renderAdditivesTab(product, analysis) {
  const harmful = analysis.harmful_ingredients || [];
  elements.harmfulIngredientsContainer.innerHTML = harmful.length ? harmful.map(h => `
    <div class="risk-card high" style="margin-bottom:0.75rem;">
      <strong>${h.ingredient}</strong>
      <p style="font-size:0.85rem; margin-top:0.3rem;">${h.reason_for_harm}</p>
    </div>
  `).join("") : `<p style="color:var(--status-safe);"><i class="fa-solid fa-circle-check"></i> No severe harmful ingredients flagged.</p>`;

  const additives = analysis.additive_explanation || [];
  elements.additivesContainer.innerHTML = additives.length ? additives.map(ad => `
    <div class="ingredient-item">
      <div>
        <span class="badge badge-mono">${ad.ins_code}</span> <strong>${ad.name}</strong>
        <div class="ing-purpose">${ad.function} — ${ad.concerns}</div>
      </div>
      <span class="badge badge-warning">${ad.safety_status}</span>
    </div>
  `).join("") : `<p style="color:var(--text-muted);">No INS / E-number food additives declared.</p>`;
}

function renderNutritionTab(product, analysis) {
  const n = product.nutriments || {};
  elements.nutritionGrid.innerHTML = `
    <div class="nutriment-card">
      <div class="nutriment-val">${n.energy_kcal_100g || 0}</div>
      <div class="nutriment-lbl">Calories (kcal)</div>
    </div>
    <div class="nutriment-card">
      <div class="nutriment-val">${n.sugars_100g || 0}g</div>
      <div class="nutriment-lbl">Sugars (${analysis.nutrition_summary?.sugar_level || 'level'})</div>
    </div>
    <div class="nutriment-card">
      <div class="nutriment-val">${n.sodium_100g ? (n.sodium_100g * 1000).toFixed(0) : 0}mg</div>
      <div class="nutriment-lbl">Sodium (${analysis.nutrition_summary?.sodium_level || 'level'})</div>
    </div>
    <div class="nutriment-card">
      <div class="nutriment-val">${n.saturated_fat_100g || 0}g</div>
      <div class="nutriment-lbl">Saturated Fat</div>
    </div>
  `;

  elements.fssaiSummaryText.textContent = analysis.fssai_guideline_summary || "FSSAI compliance evaluation completed.";
}

function renderAlternativesTab(analysis) {
  const recs = analysis.personalized_recommendations || [];
  elements.recommendationsList.innerHTML = recs.map(r => `<li>${r}</li>`).join("");

  const alts = analysis.better_alternatives || [];
  elements.alternativesContainer.innerHTML = alts.map(alt => `
    <div class="alt-card">
      <div class="alt-name"><i class="fa-solid fa-leaf"></i> ${alt.name}</div>
      <p style="font-size:0.85rem; color:var(--text-muted); margin:0.3rem 0;">${alt.reason}</p>
      <div>${(alt.healthier_aspects || []).map(a => `<span class="badge badge-safe" style="font-size:0.7rem; margin-right:0.3rem;">${a}</span>`).join("")}</div>
    </div>
  `).join("");
}

// ═══════════════════════════════════════════════════════════════════════════════
// HISTORY MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════

function addToHistoryLocal(scanData) {
  const item = {
    id: scanData.scan_id || Date.now(),
    barcode: scanData.product.barcode,
    product_name: scanData.product.product_name,
    brand: scanData.product.brand,
    product_image_url: scanData.product.image_url,
    overall_health_score: scanData.analysis.overall_health_score,
    scanned_at: scanData.scanned_at,
    scanData: scanData,
  };
  state.history.unshift(item);
  if (!elements.historySection.classList.contains("hidden")) {
    renderHistoryList();
  }
}

async function loadHistoryFromBackend() {
  if (!state.token) return;

  try {
    const res = await fetch(`${API_BASE}/history/?page=1&page_size=25`, {
      headers: getAuthHeaders(),
    });

    if (res.ok) {
      const data = await res.json();
      state.history = data.items.map(s => ({
        id: s.id,
        barcode: s.barcode,
        product_name: s.product_name || "Food Product",
        brand: s.brand || "Brand",
        product_image_url: s.product_image_url,
        overall_health_score: s.overall_health_score,
        scanned_at: s.scanned_at,
      }));
      if (!elements.historySection.classList.contains("hidden")) {
        renderHistoryList();
      }
    }
  } catch (err) {
    console.warn("Could not fetch user scan history:", err);
  }
}

function toggleHistorySection() {
  elements.historySection.classList.toggle("hidden");
  if (!elements.historySection.classList.contains("hidden")) {
    elements.resultsSection.classList.add("hidden");
    renderHistoryList();
    elements.historySection.scrollIntoView({ behavior: "smooth" });
  }
}

function renderHistoryList() {
  if (!state.history.length) {
    elements.historyListContainer.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 2rem 1rem; color: var(--text-muted);">
        <i class="fa-solid fa-clock-rotate-left" style="font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5;"></i>
        <p>No scan history recorded yet. Scan a food barcode to get started.</p>
      </div>
    `;
    return;
  }

  elements.historyListContainer.innerHTML = state.history.map(item => `
    <div class="history-card" onclick="loadPastScan('${item.barcode}')">
      <img src="${item.product_image_url || 'https://placehold.co/50x50/1e293b/fff?text=Item'}" class="history-img" alt="Product">
      <div class="history-card-body">
        <div class="history-product-name">${item.product_name}</div>
        <div style="font-size:0.8rem; color:var(--text-muted);">${item.brand || 'Food'}</div>
      </div>
      <div class="history-card-actions">
        <span class="badge badge-${item.overall_health_score < 45 ? 'danger' : (item.overall_health_score < 70 ? 'warning' : 'safe')}">
          Score ${item.overall_health_score}
        </span>
        <button class="btn-history-del" onclick="deleteHistoryItem('${item.id}', event)" title="Delete scan record">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </div>
    </div>
  `).join("");
}

window.loadPastScan = function(barcode) {
  executeBarcodeScan(barcode);
};

window.deleteHistoryItem = async function(scanId, e) {
  if (e) e.stopPropagation();

  // If user is authenticated, call DELETE on backend
  if (state.token && typeof scanId === "string" && scanId.length > 20) {
    try {
      await fetch(`${API_BASE}/history/${scanId}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });
    } catch (err) {
      console.warn("Failed to delete history item on server:", err);
    }
  }

  state.history = state.history.filter(h => String(h.id) !== String(scanId));
  renderHistoryList();
  showToast("Scan removed from history.", "info");
};

async function clearHistory() {
  if (state.token) {
    try {
      await fetch(`${API_BASE}/history/`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });
    } catch (err) {
      console.warn("Failed to clear server history:", err);
    }
  }

  state.history = [];
  renderHistoryList();
  showToast("History cleared.", "info");
}

// ═══════════════════════════════════════════════════════════════════════════════
// SAMPLES & HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

async function fetchSampleBarcodes() {
  try {
    const resp = await fetch(`${API_BASE}/scan/samples`);
    if (resp.ok) {
      const samples = await resp.json();
      console.log("Sample barcodes loaded:", samples.length);
    }
  } catch (e) {
    console.log("Sample endpoint checked.");
  }
}

function showLoading(msg = "Analyzing product...") {
  elements.loadingText.textContent = msg;
  elements.loadingOverlay.classList.remove("hidden");
}

function hideLoading() {
  elements.loadingOverlay.classList.add("hidden");
}

function showToast(msg, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  let icon = "fa-circle-info";
  if (type === "success") icon = "fa-circle-check";
  if (type === "danger") icon = "fa-circle-exclamation";
  if (type === "warning") icon = "fa-triangle-exclamation";
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${msg}</span>`;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ═══════════════════════════════════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════════════════════

function initEventListeners() {
  // Language Change
  elements.languageSelect.addEventListener("change", (e) => {
    state.language = e.target.value;
    state.userProfile.preferred_language = state.language;
    if (state.scanData) {
      executeBarcodeScan(state.scanData.product.barcode);
    }
  });

  // Auth Dialog Triggers
  elements.btnOpenAuth.addEventListener("click", () => openAuthModal("login"));
  elements.btnCloseAuth.addEventListener("click", closeAuthModal);
  elements.tabBtnLogin.addEventListener("click", () => switchAuthTab("login"));
  elements.tabBtnRegister.addEventListener("click", () => switchAuthTab("register"));
  elements.linkToRegister.addEventListener("click", (e) => { e.preventDefault(); switchAuthTab("register"); });
  elements.linkToLogin.addEventListener("click", (e) => { e.preventDefault(); switchAuthTab("login"); });

  // Auth Form Submits
  elements.loginForm.addEventListener("submit", handleLoginSubmit);
  elements.registerForm.addEventListener("submit", handleRegisterSubmit);

  // User Dropdown in Navbar
  elements.btnUserDropdown.addEventListener("click", (e) => {
    e.stopPropagation();
    elements.userDropdownPopover.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (!elements.userNavMenu.contains(e.target)) {
      elements.userDropdownPopover.classList.add("hidden");
    }
  });

  elements.btnNavProfile.addEventListener("click", () => {
    elements.userDropdownPopover.classList.add("hidden");
    openProfileModal();
  });

  elements.btnNavHistory.addEventListener("click", () => {
    elements.userDropdownPopover.classList.add("hidden");
    toggleHistorySection();
  });

  elements.btnLogout.addEventListener("click", () => {
    elements.userDropdownPopover.classList.add("hidden");
    handleLogout();
  });

  // Password Visibility Toggles
  elements.passwordToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (input) {
        const isPassword = input.type === "password";
        input.type = isPassword ? "text" : "password";
        btn.innerHTML = isPassword ? `<i class="fa-solid fa-eye-slash"></i>` : `<i class="fa-solid fa-eye"></i>`;
      }
    });
  });

  // Profile Modal Toggle
  elements.btnOpenProfile.addEventListener("click", openProfileModal);
  elements.btnCloseProfile.addEventListener("click", closeProfileModal);
  elements.profileForm.addEventListener("submit", handleProfileFormSubmit);

  // History Toggle & Clear
  elements.btnToggleHistory.addEventListener("click", toggleHistorySection);
  elements.btnClearHistory.addEventListener("click", clearHistory);

  // Scan Mode Tabs
  elements.scanTabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      elements.scanTabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const mode = btn.dataset.mode;
      switchScanMode(mode);
    });
  });

  // Camera Controls
  elements.btnStartCamera.addEventListener("click", startCameraScan);
  elements.btnStopCamera.addEventListener("click", stopCameraScan);

  // Upload Controls
  elements.btnBrowseFile.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", handleFileUpload);
  
  elements.dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    elements.dropzone.classList.add("dragover");
  });
  elements.dropzone.addEventListener("dragleave", () => elements.dropzone.classList.remove("dragover"));
  elements.dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    elements.dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processUploadedFile(e.dataTransfer.files[0]);
    }
  });

  // Manual Form
  elements.manualForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const barcode = elements.manualInput.value.trim();
    if (barcode) {
      executeBarcodeScan(barcode);
    }
  });

  // Sample Chips
  elements.sampleChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const code = chip.dataset.barcode;
      executeBarcodeScan(code);
    });
  });

  // Result Tabs Navigation
  elements.resultTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      elements.resultTabs.forEach(t => t.classList.remove("active"));
      elements.tabContents.forEach(c => c.classList.add("hidden"));
      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      document.getElementById(targetId).classList.remove("hidden");
    });
  });
}
