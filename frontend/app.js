document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("researchButton");
    const topicInput = document.getElementById("topic");
    const status = document.getElementById("status");
    const progressSection = document.getElementById("progressSection");
    const resultSection = document.getElementById("resultSection");
    const reportContent = document.getElementById("reportContent");
    const errorBox = document.getElementById("error");
    const characterCount = document.getElementById("characterCount");
    const activityContainer = document.getElementById("activity");

    // Input character counter
    topicInput.addEventListener("input", () => {
        const length = topicInput.value.length;
        characterCount.textContent = `${length} characters`;
    });

    // Start Button Listener
    button.addEventListener("click", async () => {
        const topic = topicInput.value.trim();

        if (!topic) {
            errorBox.textContent = "Please enter a research topic.";
            errorBox.classList.remove("hidden");
            return;
        }

        errorBox.classList.add("hidden");
        resultSection.classList.add("hidden");
        progressSection.classList.remove("hidden");

        button.disabled = true;
        button.textContent = "Researching...";
        status.textContent = "Your research agent is working...";

        try {
            await startResearch(topic);
        } catch (error) {
            errorBox.textContent = error.message;
            errorBox.classList.remove("hidden");
        } finally {
            button.disabled = false;
            button.innerHTML = "<span>✦</span> Start Research";
        }
    });

    async function startResearch(topic) {
        activityContainer.innerHTML = "";
        reportContent.innerHTML = "";
        status.textContent = "Starting research...";

        const response = await fetch(`/research?topic=${encodeURIComponent(topic)}`);

        if (!response.ok) {
            throw new Error("Unable to start research execution.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split("\n\n");
            buffer = events.pop();

            for (const event of events) {
                if (!event.startsWith("data: ")) continue;

                try {
                    const json = event.substring(6);
                    const data = JSON.parse(json);
                    handleResearchEvent(data);
                } catch (e) {
                    console.error("Failed to parse event data:", e);
                }
            }
        }
    }

    function handleResearchEvent(event) {
        if (event.type === "plan") {
            status.textContent = "Research plan created.";
            addActivity("✓", "Research plan created");
            return;
        }

        if (event.type === "step") {
            addActivity("●", event.message);
            return;
        }

        if (event.type === "tool") {
            addActivity("●", event.message);
            status.textContent = event.message;
            return;
        }

        if (event.type === "tool_complete") {
            addActivity("✓", event.message);
            return;
        }

        if (event.type === "verification") {
            addActivity("✓", event.message);
            return;
        }

        if (event.type === "complete") {
            progressSection.classList.add("hidden");
            resultSection.classList.remove("hidden");
            renderReport(event.report);
            status.textContent = "Research completed.";
            return;
        }

        if (event.type === "error") {
            errorBox.textContent = event.message;
            errorBox.classList.remove("hidden");
            progressSection.classList.add("hidden");
        }
    }

    function addActivity(icon, message) {
        const item = document.createElement("div");
        item.className = "activity-item";
        item.innerHTML = `
            <span class="activity-icon">${icon}</span>
            <span>${escapeHtml(message)}</span>
        `;
        activityContainer.appendChild(item);
    }

    function renderReport(report) {
        if (!report) return;

        const lines = report.split("\n");
        let html = "";

        for (const line of lines) {
            const text = line.trim();
            if (!text) continue;

            if (text.startsWith("# ")) {
                html += `<h1>${escapeHtml(text.substring(2))}</h1>`;
            } else if (text.startsWith("## ")) {
                html += `<h2>${escapeHtml(text.substring(3))}</h2>`;
            } else if (text.startsWith("### ")) {
                html += `<h3>${escapeHtml(text.substring(4))}</h3>`;
            } else if (text.startsWith("- ")) {
                html += `<div class="report-bullet"><span>•</span><span>${escapeHtml(text.substring(2))}</span></div>`;
            } else {
                html += `<p>${escapeHtml(text)}</p>`;
            }
        }

        reportContent.innerHTML = html;
    }

    function escapeHtml(string) {
        return String(string)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});