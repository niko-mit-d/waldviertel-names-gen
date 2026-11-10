// Waldviertel Imaginary Village Name Generator
document.addEventListener("DOMContentLoaded", () => {
  const data = window.WALDVIERTEL_DATA;

  if (!data || !data.startWords || !data.endWords) {
    console.error("Waldviertel data not loaded.");
    return;
  }

  const realNamesSet = new Set(data.uniqueRealNames.map((n) => n.toLowerCase()));

  // DOM Elements
  const villageNameEl = document.getElementById("village-name");
  const imaginaryBadgeEl = document.getElementById("imaginary-badge");
  const generateBtn = document.getElementById("generate-btn");
  const copyBtn = document.getElementById("copy-btn");
  const copyFeedback = document.getElementById("copy-feedback");

  const startWordEl = document.getElementById("start-word");
  const startFreqEl = document.getElementById("start-freq");
  const startOriginsEl = document.getElementById("start-origins");

  const endWordEl = document.getElementById("end-word");
  const endFreqEl = document.getElementById("end-freq");
  const endOriginsEl = document.getElementById("end-origins");

  const startSelect = document.getElementById("select-start");
  const endSelect = document.getElementById("select-end");
  const enforceFictionalToggle = document.getElementById("toggle-fictional");
  const historyListEl = document.getElementById("history-list");
  const batchBtn = document.getElementById("batch-btn");
  const batchContainer = document.getElementById("batch-container");
  const batchListEl = document.getElementById("batch-list");

  const history = [];

  // Populate Select Dropdowns
  data.startWords.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item.word;
    opt.textContent = `${item.word} (${item.count}x)`;
    startSelect.appendChild(opt);
  });

  data.endWords.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item.word;
    opt.textContent = `${item.word} (${item.count}x)`;
    endSelect.appendChild(opt);
  });

  function formatCompound(start, end) {
    if (start.endsWith("-")) {
      return `${start}${end.charAt(0).toUpperCase()}${end.slice(1)}`;
    }
    // Clean start and end
    const s = start.charAt(0).toUpperCase() + start.slice(1);
    const e = end.toLowerCase();
    return `${s}${e}`;
  }

  function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function generateName() {
    const enforceFictional = enforceFictionalToggle.checked;
    const lockedStart = startSelect.value;
    const lockedEnd = endSelect.value;

    let attempts = 0;
    let chosenStartObj = null;
    let chosenEndObj = null;
    let compound = "";
    let isReal = false;

    while (attempts < 150) {
      attempts++;
      chosenStartObj = lockedStart
        ? data.startWords.find((w) => w.word === lockedStart)
        : getRandomElement(data.startWords);

      chosenEndObj = lockedEnd
        ? data.endWords.find((w) => w.word === lockedEnd)
        : getRandomElement(data.endWords);

      compound = formatCompound(chosenStartObj.word, chosenEndObj.word);
      isReal = realNamesSet.has(compound.toLowerCase());

      if (!enforceFictional || !isReal) {
        break;
      }
    }

    renderVillage(compound, chosenStartObj, chosenEndObj, isReal);
  }

  function renderVillage(compound, startObj, endObj, isReal) {
    villageNameEl.classList.add("updating");

    setTimeout(() => {
      villageNameEl.textContent = compound;
      villageNameEl.classList.remove("updating");

      if (isReal) {
        imaginaryBadgeEl.className = "imaginary-badge real";
        imaginaryBadgeEl.innerHTML = "⚠️ Reale Ortschaft (existiert im Waldviertel)";
      } else {
        imaginaryBadgeEl.className = "imaginary-badge";
        imaginaryBadgeEl.innerHTML = "✨ 100% Frei erfunden (Waldviertler Klang)";
      }

      // Start word details
      startWordEl.textContent = startObj.word;
      startFreqEl.textContent = `Kommt ${startObj.count}× als Anfangswort vor`;
      renderOrigins(startOriginsEl, startObj.origins);

      // End word details
      endWordEl.textContent = endObj.word;
      endFreqEl.textContent = `Kommt ${endObj.count}× als Endwort vor`;
      renderOrigins(endOriginsEl, endObj.origins);

      addToHistory(compound);
    }, 120);
  }

  function renderOrigins(container, origins) {
    container.innerHTML = "";
    const displayOrigins = origins.slice(0, 8);
    displayOrigins.forEach((orig) => {
      const tag = document.createElement("span");
      tag.className = "origin-tag";
      tag.textContent = orig;
      container.appendChild(tag);
    });
    if (origins.length > 8) {
      const moreTag = document.createElement("span");
      moreTag.className = "origin-tag";
      moreTag.style.opacity = "0.75";
      moreTag.textContent = `+${origins.length - 8} weitere`;
      container.appendChild(moreTag);
    }
  }

  function addToHistory(name) {
    if (history.includes(name)) return;
    history.unshift(name);
    if (history.length > 10) history.pop();

    historyListEl.innerHTML = "";
    history.forEach((histName) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "history-item";
      item.textContent = histName;
      item.title = "Diesen Namen erneut ansehen";
      item.addEventListener("click", () => {
        // Find matching components if available
        villageNameEl.textContent = histName;
      });
      historyListEl.appendChild(item);
    });
  }

  function copyCurrentName() {
    const text = villageNameEl.textContent.trim();
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
      copyFeedback.style.display = "inline";
      setTimeout(() => {
        copyFeedback.style.display = "none";
      }, 1800);
    }).catch(() => {
      // Fallback
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      copyFeedback.style.display = "inline";
      setTimeout(() => {
        copyFeedback.style.display = "none";
      }, 1800);
    });
  }

  function generateBatch() {
    batchContainer.style.display = "block";
    batchListEl.innerHTML = "";

    const enforceFictional = enforceFictionalToggle.checked;
    const batchNames = new Set();
    let attempts = 0;

    while (batchNames.size < 6 && attempts < 100) {
      attempts++;
      const s = getRandomElement(data.startWords);
      const e = getRandomElement(data.endWords);
      const comp = formatCompound(s.word, e.word);
      const isReal = realNamesSet.has(comp.toLowerCase());
      if (!enforceFictional || !isReal) {
        batchNames.add(comp);
      }
    }

    batchNames.forEach((n) => {
      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = "history-item";
      pill.style.fontSize = "1rem";
      pill.style.padding = "0.5rem 1rem";
      pill.textContent = n;
      pill.addEventListener("click", () => {
        villageNameEl.textContent = n;
      });
      batchListEl.appendChild(pill);
    });
  }

  // Event Listeners
  generateBtn.addEventListener("click", generateName);
  copyBtn.addEventListener("click", copyCurrentName);
  batchBtn.addEventListener("click", generateBatch);

  startSelect.addEventListener("change", generateName);
  endSelect.addEventListener("change", generateName);

  // Keyboard shortcut: Spacebar or Enter
  window.addEventListener("keydown", (e) => {
    // Only trigger if user is not focusing a form input/select
    if (e.target.tagName !== "SELECT" && e.target.tagName !== "INPUT") {
      if (e.code === "Space") {
        e.preventDefault();
        generateName();
      }
    }
  });

  // Initial generation on load
  generateName();
});
