let parameterData = [
  { name: "", type: "string", description: null, default: null },
];

function update() {
  const data = JSON.stringify(parameterData);
  document.getElementById("parameters").value = data;
  console.log(data);
}

function updateName(element, index) {
  const value = element.value;
  if (index < parameterData.length) {
    parameterData[index].name = value;
    update();
  }
}

function updateType(element, index) {
  const value = element.value;

  if (index < parameterData.length) {
    parameterData[index].type = value;
    update();
  }
}

function updateDescription(element, index) {
  const value = element.value;

  if (index < parameterData.length) {
    parameterData[index].description = value;
    update();
  }
}

function updateDefault(element, index) {
  const value = element.value;

  if (index < parameterData.length) {
    parameterData[index].default = value;
    update();
  }
}

function mkTypeInput(index) {
  const select = document.createElement("select");
  select.className = "uk-margin-left";
  select.addEventListener("input", (evt) => updateType(evt.target, index));

  [
    ["String", "string"],
    ["Path", "path"],
    ["Integer", "int"],
    ["Float", "float"],
    ["Boolean", "bool"],
  ].forEach(([name, identifier], i) => {
    const opt = document.createElement("option");
    if (i === 0) {
      opt.selected = true;
    }
    opt.value = identifier;
    opt.innerText = name;
    select.appendChild(opt);
  });
  return select;
}

function add(index) {
  console.log(`add(${index})`);
  const button = document.querySelector(
    `#parameter-fields span:nth-child(${index + 1}) a`,
  );
  button.setAttribute("uk-icon", "minus");
  button.setAttribute("onclick", "remove(this, 0)");

  // Add a new row
  parameterData = parameterData.concat([
    { name: "", type: "string", description: null, default: null },
  ]);
  const container = document.createElement("span");
  container.className = "uk-flex uk-margin-top";
  const name = document.createElement("input");
  name.type = "text";
  name.addEventListener("input", (evt) => updateName(evt.target, index + 1));
  name.placeholder = "Name";
  container.appendChild(name);

  container.appendChild(mkTypeInput(index + 1));
  const desc = document.createElement("input");
  desc.className = "uk-margin-left";
  desc.type = "text";
  desc.addEventListener("input", (evt) =>
    updateDescription(evt.target, index + 1),
  );
  desc.placeholder = "Description";
  container.appendChild(desc);

  const dflt = document.createElement("input");
  dflt.className = "uk-margin-left";
  dflt.type = "text";
  dflt.addEventListener("input", (evt) => updateDefault(evt.target, index + 1));
  dflt.placeholder = "Default";
  container.appendChild(dflt);

  const btn = document.createElement("a");
  btn.className = "uk-icon-button uk-margin-left";
  btn.setAttribute("uk-icon", "plus");
  btn.addEventListener("click", () => add(index + 1));
  container.appendChild(btn);

  document.getElementById("parameter-fields").appendChild(container);
  console.log(parameterData);
}

function remove(index) {
  if (index < parameterData.length) {
    parameterData = parameterData.filter((_, i) => i !== index);
    document.querySelector(
      `#parameter-fields span:nth-child(${index + 1})`,
    ).outerHTML = "";
    update();
  }
}

function scrollToTop() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}

document
  .querySelector("#parameter-name-0")
  .addEventListener("input", (evt) => updateName(evt.target, 0));
document
  .querySelector("#parameter-type-0")
  .addEventListener("input", (evt) => updateType(evt.target, 0));
document
  .querySelector("#parameter-description-0")
  .addEventListener("input", (evt) => updateDescription(evt.target, 0));
document
  .querySelector("#parameter-default-0")
  .addEventListener("input", (evt) => updateDefault(evt.target, 0));
document.querySelector("#add-0").addEventListener("click", (evt) => {
  console.log("Click event on add button");
  add(0);
});
