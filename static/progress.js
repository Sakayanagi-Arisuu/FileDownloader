async function sendCommand(cmd) {
  const url = document.getElementById("url").value;
  await fetch(`/${cmd}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

setInterval(async () => {
  const res = await fetch("/progress");
  const data = await res.json();
  const bar = document.getElementById("progress-bar");
  bar.style.width = data.progress + "%";
  bar.textContent = data.progress + "%";
}, 1000);
