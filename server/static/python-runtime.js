// This is a worker script

importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

async function initRuntime() {
  self.pyodide = await loadPyodide();
  await self.pyodide.loadPackage([
    "micropip",
    "numpy",
    "pandas",
    "scikit-learn",
  ]);
}

let runtimeReady = initRuntime();

self.onmessage = async (event) => {
  await runtimeReady;
  let _this = self;

  const { msg, value } = event.data;

  switch (msg) {
    case "datadir": {
      self.datadir = await self.pyodide.mountNativeFS(
        `${self.pyodide.FS.cwd()}/data`,
        value,
      );
      self.postMessage({ msg: "datadir", value: "ready" });
      break;
    }
    case "source": {
      try {
        if (typeof value === "string" || value instanceof String) {
          const response = await fetch(value);
          const script = await response.text();
          self.pyodide.FS.writeFile("script.py", script, { encoding: "utf8" });
          self.postMessage({ msg: "source", value: "ready" });
        } else if (value instanceof File) {
          const reader = new FileReader();
          reader.onload = (evt) => {
            pyodide.FS.writeFile("script.py", evt.target.result, {
              encoding: "utf8",
            });
            _this.postMessage({ msg: "source", value: "ready" });
          };
          reader.readAsText(value);
        }
      } catch (error) {
        self.postMessage({
          msg: "error",
          value: error.message || "Failed to fetch package.",
        });
      }
      break;
    }
    case "run": {
      const { entry, parameters } = value;
      try {
        const pkg = self.pyodide.pyimport("script");
        const result = pkg[entry](...parameters);
      } catch (error) {
        self.postMessage({ msg: "error", value: error.message });
      }
      self.postMessage(result);
      break;
    }
    case "read": {
      self.postMessage(self.pyodide.FS.readFile(value));
      break;
    }
  }
};
