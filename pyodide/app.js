let pyodide = null;

async function loadPyodideAndPackages() {
  try {
    // Load Pyodide
    pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");

    // Install pandas
    await pyodide.runPythonAsync(`
      import micropip
      await micropip.install("pandas")
    `);

    // Load your Python script
    const response = await fetch("test_parser.py");
    const code = await response.text();
    pyodide.runPython(code);

    // Confirm function is defined
    const isDefined = pyodide.runPython(`'analyze_file' in globals()`);
    if (!isDefined) {
      document.getElementById("output").textContent = "❌ analyze_file not defined.";
      return;
    }

    // All good — show main UI
    document.getElementById("loading").style.display = "none";
    document.getElementById("main-app").style.display = "block";
    document.getElementById("loading").style.display = "none";
    document.getElementById("main-app").style.display = "block";
    document.getElementById("upload").disabled = false;
    document.getElementById("analyzeButton").disabled = false;
    document.getElementById("loading").style.display = "none";
    document.getElementById("main-app").style.display = "block";
  } catch (err) {
    document.getElementById("output").textContent = `❌ Pyodide load failed: ${err}`;
  }
}

loadPyodideAndPackages();

window.runAnalysis = async () => {
    const file = document.getElementById("upload").files[0];
    if (!file) {
      alert("Please upload a file.");
      return;
    }
  
    const text = await file.text();
    pyodide.globals.set("uploaded_text", text);
  
    try {
      const result = pyodide.runPython(`
  analyze_file(uploaded_text)
      `);
  
      const tabsContainer = document.getElementById("tabs-container");
      const tableDisplay = document.getElementById("table-display");
      tabsContainer.innerHTML = '';
      tableDisplay.innerHTML = '';
  
      // Convert Python dict (Proxy) to real JS object
      const tables = Object.fromEntries(result.toJs({ dict_converter: Object }));
  
      Object.keys(tables).forEach((name, index) => {
        const tab = document.createElement("div");
        tab.className = "tab";
        tab.textContent = name;
        tab.onclick = () => {
          // Remove active from all tabs
          document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
          tab.classList.add("active");
  
          // Set table content
          tableDisplay.innerHTML = `<div class="table-content">${tables[name]}</div>`;
        };
  
        // Auto-select first tab
        if (index === 0) {
          tab.classList.add("active");
          tableDisplay.innerHTML = `<div class="table-content">${tables[name]}</div>`;
        }
  
        tabsContainer.appendChild(tab);
      });
  
    } catch (err) {
      document.getElementById("table-display").textContent = `❌ Error: ${err}`;
    }
  };
  