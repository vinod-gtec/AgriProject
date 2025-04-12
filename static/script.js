document.addEventListener("DOMContentLoaded", function () {
    const languageSelector = document.getElementById("language");
    const elementsToTranslate = document.querySelectorAll(".translate");

    languageSelector.addEventListener("change", async function () {
        const selectedLang = this.value;

        elementsToTranslate.forEach(async (element) => {
            const originalText = element.dataset.originalText || element.innerText;
            element.dataset.originalText = originalText; // Store original text

            const translatedText = await fetchTranslation(originalText, selectedLang);
            element.innerText = translatedText;
        });
    });

    async function fetchTranslation(text, lang) {
        const response = await fetch("http://localhost:3000/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, targetLang: lang }),
        });
        const data = await response.json();
        return data.translatedText || text;
    }
});
