const loaderdiv = document.querySelector("#loader");
const parametersdiv = document.querySelector("#parameters");
const datafolderbutton = document.querySelector("#data-folder");
const runbutton = document.querySelector("#run-package");
const fieldsparent = document.querySelector("#parameter-fields");
const resultdiv = document.querySelector("#result");
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
      range.selectNode(resultdiv);
      resultdiv.appendChild(range.createContextualFragment(value));
      // {% elif package.interface.output == "output-file" %}
      worker.postMessage({ msg: "read", value });
      // {% endif %}

      resultdiv.style.display = "flex";
      break;
    }
    case "read": {
      const download = document.createElement("a");
      download.setAttribute("class", "uk-button uk-button-primary");
      download.href = window.URL.createObjectURL(value.data);
      download.download = value.filename;
      download.innerText = `Download ${value.filename}`;
      resultdiv.appendChild(download);
      break;
    }
  }
};
worker.postMessage({ msg: "interrupt_buffer", value: interruptBuffer });
worker.postMessage({
  msg: "source",
  value: "/packages/file?package={{application}}",
});

datafolderbutton.addEventListener("click", async () => {
  const dirHandle = await showDirectoryPicker();
  if ((await dirHandle.queryPermission({ mode: "read" })) !== "granted") {
    if ((await dirHandle.requestPermission({ mode: "read" })) !== "granted") {
      throw Error("Unable to access your data directory");
    }
  }
  worker.postMessage({ msg: "datadir", value: dirHandle });
});

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
        `${pathPrefix}/${document.querySelector("input[type='radio'][name='parameter-{{parameter.name}}']:checked").value}`,
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
