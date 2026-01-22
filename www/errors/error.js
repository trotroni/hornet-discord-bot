function goHome() {
    // Ajuste si ton dashboard n’est pas à la racine
    window.location.href = "/dashboard";
}

// Petit bonus : log console pour debug
console.warn(
    "Erreur HTTP détectée",
    {
        code: document.querySelector("h1")?.innerText || "unknown",
        path: window.location.pathname
    }
);
