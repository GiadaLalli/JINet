async function deriveKey(passphrase) {
  const hash = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(passphrase).buffer,
  );
  return {
    key: await crypto.subtle.importKey(
      "raw",
      hash,
      {
        name: "AES-CBC",
        length: 256,
      },
      false,
      ["encrypt", "decrypt"],
    ),
    iv: hash.slice(0, 16),
  };
}

function encrypt(data, key) {
  return crypto.subtle.encrypt(
    {
      name: "AES-CBC",
      iv: key.iv,
    },
    key.key,
    data,
  );
}

function decrypt(data, key) {
  return crypto.subtle.decrypt(
    {
      name: "AES-CBC",
      iv: key.iv,
    },
    key.key,
    data,
  );
}

function encodeData(data) {
  const array = new Uint8Array(data);
  const hexCodes = [...array].map((value) =>
    value.toString(16).padStart(2, "0"),
  );
  return hexCodes.join("");
}

function decodeData(data) {
  const bytes = Uint8Array.from(
    data.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)),
  );
  return bytes.buffer;
}

// {% if package is defined %}
document.getElementById("share-button").addEventListener("click", () => {
  document.querySelector("#share-passphrase-ui").style.display = "block";
  document.getElementById("share-button").style.display = "none";
});

document
  .querySelector("#share-passphrase")
  .addEventListener("input", async (evt) => {
    const passphrase = evt.target.value;
    const key = await deriveKey(passphrase);
    //  {% if package.interface.output == "output-html" %}
    const node = document.querySelector("#result-contents").innerHTML;
    const data = new TextEncoder().encode(node).buffer;
    console.log("Encrypting");
    console.log(data);
    console.log("============================");
    //  {% elif package.interface.output == "output-file" %}
    const data = window.filedata;
    document.querySelector("#filename").value = window.filename;
    // {% endif %}
    document.querySelector("#output-data").value = encodeData(
      await encrypt(data, key),
    );
    document.querySelector("#checksum").value = encodeData(
      await crypto.subtle.digest("SHA-256", data),
    );
  });
// {% else %}
document.querySelector("#view-results").addEventListener("click", async () => {
  const passphrase = document.querySelector("#share-passphrase").value;
  const data = decodeData(document.querySelector("#data").value);
  const checksum = document.querySelector("#checksum").value;
  const output = document.querySelector("#output").value;

  const key = await deriveKey(passphrase);
  const result = await decrypt(data, key);

  if (encodeData(await crypto.subtle.digest("SHA-256", result)) === checksum) {
    document.querySelector("#verified").style.display = "flex";
  } else {
    document.querySelector("#not-verified").style.display = "flex";
  }

  if (output === "output-html") {
    const range = document.createRange();
    document
      .querySelector("#results-ui")
      .appendChild(
        range.createContextualFragment(new TextDecoder().decode(result)),
      );
  } else if (output === "output-file") {
    const filename = document.querySelector("#filename").value;
    const download = document.createElement("a");
    download.setAttribute("class", "uk-button uk-button-primary");
    download.href = window.URL.createObjectURL(new Blob([result]));
    download.download = filename;
    download.innerText = `Download ${filename}`;
    document.querySelector("#results-ui").appendChild(download);
  }

  document.querySelector("#passphrase-ui").style.display = "none";
});
// {% endif %}
