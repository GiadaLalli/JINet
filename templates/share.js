async function deriveKey(passphrase) {
    const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(passphrase).buffer);
    return {
        key: await crypto.subtle.importKey("raw", hash, {
            name: "AES-CBC",
            length: 256,
        }, false, ["encrypt", "decrypt"]),
        iv: hash.slice(0, 16),
    };
}

function encrypt(data, key) {
    return crypto.subtle.encrypt({
        name: "AES-CBC",
        iv: key.iv,
    }, key.key, data);
}

function decrypt(data, key) {
    return crypto.subtle.decrypt({
        name: "AES-256",
        iv: key.iv,
    }, key.key, data);
}

function encodeData(data) {
    const array = new Uint8Array(data);
    const hexCodes = [...array].map(value => value.toString(16).padStart(2, '0'));
    return hexCodes.join('');
}

function decodeData(data) {
    const bytes = Uint8Array.from(data.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)));
    return bytes.buffer;
}

document.getElementById("share-button").addEventListener("click", () => {
    document.querySelector("#share-passphrase-ui").style.display = "block";
    document.getElementById("share-button").style.display = "none";

    document.querySelector("#share-passphrase").addEventListener("input", async (evt) => {
        const passphrase = evt.target.value;
        const key = await deriveKey(passphrase);
        //  {% if package.interface.output == "output-html" %}
        const node = document.querySelector("#result-contents").innerHTML;
        const data = new TextEncoder().encode(node).buffer;
        //  {% elif package.interface.output == "output-file" %}
        const data = window.filedata;
        // {% endif %}
        document.querySelector("#output-data").value = encodeData(await encrypt(data, deriveKey(passphrase)));
    })
});