const loaderdiv = document.querySelector("#loader");
const parametersdiv = document.querySelector("#parameters");
const datafolderbutton = document.querySelector("#data-folder");
const runbutton = document.querySelector("#run-package");
const fieldsparent = document.querySelector("#parameter-fields");
const cancelbutton = document.querySelector("#cancel-run-package");
const resultdiv = document.querySelector("#result");
const resultContentsDiv = document.querySelector("#result-contents");

import("https://webr.r-wasm.org/latest/webr.mjs").then(async ({ WebR }) => {
  const webr = new WebR();
  await webr.init();

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
          await webr.FS.writeFile(filename, bytes);
        };
        reader.readAsArrayBuffer(input.files[0]);
      });
      pathinput.appendChild(input);
    },
  );

  runbutton.addEventListener("click", async () => {
    parametersdiv.style.display = "none";
    document.querySelector("#loader p").innerText = "Running...";
    loaderdiv.style.display = "block";
    cancelbutton.style.display = "block";
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;

    // prettier-ignore
    const parameters = [
//    {% for parameter in package.interface.parameters %}
//    {% if parameter.type in ["float", "int"] %}
      document.querySelector("#parameter-{{parameter.name}}").value,
//    {% elif parameter.type == "string" %}
      `"${document.querySelector('#parameter-{{parameter.name}}').value}"`,
//    {% elif parameter.type == "path" %}
      `"${document.querySelector('#parameter-{{parameter.name}}').value.substring(12)}"`,
//    {% endif %}
//    {% endfor %}
    ].join(',');

    let result = await webr.evalR(
      `{{package.interface.entrypoint}}(${parameters})`,
      {
        withAutoprint: true,
      },
    );
    const value = (await result.toJs()).values;

    loaderdiv.style.display = "none";
    //  {% if package.interface.output == "output-html" %}
    const range = document.createRange();
    range.selectNode(resultContentsDiv);
    resultContentsDiv.appendChild(range.createContextualFragment(value));
    //  {% elif package.interface.output == "output-file" %}
    const download = document.createElement("a");
    download.setAttribute("class", "uk-button uk-button-primary");
    console.log(value);
    const outdata = await webr.FS.readFile(...value);
    console.log(typeof outdata);
    console.log(outdata);
    window.filedata = outdata.buffer;
    download.href = window.URL.createObjectURL(new Blob([outdata]));
    download.download = value[0];
    download.innerText = `Download ${value[0]}`;
    resultContentsDiv.appendChild(download);
    //  {% endif %}

    resultdiv.style.display = "flex";
  });

  cancelbutton.addEventListener("click", async () => {
    webr.interrupt();
    cancelbutton.style.display = "none";
    loaderdiv.style.display = "none";
    parametersdiv.style.display = "flex";
  });

  let source = await fetch("/packages/file?package={{application}}");
  await webr.evalR(await source.text());
  loaderdiv.style.display = "none";
  parametersdiv.style.display = "flex";
  datafolderbutton.style.display = "none";
  fieldsparent.style.display = "flex";
  runbutton.style.display = "block";
});
