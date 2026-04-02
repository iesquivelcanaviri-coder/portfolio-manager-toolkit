document.addEventListener("DOMContentLoaded", () => {
    console.log("JS loaded successfully");

    // Highlight active navigation link
    const links = document.querySelectorAll("nav a");
    links.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add("active");
        }
    });
});
