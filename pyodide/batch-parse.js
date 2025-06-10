let pyodide = null;
let allCSVs = []; // Store all parsed CSVs for ZIP packaging

async function loadPyodideAndPackages() {
  try {
    pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");

    await pyodide.runPythonAsync(`
      import micropip
      await micropip.install("pandas")
    `);

    const response = await fetch("test_parser.py");
    const code = await response.text();
    pyodide.runPython(code);

    const isDefined = pyodide.runPython(`'get_csvs' in globals()`);
    if (!isDefined) {
      document.getElementById("batch-output").textContent = "❌ get_csvs not defined.";
      return;
    }

    document.getElementById("loading").style.display = "none";
    document.getElementById("main-app").style.display = "block";
    document.getElementById("upload").disabled = false;
    document.getElementById("analyzeButton").disabled = false;
    document.getElementById("loading").style.display = "none";
    document.getElementById("main-app").style.display = "block";
  } catch (err) {
    document.getElementById("batch-output").textContent = `❌ Pyodide load failed: ${err}`;
  }
}

loadPyodideAndPackages();

window.runBatchParser = async () => {
  const files = document.getElementById("upload").files;
  if (!files.length) {
    alert("Please upload at least one file.");
    return;
  }

  const container = document.getElementById("batch-output");
  container.innerHTML = "";
  allCSVs = [];

  for (const file of files) {
    const text = await file.text();
    pyodide.globals.set("uploaded_text", text);

    try {
      const result = pyodide.runPython(`get_csvs(uploaded_text)`);
      const csvs = Object.fromEntries(result.toJs().entries());
      console.log("Parsed CSVs:", csvs);

      const fileSection = document.createElement("div");
      fileSection.innerHTML = `<h3>${file.name}</h3>`;

      const baseName = file.name.replace(".DTA", "");

      for (const [tableName, csvString] of Object.entries(csvs)) {
        const fileName = `${baseName}_${tableName}.csv`;
        const blob = new Blob([csvString], { type: "text/csv" });
        const url = URL.createObjectURL(blob);

        // Display individual download link
        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;
        link.textContent = `Download ${tableName}`;
        link.style.display = "block";
        link.style.marginBottom = "0.5rem";
        fileSection.appendChild(link);

        // Save for ZIP download
        allCSVs.push({
          folder: baseName,
          filename: `${tableName}.csv`,
          content: csvString
        });
      }

      container.appendChild(fileSection);

    } catch (err) {
      document.getElementById("batch-output").textContent = `❌ Error: ${err}`;
    }
  }

  // Enable ZIP download button
  document.getElementById("downloadAllBtn").disabled = false;
};

window.downloadAll = async () => {
  if (!allCSVs.length) return;

  const zip = new JSZip();
  allCSVs.forEach(({ folder, filename, content }) => {
    zip.folder(folder).file(filename, content);
  });

  const blob = await zip.generateAsync({ type: "blob" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "parsed_dta_files.zip";
  a.click();
};
