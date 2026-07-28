"use strict";

const elements = {
  form: document.querySelector("#analysis-form"),
  fileInput: document.querySelector("#cell-image"),
  dropZone: document.querySelector("#drop-zone"),
  fileCard: document.querySelector("#file-card"),
  fileName: document.querySelector("#file-name"),
  fileMeta: document.querySelector("#file-meta"),
  preview: document.querySelector("#preview"),
  removeFile: document.querySelector("#remove-file"),
  analyzeButton: document.querySelector("#analyze-button"),
  cancelButton: document.querySelector("#cancel-button"),
  buttonLabel: document.querySelector(".button-label"),
  formError: document.querySelector("#form-error"),
  scopeConfirmation: document.querySelector("#scope-confirmation"),
  statusDot: document.querySelector("#status-dot"),
  statusText: document.querySelector("#service-status-text"),
  limitsLabel: document.querySelector("#limits-label"),
  fileHelp: document.querySelector("#file-help"),
  emptyResult: document.querySelector("#empty-result"),
  resultContent: document.querySelector("#result-content"),
  predictedClass: document.querySelector("#predicted-class"),
  topScore: document.querySelector("#top-score"),
  scoreList: document.querySelector("#score-list"),
  resultFile: document.querySelector("#result-file"),
  executionTime: document.querySelector("#execution-time"),
  pipelineList: document.querySelector("#pipeline-list"),
};

const state = {
  selectedFile: null,
  previewUrl: null,
  requestController: null,
  ready: false,
  scopeAccepted: false,
  capabilities: {
    accepted_content_types: ["image/jpeg", "image/png", "image/webp"],
    max_upload_size_mb: 10,
  },
};

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function showError(message) {
  elements.formError.textContent = message;
  elements.formError.hidden = false;
}

function clearError() {
  elements.formError.textContent = "";
  elements.formError.hidden = true;
}

function setReadiness(ready, reason = null) {
  state.ready = ready;
  elements.statusDot.className = `status-dot ${ready ? "ready" : "unavailable"}`;

  const messages = {
    model_not_configured: "Модель не настроена",
    model_initialization_failed: "Ошибка загрузки модели",
    model_unavailable: "Модель недоступна",
    service_stopped: "Сервис остановлен",
  };
  elements.statusText.textContent = ready
    ? "Готова к анализу"
    : messages[reason] || "Модель недоступна";
  updateSubmitState();
}

function updateSubmitState() {
  const loading = state.requestController !== null;
  elements.analyzeButton.disabled =
    !state.selectedFile || !state.ready || !state.scopeAccepted || loading;
}

function revokePreview() {
  if (state.previewUrl) {
    URL.revokeObjectURL(state.previewUrl);
    state.previewUrl = null;
  }
}

function resetScopeConfirmation() {
  state.scopeAccepted = false;
  elements.scopeConfirmation.checked = false;
}

function clearFile() {
  revokePreview();
  resetScopeConfirmation();
  state.selectedFile = null;
  elements.fileInput.value = "";
  elements.preview.removeAttribute("src");
  elements.fileCard.hidden = true;
  clearError();
  updateSubmitState();
}

function validateFile(file) {
  if (!state.capabilities.accepted_content_types.includes(file.type)) {
    return "Поддерживаются только JPEG, PNG и WEBP.";
  }

  const maxBytes = state.capabilities.max_upload_size_mb * 1024 * 1024;
  if (file.size === 0) {
    return "Выбранный файл пуст.";
  }
  if (file.size > maxBytes) {
    return `Файл больше допустимых ${state.capabilities.max_upload_size_mb} MB.`;
  }
  return null;
}

function selectFile(file) {
  clearError();
  const validationError = validateFile(file);
  if (validationError) {
    clearFile();
    showError(validationError);
    return;
  }

  revokePreview();
  resetScopeConfirmation();
  state.selectedFile = file;
  state.previewUrl = URL.createObjectURL(file);
  elements.preview.src = state.previewUrl;
  elements.fileName.textContent = file.name;
  elements.fileMeta.textContent = `${file.type} · ${formatBytes(file.size)}`;
  elements.fileCard.hidden = false;
  updateSubmitState();
}

function setLoading(loading) {
  elements.analyzeButton.classList.toggle("loading", loading);
  elements.buttonLabel.textContent = loading ? "Анализируем…" : "Запустить анализ";
  elements.cancelButton.hidden = !loading;
  elements.fileInput.disabled = loading;
  elements.removeFile.disabled = loading;
  elements.dropZone.classList.toggle("disabled", loading);
  elements.dropZone.setAttribute("aria-disabled", String(loading));
  updateSubmitState();
}

function renderScores(probabilities) {
  elements.scoreList.replaceChildren();
  probabilities.forEach((item) => {
    const row = document.createElement("div");
    row.className = "score-row";

    const label = document.createElement("strong");
    label.textContent = item.label;

    const value = document.createElement("span");
    value.textContent = `${(item.confidence * 100).toFixed(2)}%`;

    const progress = document.createElement("progress");
    progress.className = "score-progress";
    progress.max = 1;
    progress.value = Math.max(0, Math.min(1, item.confidence));
    progress.setAttribute("aria-label", `${item.label}: ${value.textContent}`);

    row.append(label, value, progress);
    elements.scoreList.append(row);
  });
}

function renderResult(result) {
  elements.predictedClass.textContent = result.predicted_cell_class;
  elements.topScore.textContent = `${(result.confidence * 100).toFixed(2)}%`;
  elements.resultFile.textContent = result.filename;
  elements.executionTime.textContent = `${result.execution_time_ms.toFixed(2)} ms`;
  renderScores(result.probabilities);
  elements.emptyResult.hidden = true;
  elements.resultContent.hidden = false;
  elements.resultContent.focus?.();
}

function renderPipeline(methodology) {
  const labels = {
    input_image: "Входное изображение",
    image_quality_control: "Контроль качества изображения",
    cell_detection_or_segmentation: "Детекция / сегментация клетки",
    cell_classification: "Классификация клетки",
    slide_level_aggregation: "Агрегация на уровне мазка",
    patient_level_interpretation: "Интерпретация пациента",
    human_review: "Проверка человеком",
    clinical_action: "Клиническое действие",
  };
  const statuses = {
    implemented: "Реализовано",
    partial: "Частично",
    missing: "Отсутствует",
    unvalidated: "Не валидировано",
  };

  elements.pipelineList.replaceChildren();
  methodology.pipeline.forEach((item) => {
    const row = document.createElement("li");
    row.className = `pipeline-stage status-${item.status}`;

    const header = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = labels[item.stage] || item.stage;
    const status = document.createElement("span");
    status.className = "pipeline-status";
    status.textContent = statuses[item.status] || item.status;
    header.append(title, status);

    const evidence = document.createElement("p");
    evidence.textContent = item.evidence;
    row.append(header, evidence);
    elements.pipelineList.append(row);
  });
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.headers || {}),
    },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(body?.detail || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}

async function loadCapabilities() {
  try {
    state.capabilities = await fetchJson("/api/v1/capabilities");
    const types = state.capabilities.accepted_content_types
      .map((type) => type.split("/")[1].toUpperCase())
      .join(" · ");
    elements.limitsLabel.textContent = types;
    elements.fileHelp.textContent =
      `До ${state.capabilities.max_upload_size_mb} MB на файл`;
  } catch {
    elements.fileHelp.textContent = "Не удалось получить ограничения API";
  }
}

async function loadMethodology() {
  try {
    renderPipeline(await fetchJson("/api/v1/methodology"));
  } catch {
    elements.pipelineList.replaceChildren();
    const error = document.createElement("li");
    error.className = "pipeline-placeholder";
    error.textContent = "Не удалось получить описание границ системы.";
    elements.pipelineList.append(error);
  }
}

async function checkReadiness() {
  try {
    const response = await fetch("/api/v1/ready", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    const body = await response.json();
    setReadiness(response.ok && body.model_loaded, body.reason);
  } catch {
    setReadiness(false, "model_unavailable");
  }
}

async function analyze(event) {
  event.preventDefault();
  clearError();

  if (!state.selectedFile) {
    showError("Сначала выберите изображение.");
    return;
  }
  if (!state.ready) {
    showError("Модель сейчас не готова к анализу.");
    return;
  }

  const controller = new AbortController();
  state.requestController = controller;
  setLoading(true);

  const formData = new FormData();
  formData.append("file", state.selectedFile, state.selectedFile.name);

  try {
    const result = await fetchJson("/api/v1/analyze", {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    renderResult(result);
  } catch (error) {
    if (error.name === "AbortError") {
      showError("Запрос отменён.");
    } else if (error.status === 503) {
      showError("Модель недоступна или занята. Повторите позже.");
      await checkReadiness();
    } else {
      showError(error.message || "Не удалось выполнить анализ.");
    }
  } finally {
    state.requestController = null;
    setLoading(false);
  }
}

elements.fileInput.addEventListener("change", () => {
  const [file] = elements.fileInput.files;
  if (file) selectFile(file);
});

["dragenter", "dragover"].forEach((eventName) => {
  elements.dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropZone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  elements.dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropZone.classList.remove("dragging");
  });
});

elements.dropZone.addEventListener("drop", (event) => {
  if (state.requestController !== null) return;
  const [file] = event.dataTransfer.files;
  if (file) selectFile(file);
});

elements.removeFile.addEventListener("click", clearFile);
elements.scopeConfirmation.addEventListener("change", () => {
  state.scopeAccepted = elements.scopeConfirmation.checked;
  updateSubmitState();
});
elements.form.addEventListener("submit", analyze);
elements.cancelButton.addEventListener("click", () => {
  state.requestController?.abort();
});

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) void checkReadiness();
});

window.addEventListener("beforeunload", revokePreview);

void loadCapabilities();
void loadMethodology();
void checkReadiness();
window.setInterval(() => {
  if (!document.hidden && state.requestController === null) {
    void checkReadiness();
  }
}, 15000);
