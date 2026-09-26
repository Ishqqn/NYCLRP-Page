function copyServerCode() {
    const code = document.getElementById("serverCode");
    if (!code) return;
    navigator.clipboard.writeText(code.innerText).then(() => {
        alert("Server code copied!");
    });
}
