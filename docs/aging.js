let pyodide = null;
let allCSVs = []; // Store all parsed CSVs for ZIP packaging
let combinedCSVs;

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
    await pyodide.runPythonAsync(code);

    // Check for batch_dta instead of get_csvs
    const isDefined = pyodide.runPython(`'batch_dta' in globals()`);
    if (!isDefined) {
      document.getElementById("batch-output").textContent = "❌ batch_dta not defined.";
      return;
    }

    document.getElementById("loading").style.display = "none";
    document.getElementById("main-app").style.display = "block";
    document.getElementById("upload").disabled = false;
    document.getElementById("analyzeButton").disabled = false;
  } catch (err) {
    document.getElementById("batch-output").textContent = `❌ Pyodide load failed: ${err}`;
  }
}

loadPyodideAndPackages();

window.compositeDataframes = async () => {
  const files = document.getElementById("upload").files;
  if (!files.length) {
    alert("Please upload at least one file.");
    return;
  }

  const surfaceAreaInput = document.getElementById("surfaceArea");
  const cvCurveInput = document.getElementById("cvCurve");
  const surfaceArea = parseFloat(surfaceAreaInput.value) || 2000;
  const cvCurve = parseFloat(cvCurveInput.value) || 2;

  // Read all file texts into a JS array
  const dtaTexts = [];
  for (const file of files) {
    const text = await file.text();
    dtaTexts.push(text);
  }
  
  // Set Python globals
  pyodide.globals.set("dta_texts", pyodide.toPy(dtaTexts));
  pyodide.globals.set("surface_area", surfaceArea);
  pyodide.globals.set("cv_curve", cvCurve);

  // Reset before populating
  allCSVs = [];

  try {
    const result = await pyodide.runPythonAsync(`
      batch_dta(dta_texts, surface_area=surface_area, cv_curve=cv_curve)
    `);
    
    // Convert Python dict (Map) of CSV strings to JS Map
    combinedCSVs = result.toJs();
    console.log("Combined CSVs (Map):", combinedCSVs);
  
    // Clear old output
    const container = document.getElementById("batch-output");
    container.innerHTML = "";
  
    // Iterate Map entries directly
    for (const [tableName, csvString] of combinedCSVs) {
      if (!csvString.trim()) continue; // Skip empty data
      allCSVs.push({
        folder: "Combined",
        filename: `${tableName}.csv`,
        content: csvString
      });
    }
  
    console.log("allCSVs after push:", allCSVs);
    document.getElementById("downloadAllBtn").disabled = allCSVs.length === 0;
  
  } catch (err) {
    document.getElementById("batch-output").textContent = `❌ Error: ${err}`;
  }
};

window.downloadAlls = async () => {
  if (!allCSVs.length) {
    alert("No files to download. Please run the parser first.");
    return;
  }

  const zip = new JSZip();
  const folder = zip.folder("Combined");
  allCSVs.forEach(({ filename, content }) =>
    folder.file(filename, content)
  );

  const blob = await zip.generateAsync({ type: "blob" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "combined_dataframes.zip";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
