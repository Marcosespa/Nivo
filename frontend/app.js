const STORAGE_KEY = "nivo-api-console-state";

const state = {
  baseUrl: "http://127.0.0.1:8001",
  accessToken: "",
  refreshToken: "",
  apiKey: "",
  lastOtp: "",
  lastTxId: "",
  lastBankAccountId: "",
  lastVerificationAmount: "",
  lastPublicKey: "",
  lastSignature: "",
};

const elements = {
  baseUrl: document.querySelector("#base-url"),
  accessToken: document.querySelector("#access-token"),
  refreshToken: document.querySelector("#refresh-token"),
  apiKey: document.querySelector("#api-key"),
  output: document.querySelector("#response-output"),
  requestLog: document.querySelector("#request-log"),
  connectionStatus: document.querySelector("#connection-status"),
  envStatus: document.querySelector("#env-status"),
  stateOtp: document.querySelector("#state-otp"),
  stateTx: document.querySelector("#state-tx"),
  stateBank: document.querySelector("#state-bank"),
  stateMicro: document.querySelector("#state-micro"),
  statePublicKey: document.querySelector("#state-public-key"),
  verifyOtpCode: document.querySelector("#verify-otp-code"),
  paymentOtpCode: document.querySelector("#payment-otp-code"),
  paymentTxId: document.querySelector("#payment-tx-id"),
  paymentDetailId: document.querySelector("#payment-detail-id"),
  withdrawalAccountId: document.querySelector("#withdrawal-account-id"),
  withdrawalInitAccountId: document.querySelector("#withdrawal-init-account-id"),
  withdrawalVerifyAmount: document.querySelector("#withdrawal-verify-amount"),
  cryptoSignature: document.querySelector("#crypto-signature"),
  cryptoPublicKey: document.querySelector("#crypto-public-key"),
};

function loadState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    Object.assign(state, JSON.parse(raw));
  } catch (error) {
    console.warn("No se pudo leer el estado guardado", error);
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function syncInputs() {
  elements.baseUrl.value = state.baseUrl;
  elements.accessToken.value = state.accessToken;
  elements.refreshToken.value = state.refreshToken;
  elements.apiKey.value = state.apiKey;
  elements.verifyOtpCode.value = state.lastOtp;
  elements.paymentOtpCode.value = state.lastOtp;
  elements.paymentTxId.value = state.lastTxId;
  elements.paymentDetailId.value = state.lastTxId;
  elements.withdrawalAccountId.value = state.lastBankAccountId;
  elements.withdrawalInitAccountId.value = state.lastBankAccountId;
  elements.withdrawalVerifyAmount.value = state.lastVerificationAmount;
  elements.cryptoSignature.value = state.lastSignature;
  elements.cryptoPublicKey.value = state.lastPublicKey;
  renderStateSummary();
}

function renderStateSummary() {
  elements.stateOtp.textContent = state.lastOtp || "-";
  elements.stateTx.textContent = state.lastTxId || "-";
  elements.stateBank.textContent = state.lastBankAccountId || "-";
  elements.stateMicro.textContent = state.lastVerificationAmount || "-";
  elements.statePublicKey.textContent = state.lastPublicKey
    ? `${state.lastPublicKey.slice(0, 24)}...`
    : "-";
}

function setOutput(title, payload) {
  const text =
    typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  elements.output.textContent = `${title}\n\n${text}`;
}

function showClientError(message, extra = "") {
  setOutput("Error local", extra ? `${message}\n\n${extra}` : message);
}

function addLog(entry) {
  const item = document.createElement("div");
  item.className = "log-item";
  item.innerHTML = `
    <strong>${entry.method} ${entry.path}</strong>
    <div class="log-meta">${entry.time} · status ${entry.status}</div>
    <div class="log-meta">${entry.summary}</div>
  `;
  elements.requestLog.prepend(item);
}

function readFormObject(form) {
  const data = new FormData(form);
  const result = {};
  for (const [key, value] of data.entries()) {
    if (value === "") continue;
    const field = form.elements.namedItem(key);
    if (field && field.type === "number") {
      result[key] = Number(value);
    } else {
      result[key] = value;
    }
  }
  return result;
}

function withQuery(path, query) {
  const base = new URL(path, normalizeBaseUrl());
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      base.searchParams.set(key, String(value));
    }
  });
  return base.toString();
}

function normalizeBaseUrl() {
  return state.baseUrl.endsWith("/") ? state.baseUrl : `${state.baseUrl}/`;
}

async function apiRequest({
  method,
  path,
  body,
  query,
  auth = false,
  apiKey = false,
}) {
  const url = query ? withQuery(path, query) : new URL(path, normalizeBaseUrl()).toString();
  const headers = {
    Accept: "application/json",
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    if (!state.accessToken) {
      throw new Error("No hay access token guardado");
    }
    headers.Authorization = `Bearer ${state.accessToken}`;
  }

  if (apiKey && state.apiKey) {
    headers["X-Nivo-Key"] = state.apiKey;
  }

  const response = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  const summary =
    typeof payload === "string"
      ? payload.slice(0, 140)
      : JSON.stringify(payload).slice(0, 140);

  addLog({
    method,
    path,
    status: response.status,
    summary,
    time: new Date().toLocaleTimeString(),
  });

  setOutput(`${method} ${path} -> ${response.status}`, payload);

  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`);
    error.payload = payload;
    throw error;
  }

  return payload;
}

function updateStateFromResponse(path, payload) {
  if (!payload || typeof payload !== "object") return;

  if (payload.access_token) {
    state.accessToken = payload.access_token;
  }
  if (payload.refresh_token) {
    state.refreshToken = payload.refresh_token;
  }
  if (payload.dev_otp) {
    state.lastOtp = payload.dev_otp;
  }
  if (payload.tx_id) {
    state.lastTxId = payload.tx_id;
  }
  if (payload.bank_account_id) {
    state.lastBankAccountId = payload.bank_account_id;
  }
  if (payload.verification_amount_cop) {
    state.lastVerificationAmount = String(payload.verification_amount_cop);
  }
  if (payload.signature_hex) {
    state.lastSignature = payload.signature_hex;
  }
  if (payload.public_key_hex) {
    state.lastPublicKey = payload.public_key_hex;
  }

  if (path === "/api/v1/dev/seed") {
    if (payload.sender?.access_token) state.accessToken = payload.sender.access_token;
    if (payload.sender?.refresh_token) state.refreshToken = payload.sender.refresh_token;

    const senderPhone = document.querySelector("#auth-phone");
    const verifyPhone = document.querySelector('#verify-otp-form input[name="phone_number"]');
    const receiverPhone = document.querySelector("#payment-receiver-phone");
    if (senderPhone && payload.sender?.phone_number) senderPhone.value = payload.sender.phone_number;
    if (verifyPhone && payload.sender?.phone_number) verifyPhone.value = payload.sender.phone_number;
    if (receiverPhone && payload.receiver?.phone_number) receiverPhone.value = payload.receiver.phone_number;
  }

  if (path === "/api/v1/auth/logout") {
    state.refreshToken = "";
  }

  saveState();
  syncInputs();
}

async function runRequest(config) {
  try {
    const payload = await apiRequest(config);
    updateStateFromResponse(config.path, payload);
    return payload;
  } catch (error) {
    console.error(error);
    if (error.payload) {
      showClientError(error.message, error.payload);
    } else {
      showClientError(error.message || "Error ejecutando request");
    }
    if (error.payload) {
      updateConnectionStatus(false, "Backend respondio con error");
    }
    return null;
  }
}

function updateConnectionStatus(ok, message) {
  elements.connectionStatus.textContent = ok ? "Backend OK" : "Backend con error";
  elements.connectionStatus.className = `status-pill ${ok ? "ok" : "error"}`;
  elements.envStatus.textContent = message;
}

async function pingBackend() {
  try {
    const payload = await apiRequest({ method: "GET", path: "/health" });
    const env = payload.environment || "desconocido";
    updateConnectionStatus(true, `${env} @ ${state.baseUrl}`);
  } catch (error) {
    updateConnectionStatus(false, `No responde ${state.baseUrl}`);
  }
}

function bindConfigForm() {
  document.querySelector("#config-form").addEventListener("submit", (event) => {
    event.preventDefault();
    state.baseUrl = elements.baseUrl.value.trim() || state.baseUrl;
    state.accessToken = elements.accessToken.value.trim();
    state.refreshToken = elements.refreshToken.value.trim();
    state.apiKey = elements.apiKey.value.trim();
    saveState();
    syncInputs();
    pingBackend();
  });

  document.querySelector("#ping-health").addEventListener("click", pingBackend);
}

function bindUtilityButtons() {
  const mapping = {
    health: { method: "GET", path: "/health" },
    "health-pqc": { method: "GET", path: "/health/pqc" },
    "health-ready": { method: "GET", path: "/health/ready" },
    "health-live": { method: "GET", path: "/health/live" },
    root: { method: "GET", path: "/" },
    me: { method: "GET", path: "/api/v1/users/me", auth: true },
    wallet: { method: "GET", path: "/api/v1/users/me/wallet", auth: true },
    algorithms: { method: "GET", path: "/api/v1/crypto/algorithms", apiKey: true },
    "kyc-initiate": { method: "POST", path: "/api/v1/kyc/initiate", auth: true },
    "kyc-status": { method: "GET", path: "/api/v1/kyc/status", auth: true },
    "withdrawal-accounts": { method: "GET", path: "/api/v1/withdrawal/accounts", auth: true },
  };

  document.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = mapping[button.dataset.action];
      if (!action) return;
      await runRequest(action);
    });
  });

  document.querySelectorAll("[data-fill-phone]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.querySelector(`#${button.dataset.target}`);
      if (target) target.value = button.dataset.fillPhone;
    });
  });

  document.querySelector("#copy-access-token").addEventListener("click", async () => {
    if (!state.accessToken) return;
    await navigator.clipboard.writeText(state.accessToken);
    setOutput("Access token copiado", state.accessToken);
  });

  document.querySelector("#clear-session").addEventListener("click", () => {
    state.accessToken = "";
    state.refreshToken = "";
    state.lastOtp = "";
    state.lastTxId = "";
    state.lastBankAccountId = "";
    state.lastVerificationAmount = "";
    state.lastPublicKey = "";
    state.lastSignature = "";
    saveState();
    syncInputs();
    setOutput("Sesion limpiada", "Se vaciaron tokens y referencias temporales.");
  });

  document.querySelector("#clear-output").addEventListener("click", () => {
    elements.output.textContent = "Aun no hay respuestas.";
  });

  document.querySelector("#clear-log").addEventListener("click", () => {
    elements.requestLog.innerHTML = "";
  });
}

function bindForms() {
  document.querySelector("#seed-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    await runRequest({ method: "POST", path: "/api/v1/dev/seed", body });
  });

  document.querySelector("#seed-delete").addEventListener("click", async () => {
    const body = readFormObject(document.querySelector("#seed-form"));
    await runRequest({ method: "DELETE", path: "/api/v1/dev/seed", body });
  });

  document.querySelector("#request-otp-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    await runRequest({ method: "POST", path: "/api/v1/auth/request-otp", body });
  });

  document.querySelector("#verify-otp-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    if (!body.otp_code && state.lastOtp) body.otp_code = state.lastOtp;
    await runRequest({ method: "POST", path: "/api/v1/auth/verify-otp", body });
  });

  document.querySelector("#refresh-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    if (!body.refresh_token && state.refreshToken) body.refresh_token = state.refreshToken;
    await runRequest({ method: "POST", path: "/api/v1/auth/refresh", body });
  });

  document.querySelector("#logout-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    if (!body.refresh_token && state.refreshToken) body.refresh_token = state.refreshToken;
    await runRequest({ method: "POST", path: "/api/v1/auth/logout", body });
  });

  document.querySelector("#payment-initiate-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    await runRequest({ method: "POST", path: "/api/v1/payments/initiate", body, auth: true });
  });

  document.querySelector("#payment-confirm-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    if (!body.tx_id && state.lastTxId) body.tx_id = state.lastTxId;
    if (!body.otp_code && state.lastOtp) body.otp_code = state.lastOtp;
    await runRequest({ method: "POST", path: "/api/v1/payments/confirm", body, auth: true });
  });

  document.querySelector("#payment-history-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = readFormObject(event.currentTarget);
    await runRequest({ method: "GET", path: "/api/v1/payments/history", query, auth: true });
  });

  document.querySelector("#payment-detail-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const { tx_id } = readFormObject(event.currentTarget);
    const txId = tx_id || state.lastTxId;
    if (!txId) {
      showClientError("No hay tx_id disponible para consultar.");
      return;
    }
    await runRequest({ method: "GET", path: `/api/v1/payments/${txId}`, auth: true });
  });

  document.querySelector("#crypto-sign-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    await runRequest({ method: "POST", path: "/api/v1/crypto/sign", body, apiKey: true });
  });

  document.querySelector("#crypto-verify-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    if (!body.signature_hex && state.lastSignature) body.signature_hex = state.lastSignature;
    if (!body.public_key_hex && state.lastPublicKey) body.public_key_hex = state.lastPublicKey;
    await runRequest({ method: "POST", path: "/api/v1/crypto/verify", body, apiKey: true });
  });

  document.querySelector("#topup-initiate-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    await runRequest({ method: "POST", path: "/api/v1/topup/initiate", body, auth: true });
  });

  document.querySelector("#topup-history-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = readFormObject(event.currentTarget);
    await runRequest({ method: "GET", path: "/api/v1/topup/history", query, auth: true });
  });

  document.querySelector("#withdrawal-account-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    await runRequest({ method: "POST", path: "/api/v1/withdrawal/accounts", body, auth: true });
  });

  document.querySelector("#withdrawal-verify-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    const accountId = body.account_id || state.lastBankAccountId;
    if (!accountId) {
      showClientError("No hay account_id disponible para verificar.");
      return;
    }
    delete body.account_id;
    if (!body.verification_amount_cop && state.lastVerificationAmount) {
      body.verification_amount_cop = Number(state.lastVerificationAmount);
    }
    await runRequest({
      method: "POST",
      path: `/api/v1/withdrawal/accounts/${accountId}/verify`,
      body,
      auth: true,
    });
  });

  document.querySelector("#withdrawal-initiate-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = readFormObject(event.currentTarget);
    if (!body.bank_account_id && state.lastBankAccountId) {
      body.bank_account_id = state.lastBankAccountId;
    }
    await runRequest({
      method: "POST",
      path: "/api/v1/withdrawal/initiate",
      body,
      auth: true,
    });
  });

  document.querySelector("#withdrawal-history-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = readFormObject(event.currentTarget);
    await runRequest({
      method: "GET",
      path: "/api/v1/withdrawal/history",
      query,
      auth: true,
    });
  });
}

function bootstrap() {
  loadState();
  syncInputs();
  bindConfigForm();
  bindUtilityButtons();
  bindForms();
  pingBackend();
}

bootstrap();
