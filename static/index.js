document.querySelectorAll(".faq-question").forEach(button => {
    button.addEventListener("click", () => {
        const faqItem = button.parentNode;
        faqItem.classList.toggle("active");
    });
});
