const loaderdiv = document.querySelector("#loader");
const parametersdiv = document.querySelector("#parameters");
const datafolderbutton = document.querySelector("#data-folder");
const runbutton = document.querySelector("#run-package");
const fieldsparent = document.querySelector("#parameter-fields");
const resultdiv = document.querySelector("#result");
const resultContentsDiv = document.querySelector("#result-contents");
const cancelbutton = document.querySelector("#cancel-run-package");
let pathPrefix = "";

function addFileSelectors(files) {
  Array.from(document.querySelectorAll("div[data-parameter=path]")).map(
    (pathinput) => {
      files.forEach((file) => {
        const container = document.createElement("div");
        const input = document.createElement("input");
        input.type = "radio";
        input.name = pathinput.dataset.parameterName;
        input.value = file;
        input.id = `${pathinput.dataset.parameterName}-${file}`;
        container.appendChild(input);
        const label = document.createElement("label");
        label.htmlFor = `${pathinput.dataset.parameterName}-${file}`;
        label.innerHTML = file;
        container.appendChild(label);
        pathinput.appendChild(container);
      });
    },
  );
}

function isFileSystemAvailable() {
  return !!window.showDirectoryPicker;
}

let interruptBuffer = new Uint8Array(new SharedArrayBuffer(1));
const worker = new Worker("/static/python-runtime.js");
worker.onmessage = (evt) => {
  const { msg, value } = evt.data;
  switch (msg) {
    case "error": {
      console.error(value);
      break;
    }
    case "source": {
      loaderdiv.style.display = "none";
      parametersdiv.style.display = "flex";
      if (!isFileSystemAvailable()) {
        fieldsparent.style.display = "flex";
        runbutton.style.display = "block";
      }
      break;
    }
    case "datadir": {
      datafolderbutton.disabled = true;
      fieldsparent.style.display = "flex";
      runbutton.style.display = "block";
      addFileSelectors(value.files);
      pathPrefix = value.prefix;
      break;
    }
    case "run": {
      loaderdiv.style.display = "none";

      // {% if package.interface.output == "output-html" %}
      const range = document.createRange();
      range.selectNode(resultContentsDiv);
      resultContentsDiv.appendChild(range.createContextualFragment(value));
      // {% elif package.interface.output == "output-file" %}
      worker.postMessage({ msg: "read", value });
      // {% endif %}

      resultdiv.style.display = "flex";
      break;
    }
    case "read": {
      const download = document.createElement("a");
      download.setAttribute("class", "uk-button uk-button-primary");
      window.filedata = value.data.buffer;
      window.filename = value.filename;
      download.href = window.URL.createObjectURL(new Blob([value.data]));
      download.download = value.filename;
      download.innerText = `Download ${value.filename}`;
      resultContentsDiv.appendChild(download);
      break;
    }
    case "write": {
      break;
    }
  }
};
worker.postMessage({ msg: "interrupt_buffer", value: interruptBuffer });
worker.postMessage({
  msg: "source",
  value: "/packages/file?package={{application}}",
});

if (!isFileSystemAvailable()) {
  datafolderbutton.style.display = "none";
  Array.from(document.querySelectorAll("div[data-parameter=path]")).map(
    (pathinput) => {
      const input = document.createElement("input");
      input.type = "file";
      input.name = pathinput.dataset.parameterName;
      input.setAttribute("id", pathinput.dataset.parameterName);
      input.addEventListener("change", (chng) => {
        const reader = new FileReader();
        const filename = chng.target.files[0].name;
        reader.onload = async (evt) => {
          let bytes = new Uint8Array(evt.target.result);
          worker.postMessage({
            msg: "write",
            value: { filename, data: bytes },
          });
        };
        reader.readAsArrayBuffer(input.files[0]);
      });
      pathinput.appendChild(input);
    },
  );
} else {
  datafolderbutton.addEventListener("click", async () => {
    const dirHandle = await showDirectoryPicker();
    if ((await dirHandle.queryPermission({ mode: "read" })) !== "granted") {
      if ((await dirHandle.requestPermission({ mode: "read" })) !== "granted") {
        throw Error("Unable to access your data directory");
      }
    }
    worker.postMessage({ msg: "datadir", value: dirHandle });
  });
}

runbutton.addEventListener("click", async () => {
  parametersdiv.style.display = "none";
  document.querySelector("#loader p").innerText = "Running...";
  loaderdiv.style.display = "block";
  cancelbutton.style.display = "block";

  // Clear the interrupt buffer
  interruptBuffer[0] = 0;

  worker.postMessage({
    msg: "run",
    value: {
      entry: "{{package.interface.entrypoint}}",
      parameters: [
        // {% for parameter in package.interface.parameters %}
        // {% if parameter.type == "string" %}
        document.querySelector("#parameter-{{parameter.name}}").value,
        // {% elif parameter.type == "int" or parameter.type == "float" %}
        Number(document.querySelector("#parameter-{{parameter.name}}").value),
        // {% elif parameter.type == "bool" %}
        document.querySelector("#parameter-{{parameter.name}}").checked,
        // {% elif parameter.type == "path" %}
        isFileSystemAvailable()
          ? `${pathPrefix}/${document.querySelector("input[type='radio'][name='parameter-{{parameter.name}}']:checked").value}`
          : document
              .querySelector("#parameter-{{parameter.name}}")
              .value.substring(12),
        // {% endif %}
        // {% endfor %}
      ],
    },
  });
});

cancelbutton.addEventListener("click", () => {
  interruptBuffer[0] = 2;
  cancelbutton.style.display = "none";
  loaderdiv.style.display = "none";
  parametersdiv.style.display = "flex";
});
