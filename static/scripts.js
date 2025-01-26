document.addEventListener("DOMContentLoaded", () => {
  // Transcription
  const uploadForm = document.getElementById("uploadForm");
  const transcriptionResult = document.getElementById("transcriptionResult");
  const translationResult = document.getElementById("translationResult");
  const summaryResult = document.getElementById("summaryResult");

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("file");
    if (!fileInput.files.length) {
      alert("Please upload a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
      const response = await fetch("/transcribe", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();

        if (Array.isArray(data.transcription)) {
          // Map through the array of objects to extract the 'text' field
          transcriptionResult.textContent = data.transcription
            .map((segment) => segment.text || JSON.stringify(segment)) // Extract 'text', or stringify if no 'text' field
            .join("\n"); // Join each text with a newline
        } else if (typeof data.transcription === "string") {
          transcriptionResult.textContent = data.transcription; // Handle plain string response
        } else {
          transcriptionResult.textContent = "Unexpected transcription format.";
        }
      } else {
        const errorData = await response.json();
        alert(errorData.error || "An error occurred.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred. Please try again.");
    }
  });

  // Translation
  document
    .getElementById("translateBtn")
    .addEventListener("click", async () => {
      const transcript = transcriptionResult.textContent;
      const language = document.getElementById("language").value;

      if (!transcript) {
        alert("No transcription to translate.");
        return;
      }

      try {
        const response = await fetch("/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ transcript, language }),
        });

        if (response.ok) {
          const data = await response.json();
          translationResult.textContent =
            data.translation || "No translation available.";
        } else {
          alert("An error occurred during translation.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      }
    });

  // Summarization
  document
    .getElementById("summarizeBtn")
    .addEventListener("click", async () => {
      const transcript = transcriptionResult.textContent;

      if (!transcript) {
        alert("No transcription to summarize.");
        return;
      }

      try {
        const response = await fetch("/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ transcript }),
        });

        if (response.ok) {
          const data = await response.json();
          summaryResult.textContent = data || "No summary available.";
        } else {
          alert("An error occurred during summarization.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      }
    });

  // Download
  document.getElementById("downloadBtn").addEventListener("click", async () => {
    const transcript = transcriptionResult.textContent;
    const summary = summaryResult.textContent;

    if (!transcript) {
      alert("No content to download.");
      return;
    }

    try {
      const response = await fetch("/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript, summary }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "output.pdf";
        link.click();
      } else {
        alert("An error occurred during download.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred. Please try again.");
    }
  });
});
