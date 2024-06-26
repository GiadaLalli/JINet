// This is a worker script

importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.js");

async function initRuntime() {
  self.pyodide = await loadPyodide();
  await self.pyodide.loadPackage([
    "micropip",
    "numpy",
    "pandas",
    "scikit-learn",
    "statsmodels",
  ]);

  await pyodide.runPythonAsync(`
import micropip
await micropip.install('plotly')`);
}

let runtimeReady = initRuntime();

self.dirListing = (path) => {
  let _this = self;
  return self.pyodide.FS.readdir(path).flatMap((name) => {
    if (name.charAt(0) === "." || name === "..") {
      return [];
    }
    const newpath = `${path}/${name}`;
    const stat = _this.pyodide.FS.lstat(newpath);
    if (_this.pyodide.FS.isFile(stat.mode)) {
      return [newpath];
    } else if (_this.pyodide.FS.isDir(stat.mode)) {
      return _this.dirListing(newpath);
    } else {
      return [];
    }
  });
};

self.onmessage = async (event) => {
  await runtimeReady;
  let _this = self;

  const { msg, value } = event.data;

  switch (msg) {
    case "interrupt_buffer": {
      self.pyodide.setInterruptBuffer(value);
      break;
    }
    case "datadir": {
      self.datapath = `${self.pyodide.FS.cwd()}/data`;
      self.datadir = await self.pyodide.mountNativeFS(self.datapath, value);
      self.postMessage({
        msg: "datadir",
        value: {
          prefix: self.datapath,
          files: self.dirListing(self.datapath).map((name) => {
            return name.substring(self.datapath.length + 1);
          }),
        },
      });
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
        await self.pyodide.loadPackagesFromImports(
          self.pyodide.FS.readFile("script.py", { encoding: "utf8" }),
        );
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
        const result = await pkg[entry](...parameters);
        self.postMessage({ msg: "run", value: result });
      } catch (error) {
        self.postMessage({ msg: "error", value: error.message });
      }
      break;
    }
    case "read": {
      self.postMessage({
        msg: "read",
        value: {
          filename: value,
          data: self.pyodide.FS.readFile(value),
        },
      });
      break;
    }
    case "write": {
      const { filename, data } = value;
      self.pyodide.FS.writeFile(filename, data);
      self.postMessage({
        msg: "write",
        value: filename,
      });
      break;
    }
  }
};
